
import re
from typing import Optional
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from . import config

def _find_corpus(name_or_id: str) -> Optional[rag.RagCorpus]:
    """Finds a corpus by its full resource name or display name."""
    corpora = rag.list_corpora()
    for corpus in corpora:
        if corpus.name == name_or_id or corpus.display_name == name_or_id:
            return corpus
    return None

def get_corpus_resource_name(name_or_id: str) -> Optional[str]:
    """
    Gets the full resource name for a corpus, whether the input is a
    display name or the resource name itself.
    """
    # If the input is already a resource name, return it.
    resource_name_pattern = r"^projects\/[^\/]+\/locations\/[^\/]+\/ragCorpora\/[^\/]+$"
    if re.match(resource_name_pattern, name_or_id):
        return name_or_id

    # Otherwise, look up the corpus by display name.
    corpus = _find_corpus(name_or_id)
    return corpus.name if corpus else None

def check_corpus_exists(name_or_id: str, tool_context: ToolContext) -> bool:
    """
    Checks if a corpus with the given display name or resource name exists.
    """
    # Check state first
    if tool_context.state.get(f"corpus_exists_{name_or_id}"):
        return True
    
    corpus = _find_corpus(name_or_id)
    if corpus:
        # Cache the result for both identifiers
        tool_context.state[f"corpus_exists_{corpus.display_name}"] = True
        tool_context.state[f"corpus_exists_{corpus.name}"] = True
        return True
        
    return False
