import os

import requests

from rag.domain.interfaces.llm_repository import NO_ANSWER_SIGNAL, LLMRepository

_SYSTEM_PROMPT_TEMPLATE = """Você é um assistente especialista em pesquisa acadêmica de Ciência da Computação.
Responda à pergunta do usuário com base SOMENTE nos papers fornecidos a seguir.
Se os papers não tiverem informação suficiente para responder, responda EXATAMENTE com o texto {no_answer_signal} e nada mais — não invente.
Sempre que usar informação de um paper específico, cite o arxiv_id entre parênteses.

Papers disponíveis:
{context}
"""


class OllamaRepository(LLMRepository):
    """Implementação do LLMRepository usando um servidor Ollama local."""

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