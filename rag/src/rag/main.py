from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel

from ingestion.infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)
from ingestion.infrastructure.vector_store.qdrant_repository import QdrantRepository

from rag.application.usecases.answer_question import AnswerQuestionUseCase
from rag.config import Settings, configure_tls_certificates
from rag.infrastructure.llm.ollama_repository import OllamaRepository
from rag.infrastructure.session.in_memory_session_store import InMemorySessionStore


def build_use_case(settings: Settings) -> AnswerQuestionUseCase:
    """Monta o caso de uso e suas dependências a partir da configuração."""
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
    session_store = InMemorySessionStore()

    return AnswerQuestionUseCase(
        embedder=embedder,
        store=store,
        llm=llm,
        session_store=session_store,
        top_k=settings.top_k,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga pesada (modelo de embedding, clientes) acontece aqui, no startup,
    # e não na importação do módulo — mantém o import barato e os erros explícitos.
    configure_tls_certificates()
    settings = Settings.from_env()
    app.state.use_case = build_use_case(settings)
    yield
    app.state.use_case = None


app = FastAPI(title="arXiv RAG API", lifespan=lifespan)


def get_use_case(request: Request) -> AnswerQuestionUseCase:
    return request.app.state.use_case


class ChatRequest(BaseModel):
    session_id: str
    question: str


class Source(BaseModel):
    arxiv_id: str
    title: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    use_case: AnswerQuestionUseCase = Depends(get_use_case),
) -> ChatResponse:
    result = use_case.execute(session_id=request.session_id, question=request.question)
    return ChatResponse(answer=result.answer, sources=result.sources)
