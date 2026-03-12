import json
import os
import re
import hashlib
import types
from typing import Any, Dict, List, Optional
import uuid

import google.generativeai as genai
from google.adk.tools import ToolContext

try:
    import chromadb
except ImportError:
    chromadb = None


_RESOLVED_EMBEDDING_MODEL: Optional[str] = None
_DISCOVERED_EMBEDDING_MODELS: Optional[List[str]] = None
_SUPPORTED_DOC_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".log", ".pdf"}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sanitize_collection_name(raw_name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_name)
    cleaned = cleaned[:48] if len(cleaned) > 48 else cleaned
    digest = hashlib.sha1(raw_name.encode("utf-8")).hexdigest()[:12]
    return f"rag_{cleaned}_{digest}"


def _get_vector_db_dir() -> str:
    return os.environ.get(
        "RAG_VECTOR_DB_DIR",
        os.path.join(os.getcwd(), ".rag_vector_db"),
    )


def _get_module_reference_doc_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "reference_docs"))


def _get_project_root_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _expand_path_candidates(raw_path: str) -> List[str]:
    if not raw_path:
        return []

    if os.path.isabs(raw_path):
        return [os.path.abspath(raw_path)]

    project_root = _get_project_root_dir()
    cwd = os.getcwd()
    return [
        os.path.abspath(os.path.join(cwd, raw_path)),
        os.path.abspath(os.path.join(project_root, raw_path)),
        os.path.abspath(raw_path),
    ]


def _get_reference_doc_path_from_env() -> Optional[str]:
    raw_value = os.environ.get("RESEARCH_REFERENCE_DOC_PATH")
    if not raw_value:
        return None
    for candidate in _expand_path_candidates(raw_value):
        if os.path.exists(candidate):
            return candidate
    return None


def _get_reference_doc_dir_candidates(session_id: Optional[str] = None) -> List[str]:
    env_dir = os.environ.get("RESEARCH_REFERENCE_DOC_DIR")
    cwd = os.getcwd()
    project_root = _get_project_root_dir()

    candidate_dirs: List[str] = []
    if env_dir:
        candidate_dirs.extend(_expand_path_candidates(env_dir))

    if session_id:
        candidate_dirs.extend(
            [
                os.path.abspath(os.path.join(project_root, "reference_docs", session_id)),
                os.path.abspath(os.path.join(cwd, "ResearchAgent", "reference_docs", session_id)),
                os.path.abspath(os.path.join(cwd, "reference_docs", session_id)),
                os.path.abspath(
                    os.path.join(os.path.dirname(cwd), "ResearchAgent", "reference_docs", session_id)
                ),
            ]
        )

    candidate_dirs.extend(
        [
            _get_module_reference_doc_dir(),
            os.path.abspath(os.path.join(project_root, "reference_docs")),
            os.path.abspath(os.path.join(cwd, "ResearchAgent", "reference_docs")),
            os.path.abspath(os.path.join(cwd, "reference_docs")),
            os.path.abspath(
                os.path.join(os.path.dirname(cwd), "ResearchAgent", "reference_docs")
            ),
        ]
    )

    deduped: List[str] = []
    seen = set()
    for candidate in candidate_dirs:
        normalized = os.path.normcase(os.path.abspath(candidate))
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(os.path.abspath(candidate))
    return deduped


def _get_reference_doc_dir(session_id: Optional[str] = None) -> str:
    candidate_dirs = _get_reference_doc_dir_candidates(session_id)
    for candidate in candidate_dirs:
        if os.path.isdir(candidate):
            return candidate

    return candidate_dirs[0]


def _resolve_reference_doc_path(doc_path: Optional[str], session_id: Optional[str] = None) -> Optional[str]:
    if doc_path and doc_path.strip():
        # Clean aggressive LLM hallucinations like "doc- brand.txt" or "file: brand.txt"
        clean_path = doc_path.strip()
        clean_path = re.sub(r'^(doc-|docs-|file:|path:)\s*', '', clean_path, flags=re.IGNORECASE)
        clean_path = clean_path.strip()

        for candidate in _expand_path_candidates(clean_path):
            if os.path.exists(candidate):
                return candidate
        
        # Fallback: check inside reference doc directories
        base_name = os.path.basename(clean_path)
        for ref_dir in _get_reference_doc_dir_candidates(session_id):
            if not os.path.isdir(ref_dir):
                continue
            cand = os.path.join(ref_dir, base_name)
            if os.path.exists(cand):
                return cand
            
            # Simple fix for singular vs. plural typos (e.g., brand_guideline.txt)
            if base_name.endswith('.txt'):
                alt_base = base_name[:-5] + '.txt' if base_name.endswith('s.txt') else base_name[:-4] + 's.txt'
                alt_cand = os.path.join(ref_dir, alt_base)
                if os.path.exists(alt_cand):
                    return alt_cand

        return os.path.abspath(clean_path)

    env_doc_path = _get_reference_doc_path_from_env()
    if env_doc_path and os.path.exists(env_doc_path):
        return env_doc_path

    reference_dir = _get_reference_doc_dir(session_id)
    if not os.path.isdir(reference_dir):
        return None

    candidate_files = []
    for file_name in os.listdir(reference_dir):
        full_path = os.path.join(reference_dir, file_name)
        if not os.path.isfile(full_path):
            continue
        _, ext = os.path.splitext(file_name)
        if ext.lower() not in _SUPPORTED_DOC_EXTENSIONS:
            continue
        candidate_files.append(full_path)

    if not candidate_files:
        return None

    candidate_files.sort(key=lambda path: os.path.getmtime(path), reverse=True)
    return candidate_files[0]


def _get_embedding_model() -> str:
    return os.environ.get("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")


def _get_embedding_model_candidates() -> List[str]:
    configured = _get_embedding_model()
    candidates = [
        configured,
        "models/gemini-embedding-001",
        "gemini-embedding-001",
        "models/embedding-001",
        "embedding-001",
        "models/text-embedding-004",
        "text-embedding-004",
    ]
    seen = set()
    unique_candidates = []
    for candidate in candidates:
        normalized = (candidate or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_candidates.append(normalized)
    return unique_candidates


def _discover_embedding_models() -> List[str]:
    global _DISCOVERED_EMBEDDING_MODELS
    if _DISCOVERED_EMBEDDING_MODELS is not None:
        return _DISCOVERED_EMBEDDING_MODELS

    discovered: List[str] = []
    try:
        for model in genai.list_models():
            methods = getattr(model, "supported_generation_methods", []) or []
            supports_embed = any(
                str(method).lower() in {"embedcontent", "batchembedcontents"}
                for method in methods
            )
            if supports_embed:
                model_name = getattr(model, "name", None)
                if model_name:
                    discovered.append(str(model_name))
    except Exception:
        discovered = []

    _DISCOVERED_EMBEDDING_MODELS = discovered
    return discovered


def _get_active_embedding_model() -> str:
    return _RESOLVED_EMBEDDING_MODEL or _get_embedding_model()


def _embed_text(text: str, task_type: str) -> List[float]:
    global _RESOLVED_EMBEDDING_MODEL

    candidate_models = _get_embedding_model_candidates()
    discovered_models = _discover_embedding_models()
    candidate_models = candidate_models + [
        model for model in discovered_models if model not in candidate_models
    ]

    if _RESOLVED_EMBEDDING_MODEL and _RESOLVED_EMBEDDING_MODEL in candidate_models:
        candidate_models = [_RESOLVED_EMBEDDING_MODEL] + [
            model for model in candidate_models if model != _RESOLVED_EMBEDDING_MODEL
        ]

    errors: List[str] = []
    for model_name in candidate_models:
        try:
            response = genai.embed_content(
                model=model_name,
                content=text,
                task_type=task_type,
            )
            _RESOLVED_EMBEDDING_MODEL = model_name
            return response["embedding"]
        except Exception as first_exc:
            try:
                response = genai.embed_content(
                    model=model_name,
                    content=text,
                )
                _RESOLVED_EMBEDDING_MODEL = model_name
                return response["embedding"]
            except Exception as second_exc:
                errors.append(f"{model_name}: {second_exc}")
                errors.append(f"{model_name} (with task_type): {first_exc}")

    raise RuntimeError("No embedding model available. " + " | ".join(errors[:4]))


def _read_document_text(doc_path: str) -> str:
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"Document not found: {doc_path}")

    _, ext = os.path.splitext(doc_path)
    ext = ext.lower()

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError(
                "Reading PDF requires pypdf. Install with `pip install pypdf`."
            ) from exc

        reader = PdfReader(doc_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    with open(doc_path, "r", encoding="utf-8", errors="ignore") as handle:
        raw_text = handle.read()

    if ext == ".json":
        try:
            parsed = json.loads(raw_text)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            return raw_text

    return raw_text


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return []

    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)

    chunks: List[str] = []
    start = 0
    text_len = len(normalized)

    while start < text_len:
        end = min(text_len, start + chunk_size)
        chunks.append(normalized[start:end])
        if end >= text_len:
            break
        start = max(0, end - overlap)

    return chunks


def _score_chunk(chunk: str, terms: List[str]) -> int:
    lowered = chunk.lower()
    score = 0
    for term in terms:
        if term:
            score += lowered.count(term)
    return score


def rag_over_uploaded_doc(
    query: str,
    doc_path: Optional[str] = None,
    document_text: Optional[str] = None,
    max_chunks: int = 4,
    chunk_size: int = 900,
    overlap: int = 150,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Semantic RAG over an uploaded document using Gemini embeddings + local Chroma vector DB.
    Accepts either a document path or raw text and returns top semantically similar chunks.
    """
    if chromadb is None:
        return {
            "error": "Missing dependency: chromadb. Install it with `pip install chromadb`."
        }

    if not query or not query.strip():
        return {"error": "Query is required."}

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {
            "error": "GOOGLE_API_KEY is not set. Required for embedding generation."
        }
    genai.configure(api_key=api_key)

    source_id: str
    
    session_id = None
    if tool_context and hasattr(tool_context, "session") and tool_context.session:
        session_id = tool_context.session.id

    resolved_doc_path = _resolve_reference_doc_path(doc_path, session_id)
    if document_text:
        text = document_text
        source_id = f"inline_{hashlib.sha1(document_text.encode('utf-8')).hexdigest()}"
    elif resolved_doc_path:
        try:
            text = _read_document_text(resolved_doc_path)
            source_id = resolved_doc_path
        except (FileNotFoundError, ImportError) as exc:
            return {"error": str(exc)}
    else:
        return {
            "error": "Provide either doc_path/document_text or configure RESEARCH_REFERENCE_DOC_PATH / RESEARCH_REFERENCE_DOC_DIR.",
            "cwd": os.getcwd(),
            "searched_reference_dirs": _get_reference_doc_dir_candidates(session_id),
        }

    chunks = _chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        return {"error": "Document is empty or could not be parsed."}

    if max_chunks < 1:
        max_chunks = 1

    try:
        db_dir = _get_vector_db_dir()
        os.makedirs(db_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=db_dir)

        collection_name = _sanitize_collection_name(
            f"{source_id}_{chunk_size}_{overlap}"
        )
        collection = client.get_or_create_collection(name=collection_name)

        if collection.count() == 0:
            embeddings = [_embed_text(chunk, "retrieval_document") for chunk in chunks]
            ids = [f"chunk_{idx}" for idx in range(len(chunks))]
            metadatas = [{"chunk_index": idx} for idx in range(len(chunks))]
            collection.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )

        query_embedding = _embed_text(query, "retrieval_query")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(max_chunks, len(chunks)),
            include=["documents", "distances", "metadatas"],
        )

        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        top_hits = []
        for doc_text, distance, metadata in zip(docs, distances, metadatas):
            similarity = 1.0 / (1.0 + float(distance))
            chunk_index = metadata.get("chunk_index") if metadata else None
            citation_id = (
                f"DOC-{int(chunk_index) + 1}" if isinstance(chunk_index, int) else "DOC-?"
            )
            top_hits.append(
                {
                    "citation_id": citation_id,
                    "score": round(similarity, 6),
                    "distance": round(float(distance), 6),
                    "chunk_index": chunk_index,
                    "source": {
                        "type": "uploaded_document",
                        "doc_path": resolved_doc_path,
                        "doc_identifier": source_id,
                        "chunk_index": chunk_index,
                    },
                    "text": doc_text,
                }
            )
    except Exception as exc:
        terms = re.findall(r"[a-zA-Z0-9]+", query.lower())
        scored = []
        for idx, chunk in enumerate(chunks):
            score = _score_chunk(chunk, terms)
            scored.append((idx, score, chunk))

        scored.sort(key=lambda item: item[1], reverse=True)
        fallback_hits = scored[: min(max_chunks, len(scored))]

        top_hits = []
        for rank, (chunk_index, score, chunk_text) in enumerate(fallback_hits, start=1):
            citation_id = f"DOC-{chunk_index + 1}"
            top_hits.append(
                {
                    "citation_id": citation_id,
                    "score": float(score),
                    "distance": None,
                    "chunk_index": chunk_index,
                    "source": {
                        "type": "uploaded_document",
                        "doc_path": resolved_doc_path,
                        "doc_identifier": source_id,
                        "chunk_index": chunk_index,
                    },
                    "text": chunk_text,
                    "retrieval_rank": rank,
                }
            )

        return {
            "doc_path": resolved_doc_path,
            "doc_identifier": source_id,
            "vector_db": "chroma",
            "embedding_model": _get_active_embedding_model(),
            "vector_db_dir": _get_vector_db_dir(),
            "reference_doc_dir": _get_reference_doc_dir(session_id),
            "total_chunks": len(chunks),
            "retrieval_mode": "keyword_fallback",
            "warning": f"Semantic retrieval unavailable, using keyword fallback: {str(exc)}",
            "references": [
                {
                    "source_type": "uploaded_document",
                    "doc_path": resolved_doc_path,
                    "doc_identifier": source_id,
                    "citation_id": hit.get("citation_id"),
                    "chunk_index": hit.get("chunk_index"),
                    "distance": hit.get("distance"),
                }
                for hit in top_hits
            ],
            "matches": top_hits,
        }

    return {
        "doc_path": resolved_doc_path,
        "doc_identifier": source_id,
        "vector_db": "chroma",
        "embedding_model": _get_active_embedding_model(),
        "vector_db_dir": _get_vector_db_dir(),
        "reference_doc_dir": _get_reference_doc_dir(),
        "total_chunks": len(chunks),
        "references": [
            {
                "source_type": "uploaded_document",
                "doc_path": resolved_doc_path,
                "doc_identifier": source_id,
                "citation_id": hit.get("citation_id"),
                "chunk_index": hit.get("chunk_index"),
                "distance": hit.get("distance"),
            }
            for hit in top_hits
        ],
        "matches": top_hits,
    }


async def generate_concept_images(prompt: str, tool_context: ToolContext = None,number_of_images=4) -> str:
    """
    Generates images and registers them as ADK artifacts with proper MIME types.
    """
    from google import genai as new_genai
    from google.genai import types as new_types
    
    target_number = max(1, min(12, int(number_of_images)))
    
    client = new_genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    all_generated_images = []
    images_left = target_number
    
    while images_left > 0:
        batch_size = min(4, images_left)
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=new_types.GenerateImagesConfig(number_of_images=batch_size)
        )
        all_generated_images.extend(response.generated_images)
        images_left -= batch_size
    
    save_dir = "concept_outputs"
    os.makedirs(save_dir, exist_ok=True)
    
    for i, generated_image in enumerate(all_generated_images):
        file_name = f"concept_{i+1}_{uuid.uuid4().hex[:8]}.png"
        
        # 1. Local Disk Save
        save_path = os.path.join(save_dir, file_name)
        generated_image.image.save(location=save_path)

        # 2. Artifact Save (UI Detection)
        if tool_context:
            try:
                # Wrap bytes in a Part object with a clear mime_type
                from google.genai import types as adk_types
                image_part = adk_types.Part.from_bytes(
                    data=generated_image.image.image_bytes, 
                    mime_type="image/png"
                )
                
                # Use await for the artifact service
                await tool_context.save_artifact(
                    filename=file_name, 
                    artifact=image_part
                )
            except ValueError as e:
                # In demo mode, there might not be an artifact service attached to the runner
                print(f"Skipping save_artifact: {e}")

    return f"Successfully generated {len(all_generated_images)} image(s) and saved them as artifacts."

from pydantic import BaseModel, Field

from typing import Dict, Any

class ProjectBrief(BaseModel):
    intent: str = Field(default="", description="The specific intent selected by the user (e.g., 'Visual Moodboards').")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="A dictionary of key-value pairs representing the answers to the intent's questions.")
    miscellaneous: str = Field(default="", description="Any other constraints, requirements, or notes provided by the user.")

async def update_brief(
    brief: ProjectBrief,
    locked: bool,
    tool_context: ToolContext = None
) -> str:
    """Updates the project brief in the shared session context. ONLY call this tool with locked=True if the user has provided ALL mandatory fields for the selected intent."""
    if tool_context is None:
        return "Warning: ToolContext not available."
    
    # Handle case where LLM/ADK passes a dict instead of instantiated model
    if isinstance(brief, dict):
        brief = ProjectBrief(**brief)
        
    tool_context.state["brief"] = {
        "intent": brief.intent,
        "parameters": brief.parameters,
        "miscellaneous": brief.miscellaneous,
        "locked": locked
    }
    
    tool_context.state["status"] = "EXECUTION" if locked else "BRIEFING"
    
    # Snapshot the session state into the Artifacts UI
    try:
        from google.genai import types as adk_types
        state_json = json.dumps(tool_context.state, indent=2)
        json_part = adk_types.Part.from_bytes(
            data=state_json.encode('utf-8'),
            mime_type="application/json"
        )
        file_name = f"session_state_{uuid.uuid4().hex[:8]}.json"
        await tool_context.save_artifact(
            filename=file_name, 
            artifact=json_part
        )
    except Exception as e:
        print(f"Skipping save_artifact for state json: {e}")
    
    msg = f"Brief updated successfully. Status: {tool_context.state['status']}. "
    if not locked:
        msg += "Brief is NOT locked. Ask the user for any missing information."
    else:
        msg += "Brief is LOCKED. You may proceed to execution."
        
    return msg

async def update_generation_state(artifacts_key: str, content: list[str], tool_context: ToolContext = None) -> str:
    """Updates the generation state artifacts (e.g. text_concepts, visual_assets) in the shared session context."""
    if tool_context is None:
        return "Warning: ToolContext not available."
    
    if "generation_state" not in tool_context.state:
        tool_context.state["generation_state"] = {"artifacts": {}}
    elif "artifacts" not in tool_context.state["generation_state"]:
        tool_context.state["generation_state"]["artifacts"] = {}
    
    tool_context.state["generation_state"]["artifacts"][artifacts_key] = content
    
    try:
        from google.genai import types as adk_types
        text_content = "\n".join(content)
        # Wrap bytes in a Part object with a clear mime_type for the UI
        text_part = adk_types.Part.from_bytes(
            data=text_content.encode('utf-8'),
            mime_type="text/plain"
        )
        file_name = f"{artifacts_key}_{uuid.uuid4().hex[:8]}.txt"
        await tool_context.save_artifact(
            filename=file_name, 
            artifact=text_part
        )
    except Exception as e:
        # In demo mode, there might not be an artifact service attached to the runner
        print(f"Skipping save_artifact for text: {e}")
        
    return f"Updated {artifacts_key} in generation_state and exported as artifact."
