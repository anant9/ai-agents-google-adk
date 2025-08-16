# rag_agent/tools/utils.py

import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from . import config


def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Convert a corpus name to its full resource name if needed. Handles various input formats and ensures the returned name
    is what Vertex AI's requirements.

    Args:
        corpus_name (str): The corpus name or display name

    Returns:
        str: The full resource name of the corpus
    """
    # Remove any special characters that might cause issues
    corpus_id = re.sub(r"[^a-zA-Z0-9-_]", "_", corpus_name)

    # Construct the standardized resource name
    return f"projects/{config.PROJECT_ID}/locations/{config.LOCATION}/ragCorpora/{corpus_id}"


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Check if a corpus with the given name exists.

    Args:
        corpus_name (str): The name of the corpus to check
        tool_context (ToolContext): The tool context for state management

    Returns:
        bool: True if the corpus exists, False otherwise
    """
    # Check state first if tool_context is provided
    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True

    try:
        # Get full resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # List all corpora and check if this one exists
        corpora = rag.list_corpora()
        for corpus in corpora:
            if (
                corpus.name == corpus_resource_name
                or corpus.display_name == corpus_name
            ):
                # Update state
                tool_context.state[f"corpus_exists_{corpus_name}"] = True
                # Also set this as the current corpus if no current corpus is set
                if not tool_context.state.get("current_corpus"):
                    tool_context.state["current_corpus"] = corpus_name
                return True
        return False
    except Exception as e:
        print(f"Error checking if corpus exists: {str(e)}")
        # If we can't check, assume it doesn't exist
        return False
