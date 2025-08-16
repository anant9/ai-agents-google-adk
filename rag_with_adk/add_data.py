# rag_agent/tools/add_data.py

import re
from typing import Dict, List, Union

from google.adk.tools.tool_context import ToolContext
from .utils import check_corpus_exists, get_corpus_resource_name
from vertexai import rag

from . import config


def add_data(corpus_name: str, paths: List[str], tool_context: ToolContext) -> dict:
    """
    Add new data sources to a Vertex AI RAG corpus.

    Args:
        corpus_name (str): The name of the corpus to add data to. If empty, the current corpus will be used.
        paths (List[str]): List of URLs or GCS paths to add to the corpus.
        tool_context (ToolContext): The tool context for state management

    Returns:
        dict: Information about the added data and status
    """
    # ... (code for checking if corpus exists and validating inputs) ...

    # Pre-process paths to validate and convert Google Docs URLs to Drive format if needed
    validated_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        # ... (code for checking valid string) ...

        # Check for Google Docs/Sheets/Slides URLs and convert them to Drive format
        docs_match = re.match(
            r"https?:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9-_]+)",
            path,
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append({path: drive_url})
            continue

        # Check for valid Drive URL format
        drive_match = re.match(
            r"https?:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9-_]+)",
            path,
        )
        if drive_match:
            file_id = drive_match.group(1)
            # Normalize to the standard Drive URL format
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append({path: drive_url})
            continue
        
        # Check for GCS paths
        if path.startswith("gs://"):
            validated_paths.append(path)
            continue
        
        # If we're here, the path wasn't in a recognized format
        invalid_paths.append((path, "Invalid format"))

    # ... (code for handling invalid paths) ...

    try:
        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Set up chunking configuration
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=config.DEFAULT_CHUNK_SIZE,
                chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
            )
        )

        # Import files to the corpus
        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=config.DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )

        # ... (code to build success message and return status) ...

    except Exception as e:
        return {"status": "error", "message": f"Error adding data to corpus: {str(e)}"}
