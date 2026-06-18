from rag.application.usecases.answer_question import (
    AnswerQuestionUseCase,
    NO_ANSWER_MESSAGE,
)
from rag.domain.interfaces.llm_repository import NO_ANSWER_SIGNAL
from rag.infrastructure.session.in_memory_session_store import InMemorySessionStore


class FakeEmbedder:
    def embed(self, text):
        return [0.0] * 384


class FakeStore:
    def __init__(self, results):
        self.results = results

    def search(self, vector, limit=5):
        return self.results


class FakeLLM:
    def __init__(self, reply):
        self.reply = reply
        self.last_messages = None
        self.last_context = None

    def generate(self, messages, context):
        self.last_messages = messages
        self.last_context = context
        return self.reply


_RESULTS = [
    {"id": "1", "score": 0.9, "payload": {"arxiv_id": "2401.1", "title": "T", "abstract": "A"}}
]


def _use_case(reply, results=_RESULTS, store=None):
    return AnswerQuestionUseCase(
        FakeEmbedder(), FakeStore(results), FakeLLM(reply), store or InMemorySessionStore()
    )


def test_normal_answer_returns_sources():
    r = _use_case("answer (2401.1)").execute("s", "q")
    assert r.answer == "answer (2401.1)"
    assert r.sources == [{"arxiv_id": "2401.1", "title": "T"}]


def test_no_answer_returns_empty_sources_and_friendly_message():
    r = _use_case(NO_ANSWER_SIGNAL).execute("s", "q")
    assert r.sources == []
    assert r.answer == NO_ANSWER_MESSAGE


def test_no_answer_tolerates_surrounding_whitespace():
    r = _use_case(f"  {NO_ANSWER_SIGNAL}\n").execute("s", "q")
    assert r.sources == []
    assert r.answer == NO_ANSWER_MESSAGE


def test_context_passed_to_llm_includes_abstract():
    uc = _use_case("ok")
    uc.execute("s", "q")
    assert "A" in uc._llm.last_context


def test_history_is_persisted_across_calls():
    store = InMemorySessionStore()
    uc = _use_case("a", store=store)
    uc.execute("sess", "first")
    uc.execute("sess", "second")
    contents = [m["content"] for m in store.get_history("sess")]
    assert contents == ["first", "a", "second", "a"]


def test_history_capped_when_sent_to_llm():
    store = InMemorySessionStore()
    llm = FakeLLM("a")
    uc = AnswerQuestionUseCase(
        FakeEmbedder(), FakeStore(_RESULTS), llm, store, max_history=2
    )
    uc.execute("s", "q1")
    uc.execute("s", "q2")
    uc.execute("s", "q3")
    sent = [(m["role"], m["content"]) for m in llm.last_messages]
    assert len(sent) == 3
    assert sent[0] == ("user", "q2")
    assert sent[-1] == ("user", "q3")
