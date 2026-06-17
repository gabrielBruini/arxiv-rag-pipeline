from abc import ABC, abstractmethod


class EmbeddingRepository(ABC):
    """Contrato para qualquer implementação que transforme texto em vetores."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Gera o embedding de um único texto."""
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings para uma lista de textos de uma vez (mais eficiente)."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensão dos vetores gerados (necessário para configurar a collection do Qdrant)."""
        raise NotImplementedError