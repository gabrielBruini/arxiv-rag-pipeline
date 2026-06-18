from unittest.mock import MagicMock, patch

from rag.domain.interfaces.llm_repository import NO_ANSWER_SIGNAL
from rag.infrastructure.llm.ollama_repository import (
    OllamaRepository,
    _SYSTEM_PROMPT_TEMPLATE,
)


def test_system_prompt_includes_context_and_signal_and_english():
    prompt = _SYSTEM_PROMPT_TEMPLATE.format(context="CTX", no_answer_signal=NO_ANSWER_SIGNAL)
    assert "CTX" in prompt
    assert NO_ANSWER_SIGNAL in prompt
    assert "English" in prompt


def test_generate_posts_and_returns_content():
    repo = OllamaRepository(model="m", base_url="http://x:11434")
    response = MagicMock()
    response.json.return_value = {"message": {"content": "hello"}}

    with patch(
        "rag.infrastructure.llm.ollama_repository.requests.post", return_value=response
    ) as post:
        out = repo.generate([{"role": "user", "content": "q"}], "CTX")

    assert out == "hello"
    response.raise_for_status.assert_called_once()
    sent = post.call_args.kwargs["json"]
    assert sent["model"] == "m"
    assert sent["messages"][0]["role"] == "system"
    assert "CTX" in sent["messages"][0]["content"]
    assert sent["messages"][-1] == {"role": "user", "content": "q"}
