from rag.config import Settings

_VARS = [
    "QDRANT_HOST",
    "QDRANT_PORT",
    "QDRANT_COLLECTION",
    "OLLAMA_MODEL",
    "OLLAMA_BASE_URL",
    "RAG_TOP_K",
    "EMBEDDING_MODEL",
    "EMBEDDING_DEVICE",
]


def test_defaults_when_env_absent(monkeypatch):
    for var in _VARS:
        monkeypatch.delenv(var, raising=False)
    s = Settings.from_env()
    assert s.qdrant_host == "localhost"
    assert s.qdrant_port == 6333
    assert s.qdrant_collection == "arxiv_cs_papers"
    assert s.top_k == 5
    assert s.embedding_device is None


def test_reads_from_env(monkeypatch):
    monkeypatch.setenv("QDRANT_HOST", "qdrant")
    monkeypatch.setenv("QDRANT_PORT", "7000")
    monkeypatch.setenv("RAG_TOP_K", "3")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    s = Settings.from_env()
    assert s.qdrant_host == "qdrant"
    assert s.qdrant_port == 7000
    assert s.top_k == 3
    assert s.ollama_model == "mistral"
