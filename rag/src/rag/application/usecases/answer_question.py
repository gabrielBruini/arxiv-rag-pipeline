from dataclasses import dataclass
from typing import Any

from shared.domain.interfaces.embedding_repository import EmbeddingRepository
from shared.domain.interfaces.vector_store_repository import VectorStoreRepository

from rag.domain.interfaces.llm_repository import NO_ANSWER_SIGNAL, LLMRepository
from rag.infrastructure.session.in_memory_session_store import InMemorySessionStore

NO_ANSWER_MESSAGE = (
    "I couldn't find enough information in the available papers to answer this question."
)

@dataclass
class AnswerResult:
    answer: str
    sources: list[dict[str, str]]

def _build_context(search_results: list[dict[str, Any]]) -> str:
    blocks = []
    for r in search_results:
        payload = r["payload"]
        blocks.append(
            f"[{payload['arxiv_id']}] {payload['title']}\n{payload['abstract']}"
        )
    return "\n\n".join(blocks)

def _extract_sources(search_results: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"arxiv_id": r["payload"]["arxiv_id"], "title": r["payload"]["title"]}
        for r in search_results
    ]

class AnswerQuestionUseCase:

    def __init__(
        self,
        embedder: EmbeddingRepository,
        store: VectorStoreRepository,
        llm: LLMRepository,
        session_store: InMemorySessionStore,
        top_k: int = 5,
        max_history: int = 10,
    ):
        self._embedder = embedder
        self._store = store
        self._llm = llm
        self._session_store = session_store
        self._top_k = top_k
        self._max_history = max_history

    def execute(self, session_id: str, question: str) -> AnswerResult:
        history = self._session_store.get_history(session_id)

        query_vector = self._embedder.embed(question)
        search_results = self._store.search(query_vector, limit=self._top_k)

        context = _build_context(search_results)
        sources = _extract_sources(search_results)

        recent_history = history[-self._max_history :] if self._max_history else history
        messages = [*recent_history, {"role": "user", "content": question}]
        answer = self._llm.generate(messages, context)

        if answer.strip() == NO_ANSWER_SIGNAL:
            answer = NO_ANSWER_MESSAGE
            sources = []

        self._session_store.append_message(session_id, "user", question)
        self._session_store.append_message(session_id, "assistant", answer)

        return AnswerResult(answer=answer, sources=sources)
