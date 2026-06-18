import json
from collections.abc import Iterator

from ingestion.infrastructure.readers.json_reader import read_papers


def test_read_papers_is_a_lazy_iterator(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps([{"arxiv_id": "1", "title": "T", "abstract": "A"}]), encoding="utf-8")
    result = read_papers(f)
    assert isinstance(result, Iterator)


def test_read_papers_parses_fields_and_dates(tmp_path):
    data = [
        {
            "arxiv_id": "2401.1",
            "title": "T",
            "abstract": "A",
            "authors": ["Doe"],
            "categories": ["cs.AI"],
            "published_date": "2024-01-15",
            "updated_date": None,
        }
    ]
    f = tmp_path / "papers.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    papers = list(read_papers(f))

    assert len(papers) == 1
    p = papers[0]
    assert p.arxiv_id == "2401.1"
    assert p.authors == ["Doe"]
    assert p.published_date is not None and p.published_date.year == 2024
    assert p.updated_date is None


def test_read_papers_defaults_missing_optional_fields(tmp_path):
    data = [{"arxiv_id": "1", "title": "T", "abstract": "A"}]
    f = tmp_path / "p.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    p = list(read_papers(f))[0]

    assert p.authors == []
    assert p.categories == []
    assert p.published_date is None
