import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Configuração da API de RAG, lida a partir de variáveis de ambiente."""

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str | None = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "arxiv_cs_papers"
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"
    top_k: int = 5

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
        )


def configure_tls_certificates() -> None:
    """Aponta as libs HTTP para o bundle de CAs do certifi quando o ambiente não
    tem um configurado.

    Em máquinas Windows sem os CAs corretos no store do sistema, o download de
    modelos do HuggingFace falha com CERTIFICATE_VERIFY_FAILED. Usar o bundle do
    certifi resolve isso sem desabilitar a verificação de certificado. Só preenche
    as variáveis se ainda não estiverem definidas, respeitando overrides do usuário.
    """
    try:
        import certifi
    except ImportError:
        return

    bundle = certifi.where()
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
