import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str | None = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "arxiv_cs_papers"
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"
    top_k: int = 5
    max_history: int = 10
    session_backend: str = "memory"
    redis_url: str = "redis://localhost:6379/0"
    session_ttl_seconds: int = 86400
    session_max_messages: int = 50

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            embedding_model=os.environ.get("EMBEDDING_MODEL", cls.embedding_model),
            embedding_device=os.environ.get("EMBEDDING_DEVICE") or None,
            qdrant_host=os.environ.get("QDRANT_HOST", cls.qdrant_host),
            qdrant_port=int(os.environ.get("QDRANT_PORT", cls.qdrant_port)),
            qdrant_collection=os.environ.get("QDRANT_COLLECTION", cls.qdrant_collection),
            ollama_model=os.environ.get("OLLAMA_MODEL", cls.ollama_model),
            ollama_base_url=os.environ.get("OLLAMA_BASE_URL", cls.ollama_base_url),
            top_k=int(os.environ.get("RAG_TOP_K", cls.top_k)),
            max_history=int(os.environ.get("RAG_MAX_HISTORY", cls.max_history)),
            session_backend=os.environ.get("SESSION_BACKEND", cls.session_backend),
            redis_url=os.environ.get("REDIS_URL", cls.redis_url),
            session_ttl_seconds=int(os.environ.get("SESSION_TTL_SECONDS", cls.session_ttl_seconds)),
            session_max_messages=int(os.environ.get("SESSION_MAX_MESSAGES", cls.session_max_messages)),
        )

def configure_tls_certificates() -> None:
    try:
        import certifi
    except ImportError:
        return

    bundle = certifi.where()
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
