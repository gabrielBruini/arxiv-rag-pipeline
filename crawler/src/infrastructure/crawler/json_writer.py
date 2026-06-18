import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from shared.domain.entities.paper import Paper
from shared.logger import get_logger

logger = get_logger(__name__)


class JsonWriter:

    def write(self, papers: Iterable[Paper], dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)

        count = 0
        with open(dest, "w", encoding="utf-8") as f:
            f.write("[")
            for paper in papers:
                f.write(",\n  " if count else "\n  ")
                json.dump(asdict(paper), f, ensure_ascii=False, default=str)
                count += 1
            f.write("\n]" if count else "]")

        logger.info(f"Salvos {count} papers em {dest}")
        return dest
