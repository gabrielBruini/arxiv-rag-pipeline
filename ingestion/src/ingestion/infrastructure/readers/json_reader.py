from collections.abc import Iterator
from datetime import date
from pathlib import Path

import ijson
from shared.domain.entities.paper import Paper


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value)


def _to_paper(raw: dict) -> Paper:
    return Paper(
        arxiv_id=raw["arxiv_id"],
        title=raw["title"],
        abstract=raw["abstract"],
        authors=raw.get("authors", []),
        categories=raw.get("categories", []),
        published_date=_parse_date(raw.get("published_date")),
        updated_date=_parse_date(raw.get("updated_date")),
    )


def read_papers(file_path: str | Path) -> Iterator[Paper]:
    path = Path(file_path)
    with path.open("rb") as f:
        for raw in ijson.items(f, "item"):
            yield _to_paper(raw)
