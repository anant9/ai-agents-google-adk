import re
from typing import Dict

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from . import config
from .utils import check_corpus_exists, get_corpus_resource_name


def create_corpus(corpus_name: str, tool_context: ToolContext) -> dict:
    """
    Create a new Vertex AI RAG corpus with the specified name.

    Args:
        corpus_name (str): The name for the new corpus
        tool_context (ToolContext): The tool context for state management

    Returns:
        dict: Status information about the operation
    """
    # Check if a corpus with this name already exists to prevent errors
    if check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "info",
            "message": f"Corpus '{corpus_name}' already exists",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }

    try:
        # Clean the corpus name to ensure it's a valid display name
        display_name = re.sub(r"[^a-zA-Z0-9-_]", "_", corpus_name)

        # Configure which embedding model the corpus will use.
        # This is essential for converting documents into vectors.
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model=config.DEFAULT_EMBEDDING_MODEL
            )
        )

        # This is the actual API call to create the corpus in Vertex AI
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )

        # Update the agent's state to remember that this corpus now exists
        tool_context.state[f"corpus_exists_{corpus_name}"] = True

        # Set this newly created corpus as the "current" one for subsequent commands
        tool_context.state["current_corpus"] = corpus_name

        # Return a success message with details about the new corpus
        return {
            "status": "success",
            "message": f"Successfully created corpus '{corpus_name}'",
            "corpus_name": rag_corpus.name,
            "display_name": rag_corpus.display_name,
            "corpus_created": True,
        }
    except Exception as e:
        # If anything goes wrong, return a detailed error message
        return {
            "status": "error",
            "message": f"Error creating corpus: {str(e)}",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }
