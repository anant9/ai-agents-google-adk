from typing import Dict

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from . import config
from .utils import check_corpus_exists, get_corpus_resource_name


def rag_query(corpus_name: str, query: str, tool_context: ToolContext) -> dict:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.

    Args:
        corpus_name (str): The name of the corpus to query. If empty, the current corpus will be used.
        query (str): The text query to search for in the corpus.
        tool_context (ToolContext): The tool context for state management.

    Returns:
        dict: The query results and status.
    """
    # Use the current corpus from state if corpus_name is not provided
    if not corpus_name:
        corpus_name = tool_context.state.get("current_corpus")
        if not corpus_name:
            return {
                "status": "error",
                "message": "Corpus name not specified and no current corpus is set.",
            }

    # Check if the specified corpus actually exists
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist.",
            "query": query,
            "corpus_name": corpus_name,
        }

    try:
        # Get the full, official resource name required by the API
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configure how the retrieval should behave
        rag_retrieval_config = rag.RagRetrievalConfig(
            # How many of the top results to return
            top_k=config.DEFAULT_TOP_K,
            # Filter results based on similarity score (vector distance)
            filter=rag.Filter(
                vector_distance_threshold=config.DEFAULT_DISTANCE_THRESHOLD
            ),
        )

        # Perform the actual query against the Vertex AI RAG service
        print("Performing retrieval query...")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response into a clean, usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": (
                        ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                    ),
                    "source_name": (
                        ctx_group.source.display_name
                        if hasattr(ctx_group, "source")
                        else ""
                    ),
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)

        # Handle cases where no relevant documents were found
        if not results:
            return {
                "status": "warning",
                "message": f"No results found in corpus '{corpus_name}' for query: '{query}'",
                "query": query,
                "corpus_name": corpus_name,
                "results": [],
                "results_count": 0,
            }

        # Return the successful results
        return {
            "status": "success",
            "message": f"Successfully queried corpus '{corpus_name}'",
            "query": query,
            "corpus_name": corpus_name,
            "results": results,
            "results_count": len(results),
        }
    except Exception as e:
        # Catch and report any errors during the query process
        return {"status": "error", "message": f"Error querying corpus: {str(e)}"}
