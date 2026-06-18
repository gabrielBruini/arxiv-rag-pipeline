from rag.config import Settings

_VARS = [
    "QDRANT_HOST",
    "QDRANT_PORT",
    "QDRANT_COLLECTION",
    "OLLAMA_MODEL",
    "OLLAMA_BASE_URL",
    "RAG_TOP_K",
    "RAG_MAX_HISTORY",
    "EMBEDDING_MODEL",
    "EMBEDDING_DEVICE",
    "SESSION_BACKEND",
    "REDIS_URL",
    "SESSION_TTL_SECONDS",
    "SESSION_MAX_MESSAGES",
]


def test_defaults_when_env_absent(monkeypatch):
    for var in _VARS:
        monkeypatch.delenv(var, raising=False)
    s = Settings.from_env()
    assert s.qdrant_host == "localhost"
    assert s.qdrant_port == 6333
    assert s.qdrant_collection == "arxiv_cs_papers"
    assert s.top_k == 5
    assert s.max_history == 10
    assert s.embedding_device is None
    assert s.session_backend == "memory"
    assert s.session_max_messages == 50


def test_reads_from_env(monkeypatch):
    monkeypatch.setenv("QDRANT_HOST", "qdrant")
    monkeypatch.setenv("QDRANT_PORT", "7000")
    monkeypatch.setenv("RAG_TOP_K", "3")
    monkeypatch.setenv("RAG_MAX_HISTORY", "4")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    monkeypatch.setenv("SESSION_BACKEND", "redis")
    monkeypatch.setenv("SESSION_TTL_SECONDS", "120")
    s = Settings.from_env()
    assert s.qdrant_host == "qdrant"
    assert s.qdrant_port == 7000
    assert s.top_k == 3
    assert s.max_history == 4
    assert s.ollama_model == "mistral"
    assert s.session_backend == "redis"
    assert s.session_ttl_seconds == 120
