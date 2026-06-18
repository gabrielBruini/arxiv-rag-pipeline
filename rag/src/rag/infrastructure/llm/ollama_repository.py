import os

import requests

from rag.domain.interfaces.llm_repository import NO_ANSWER_SIGNAL, LLMRepository

_SYSTEM_PROMPT_TEMPLATE = """You are an expert assistant in Computer Science academic research.
Answer the user's question based ONLY on the papers provided below.
Always respond in English, regardless of the language of the question.
If the papers do not contain enough information to answer, respond EXACTLY with the text {no_answer_signal} and nothing else — do not make anything up.
Whenever you use information from a specific paper, cite its arxiv_id in parentheses.

Available papers:
{context}
"""

class OllamaRepository(LLMRepository):

    def __init__(self, model: str | None = None, base_url: str | None = None):
        self._model = model or os.environ.get("OLLAMA_MODEL", "llama3.1")
        self._base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, messages: list[dict[str, str]], context: str) -> str:
        system_message = {
            "role": "system",
            "content": _SYSTEM_PROMPT_TEMPLATE.format(
                context=context, no_answer_signal=NO_ANSWER_SIGNAL
            ),
        }

        payload = {
            "model": self._model,
            "messages": [system_message, *messages],
            "stream": False,
        }

        response = requests.post(f"{self._base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data["message"]["content"]

    def is_healthy(self) -> bool:
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
