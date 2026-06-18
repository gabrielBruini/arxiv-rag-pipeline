from unittest.mock import MagicMock, patch

import pytest
from qdrant_client.models import Distance, VectorParams
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


def test_is_healthy_true_when_client_responds():
    repo = _repo()
    repo._client.get_collections.return_value = MagicMock()
    assert repo.is_healthy() is True


def test_is_healthy_false_on_error():
    repo = _repo()
    repo._client.get_collections.side_effect = Exception("down")
    assert repo.is_healthy() is False


def test_ensure_collection_creates_when_absent():
    repo = _repo()
    repo._client.collection_exists.return_value = False
    repo.ensure_collection(384)
    repo._client.create_collection.assert_called_once()


def test_ensure_collection_ok_when_dimension_matches():
    repo = _repo()
    repo._client.collection_exists.return_value = True
    repo._client.get_collection.return_value.config.params.vectors = VectorParams(
        size=384, distance=Distance.COSINE
    )
    repo.ensure_collection(384)
    repo._client.create_collection.assert_not_called()


def test_ensure_collection_raises_on_dimension_mismatch():
    repo = _repo()
    repo._client.collection_exists.return_value = True
    repo._client.get_collection.return_value.config.params.vectors = VectorParams(
        size=384, distance=Distance.COSINE
    )
    with pytest.raises(ValueError, match="dimension"):
        repo.ensure_collection(768)
