from abc import ABC, abstractmethod

# Sinal que o LLM deve emitir quando os papers recuperados não têm informação
# suficiente para responder. É parte do contrato: a implementação instrui o modelo
# a devolvê-lo, e o caso de uso o detecta para não retornar sources fabricados.
NO_ANSWER_SIGNAL = "NO_ANSWER"


class LLMRepository(ABC):
    """Contrato para qualquer implementação de LLM (Ollama, etc) usada para gerar respostas."""

    @abstractmethod
    def generate(self, messages: list[dict[str, str]], context: str) -> str:
        """
        Gera uma resposta com base no histórico de mensagens e no contexto recuperado.

        messages: histórico de conversa, formato [{"role": "user"|"assistant", "content": str}, ...]
        context: texto com os papers recuperados (título + abstract), a ser usado como base factual da resposta
        """
        raise NotImplementedError