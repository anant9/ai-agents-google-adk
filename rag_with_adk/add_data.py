
import re
import os
from typing import Dict, List
from google.adk.tools.tool_context import ToolContext
from .utils import get_corpus_resource_name
from vertexai import rag
from . import config
from google.cloud import storage
from google.oauth2 import service_account

KEY_FILE_PATH = os.path.join(os.path.dirname(__file__), 'rag-accessor-key.json')

def add_data(corpus_name: str, paths: List[str], tool_context: ToolContext) -> dict:
    """
    Add new data sources from Google Cloud Storage to a Vertex AI RAG corpus.
    """
    
    # Get the full resource name for the corpus.
    corpus_resource_name = get_corpus_resource_name(corpus_name)
    if not corpus_resource_name:
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' could not be found. Please check the name and try again. You can use the list_corpora function to see available corpora."
        }

    # Validate all paths are GCS paths.
    for path in paths:
        if not path.startswith("gs://"):
            return {"status": "error", "message": f"Unsupported path format: {path}. Please provide a GCS path (e.g., gs://your-bucket/your-file.pdf)."}

    try:
        # Authenticate using the service account key file.
        credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
        storage_client = storage.Client(credentials=credentials)
        
        # This is a lightweight check to ensure the files exist before starting the import.
        for path in paths:
            bucket_name = path.split('/')[2]
            blob_name = '/'.join(path.split('/')[3:])
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            if not blob.exists():
                 return {"status": "error", "message": f"The file at GCS path '{path}' does not exist or you do not have permission to access it."}

        # Proceed with the import
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=config.DEFAULT_CHUNK_SIZE,
                chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
            )
        )
        import_result = rag.import_files(
            corpus_resource_name,
            paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=config.DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )
        return {"status": "success", "message": f"Successfully started import for {len(paths)} file(s) into corpus '{corpus_name}'.", "import_result": str(import_result)}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred while adding data to the corpus: {e}"}
