import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

import requests
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

from shared.infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)
from shared.infrastructure.vector_store.qdrant_repository import QdrantRepository

from rag.application.usecases.answer_question import AnswerQuestionUseCase
from rag.config import Settings, configure_tls_certificates
from rag.infrastructure.llm.ollama_repository import OllamaRepository
from rag.infrastructure.session.in_memory_session_store import InMemorySessionStore

logger = logging.getLogger("rag.api")

try:
    from qdrant_client.http.exceptions import (
        ResponseHandlingException,
        UnexpectedResponse,
    )

    _QDRANT_ERRORS: tuple[type[Exception], ...] = (
        ResponseHandlingException,
        UnexpectedResponse,
    )
except Exception:
    _QDRANT_ERRORS = ()

_DEPENDENCY_ERRORS = (requests.RequestException, ConnectionError, *_QDRANT_ERRORS)


@dataclass
class AppDependencies:
    use_case: AnswerQuestionUseCase
    store: QdrantRepository
    llm: OllamaRepository


def build_dependencies(settings: Settings) -> AppDependencies:
    embedder = SentenceTransformerRepository(
        model_name=settings.embedding_model,
        device=settings.embedding_device,
    )
    store = QdrantRepository(
        collection_name=settings.qdrant_collection,
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )
    llm = OllamaRepository(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
    )
    use_case = AnswerQuestionUseCase(
        embedder=embedder,
        store=store,
        llm=llm,
        session_store=InMemorySessionStore(),
        top_k=settings.top_k,
        max_history=settings.max_history,
    )
    return AppDependencies(use_case=use_case, store=store, llm=llm)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_tls_certificates()
    app.state.deps = build_dependencies(Settings.from_env())
    yield
    app.state.deps = None


app = FastAPI(title="arXiv RAG API", lifespan=lifespan)


def get_dependencies(request: Request) -> AppDependencies:
    return request.app.state.deps


class ChatRequest(BaseModel):
    session_id: str
    question: str


class Source(BaseModel):
    arxiv_id: str
    title: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(deps: AppDependencies = Depends(get_dependencies)) -> dict[str, object]:
    checks = {"qdrant": deps.store.is_healthy(), "ollama": deps.llm.is_healthy()}
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail={"ready": False, "checks": checks})
    return {"ready": True, "checks": checks}


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    deps: AppDependencies = Depends(get_dependencies),
) -> ChatResponse:
    try:
        result = deps.use_case.execute(
            session_id=request.session_id, question=request.question
        )
    except _DEPENDENCY_ERRORS:
        logger.exception("Chat failed: upstream dependency error")
        raise HTTPException(
            status_code=503,
            detail="An upstream dependency (vector store or LLM) is unavailable.",
        )
    return ChatResponse(answer=result.answer, sources=result.sources)
