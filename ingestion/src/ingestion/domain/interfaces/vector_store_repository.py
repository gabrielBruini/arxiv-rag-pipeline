from abc import ABC, abstractmethod
from typing import Any

class VectorStoreRepository(ABC):

    @abstractmethod
    def ensure_collection(self, dimension: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists_batch(self, point_ids: list[str]) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError
