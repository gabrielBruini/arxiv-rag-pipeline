from abc import ABC, abstractmethod
from typing import Any


class VectorStoreRepository(ABC):
    """Contrato para qualquer implementação de banco vetorial (Qdrant, Weaviate, Pinecone, etc)."""

    @abstractmethod
    def ensure_collection(self, dimension: int) -> None:
        """Garante que a collection existe, criando-a se necessário."""
        raise NotImplementedError

    @abstractmethod
    def exists_batch(self, point_ids: list[str]) -> set[str]:
        """Dado um lote de ids, retorna o subconjunto que JÁ existe na collection."""
        raise NotImplementedError

    @abstractmethod
    def upsert(self, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        """Insere ou sobrescreve um ponto na collection."""
        raise NotImplementedError

    @abstractmethod
    def search(self, vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        """Busca os pontos mais similares a um vetor de consulta."""
        raise NotImplementedError