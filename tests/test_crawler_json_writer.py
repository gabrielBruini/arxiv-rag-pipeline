import json

from infrastructure.crawler.json_writer import JsonWriter
from shared.domain.entities.paper import Paper


def _papers(n):
    for i in range(n):
        yield Paper(arxiv_id=str(i), title=f"T{i}", abstract="A", categories=["cs.AI"])


def test_write_streams_generator_to_valid_json(tmp_path):
    dest = tmp_path / "out.json"
    JsonWriter().write(_papers(3), dest)
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert len(data) == 3
    assert data[0]["arxiv_id"] == "0"
    assert data[2]["categories"] == ["cs.AI"]


def test_write_empty_iterable_produces_empty_array(tmp_path):
    dest = tmp_path / "empty.json"
    JsonWriter().write(iter([]), dest)
    assert json.loads(dest.read_text(encoding="utf-8")) == []
