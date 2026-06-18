from unittest.mock import MagicMock, patch

import rag.main as main
import requests
from fastapi.testclient import TestClient
from rag.application.usecases.answer_question import AnswerResult
from rag.main import AppDependencies


def _deps(use_case=None, qdrant_ok=True, ollama_ok=True, session_ok=True):
    store = MagicMock()
    store.is_healthy.return_value = qdrant_ok
    llm = MagicMock()
    llm.is_healthy.return_value = ollama_ok
    session = MagicMock()
    session.is_healthy.return_value = session_ok
    return AppDependencies(
        use_case=use_case or MagicMock(), store=store, llm=llm, session_store=session
    )


def _patched(deps):
    return patch.object(main, "build_dependencies", return_value=deps)


def test_health_returns_ok():
    with _patched(_deps()):
        with TestClient(main.app) as client:
            r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_ok_when_dependencies_healthy():
    with _patched(_deps()):
        with TestClient(main.app) as client:
            r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True


def test_ready_503_when_a_dependency_is_down():
    with _patched(_deps(qdrant_ok=False)):
        with TestClient(main.app) as client:
            r = client.get("/ready")
    assert r.status_code == 503


def test_ready_503_when_session_store_is_down():
    with _patched(_deps(session_ok=False)):
        with TestClient(main.app) as client:
            r = client.get("/ready")
    assert r.status_code == 503


def test_chat_returns_answer_and_sources():
    uc = MagicMock()
    uc.execute.return_value = AnswerResult(
        answer="hi", sources=[{"arxiv_id": "1", "title": "T"}]
    )
    with _patched(_deps(use_case=uc)):
        with TestClient(main.app) as client:
            r = client.post("/chat", json={"session_id": "s", "question": "q"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "hi"
    assert body["sources"] == [{"arxiv_id": "1", "title": "T"}]


def test_chat_503_on_dependency_error():
    uc = MagicMock()
    uc.execute.side_effect = requests.RequestException("ollama down")
    with _patched(_deps(use_case=uc)):
        with TestClient(main.app) as client:
            r = client.post("/chat", json={"session_id": "s", "question": "q"})
    assert r.status_code == 503
