from unittest.mock import MagicMock, patch

from shared.infrastructure.vector_store import qdrant_repository
from shared.infrastructure.vector_store.qdrant_repository import (
    QdrantRepository,
    _to_point_id,
)


def _repo():
    with patch.object(qdrant_repository, "QdrantClient"):
        return QdrantRepository(collection_name="c")


def test_to_point_id_is_deterministic():
    assert _to_point_id("2401.1") == _to_point_id("2401.1")


def test_to_point_id_differs_per_arxiv_id():
    assert _to_point_id("a") != _to_point_id("b")


def test_exists_batch_maps_points_back_to_arxiv_ids():
    repo = _repo()
    repo._client.retrieve.return_value = [
        MagicMock(id=_to_point_id("a")),
        MagicMock(id=_to_point_id("c")),
    ]
    assert repo.exists_batch(["a", "b", "c"]) == {"a", "c"}


def test_search_maps_points_to_dicts():
    repo = _repo()
    point = MagicMock(id="x", score=0.5, payload={"arxiv_id": "a"})
    repo._client.query_points.return_value = MagicMock(points=[point])
    assert repo.search([0.0], limit=1) == [
        {"id": "x", "score": 0.5, "payload": {"arxiv_id": "a"}}
    ]
