# rag_agent/tools/get_corpus_info.py

from typing import Dict, List, Union
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from .utils import check_corpus_exists, get_corpus_resource_name


def get_corpus_info(corpus_name: str, tool_context: ToolContext) -> dict:
    """
    Get detailed information about a specific RAG corpus, including its files.

    Args:
        corpus_name (str): The full resource name of the corpus to get information about.
                            Preferably use the resource_name from list_corpora results.
        tool_context (ToolContext): The tool context for state management

    Returns:
        dict: Information about the corpus and its files
    """
    try:
        # Check if corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
                "corpus_name": corpus_name,
            }

        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Get the corpus object to access its display name
        corpus = rag.get_corpus(corpus_resource_name)
        corpus_display_name = corpus.display_name

        # Get the list of files
        files = rag.list_files(corpus_resource_name)
        file_details = []

        for rag_file in files:
            # Get document specific details
            file_info = {
                "file_id": rag_file.name.split("/")[-1],
                "display_name": rag_file.display_name,
                "source_uri": (
                    rag_file.source_uri if hasattr(rag_file, "source_uri") else ""
                ),
                "create_time": (
                    str(rag_file.create_time)
                    if hasattr(rag_file, "create_time")
                    else ""
                ),
                "update_time": (
                    str(rag_file.update_time)
                    if hasattr(rag_file, "update_time")
                    else ""
                ),
            }
            file_details.append(file_info)

        return {
            "status": "success",
            "message": f"Successfully retrieved information for corpus '{corpus_display_name}'",
            "corpus_name": corpus_name,
            "corpus_display_name": corpus_display_name,
            "file_count": len(file_details),
            "files": file_details,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting corpus information: {str(e)}",
        }
