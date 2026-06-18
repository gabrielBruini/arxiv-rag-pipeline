import json

from ingestion.application.usecases.ingest_papers import IngestPapersUseCase


class FakeEmbedder:
    dimension = 384

    def embed(self, text):
        return [0.0] * self.dimension

    def embed_batch(self, texts):
        return [[0.0] * self.dimension for _ in texts]


class FakeStore:
    def __init__(self, already=None):
        self.ensured_dim = None
        self.already = set(already or [])
        self.upserts = []

    def ensure_collection(self, dimension):
        self.ensured_dim = dimension

    def exists_batch(self, point_ids):
        return {pid for pid in point_ids if pid in self.already}

    def upsert(self, point_id, vector, payload):
        self.upserts.append((point_id, payload))

    def search(self, vector, limit=5):
        return []


def _write(tmp_path, items):
    f = tmp_path / "papers.json"
    f.write_text(json.dumps(items), encoding="utf-8")
    return f


def test_ensure_collection_called_with_embedder_dimension(tmp_path):
    store = FakeStore()
    IngestPapersUseCase(FakeEmbedder(), store).execute(_write(tmp_path, []))
    assert store.ensured_dim == 384


def test_skips_invalid_and_indexes_valid(tmp_path):
    items = [
        {"arxiv_id": "ok", "title": "T", "abstract": "A"},
        {"arxiv_id": "bad", "title": "", "abstract": ""},
    ]
    store = FakeStore()
    IngestPapersUseCase(FakeEmbedder(), store).execute(_write(tmp_path, items))
    assert [pid for pid, _ in store.upserts] == ["ok"]


def test_dedup_skips_already_indexed(tmp_path):
    items = [
        {"arxiv_id": "a", "title": "T", "abstract": "A"},
        {"arxiv_id": "b", "title": "T", "abstract": "A"},
    ]
    store = FakeStore(already={"a"})
    IngestPapersUseCase(FakeEmbedder(), store).execute(_write(tmp_path, items))
    assert [pid for pid, _ in store.upserts] == ["b"]


def test_payload_has_expected_fields(tmp_path):
    items = [{"arxiv_id": "a", "title": "T", "abstract": "A", "categories": ["cs.AI"]}]
    store = FakeStore()
    IngestPapersUseCase(FakeEmbedder(), store).execute(_write(tmp_path, items))
    _, payload = store.upserts[0]
    assert payload["arxiv_id"] == "a"
    assert payload["primary_category"] == "cs.AI"


def test_batching_processes_all_pending(tmp_path):
    items = [{"arxiv_id": str(i), "title": "T", "abstract": "A"} for i in range(10)]
    store = FakeStore()
    IngestPapersUseCase(FakeEmbedder(), store, batch_size=3).execute(_write(tmp_path, items))
    assert len(store.upserts) == 10
