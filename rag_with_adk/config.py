import os

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- Vertex AI Settings ---
# These are pulled from your .env file which you configured during setup.
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")

# --- RAG Settings ---
# These are the default parameters for how the RAG service should behave.

# The size of each text chunk in tokens when a document is processed.
DEFAULT_CHUNK_SIZE = 512

# The number of tokens that overlap between consecutive chunks.
# This helps maintain context across chunks.
DEFAULT_CHUNK_OVERLAP = 100

# The default number of top matching results to retrieve from the vector store.
DEFAULT_TOP_K = 3

# A similarity threshold for filtering results. Only results with a score
# above this value will be returned. (Ranges typically from 0 to 1).
DEFAULT_DISTANCE_THRESHOLD = 0.5

# The specific embedding model used to convert text to vectors.
DEFAULT_EMBEDDING_MODEL = "publishers/google/models/text-embedding-004"

# A rate limit to stay within the API's quotas when importing many files at once.
DEFAULT_EMBEDDING_REQUESTS_PER_MIN = 1000
