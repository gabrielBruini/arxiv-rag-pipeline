import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from shared.domain.interfaces.vector_store_repository import VectorStoreRepository


def _to_point_id(arxiv_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"arxiv:{arxiv_id}"))

class QdrantRepository(VectorStoreRepository):

    _RETRIEVE_CHUNK_SIZE = 500

    def __init__(self, collection_name: str = "arxiv_cs_papers", host: str = "localhost", port: int = 6333):
        self._client = QdrantClient(host=host, port=port)
        self._collection_name = collection_name

    def ensure_collection(self, dimension: int) -> None:
        if self._client.collection_exists(self._collection_name):
            params = self._client.get_collection(self._collection_name).config.params.vectors
            existing = params.size if isinstance(params, VectorParams) else None
            if existing is not None and existing != dimension:
                raise ValueError(
                    f"Collection '{self._collection_name}' has dimension {existing}, but the "
                    f"embedding model produces {dimension}. Recreate the collection or use a "
                    "matching model."
                )
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    def exists_batch(self, point_ids: list[str]) -> set[str]:
        original_by_point_id = {_to_point_id(pid): pid for pid in point_ids}

        existing: set[str] = set()
        ids = list(original_by_point_id)
        for start in range(0, len(ids), self._RETRIEVE_CHUNK_SIZE):
            chunk = ids[start : start + self._RETRIEVE_CHUNK_SIZE]
            records = self._client.retrieve(
                collection_name=self._collection_name,
                ids=chunk,
                with_payload=False,
                with_vectors=False,
            )
            existing.update(original_by_point_id[str(record.id)] for record in records)

        return existing

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

    def is_healthy(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception:
            return False
