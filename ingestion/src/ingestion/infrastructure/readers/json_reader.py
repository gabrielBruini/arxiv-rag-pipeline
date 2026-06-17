import json
from datetime import date
from pathlib import Path

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


def read_papers(file_path: str | Path) -> list[Paper]:
    """
    Lê o arquivo JSON (array de objetos) gerado pelo crawler do arXiv
    e retorna a lista de Paper já desserializada.
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        raw_items = json.load(f)

    return [_to_paper(item) for item in raw_items]