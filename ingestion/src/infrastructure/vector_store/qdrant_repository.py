import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from domain.interfaces.vector_store_repository import VectorStoreRepository


def _to_point_id(arxiv_id: str) -> str:
  
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"arxiv:{arxiv_id}"))


class QdrantRepository(VectorStoreRepository):

    def __init__(self, collection_name: str = "arxiv_cs_papers", host: str = "localhost", port: int = 6333):
        self._client = QdrantClient(host=host, port=port)
        self._collection_name = collection_name

    def ensure_collection(self, dimension: int) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    def exists(self, point_id: str) -> bool:
        result = self._client.retrieve(
            collection_name=self._collection_name,
            ids=[_to_point_id(point_id)],
        )
        return len(result) > 0

    def upsert(self, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        point = PointStruct(
            id=_to_point_id(point_id),
            vector=vector,
            payload=payload,
        )
        self._client.upsert(collection_name=self._collection_name, points=[point])

    def search(self, vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        results = self._client.query_points(
            collection_name=self._collection_name,
            query=vector,
            limit=limit,
        ).points

        return [
            {"id": r.id, "score": r.score, "payload": r.payload}
            for r in results
        ]