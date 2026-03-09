import os


def _load_model_name() -> str:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("Warning: python-dotenv not installed. Ensure API key is set")

    return os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.5-flash-lite")


def _env_flag(name: str, default: bool = True) -> bool:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


MODEL_NAME = _load_model_name()
ENABLE_WEB_RESEARCH = _env_flag("ENABLE_WEB_RESEARCH", True)
ENABLE_RAG_RESEARCH = _env_flag("ENABLE_RAG_RESEARCH", True)
