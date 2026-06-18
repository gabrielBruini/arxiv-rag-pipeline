import json
from pathlib import Path
from dataclasses import asdict
from shared.domain.entities.paper import Paper
from shared.logger import get_logger

logger = get_logger(__name__)

class JsonWriter:

    def write(self, papers: list[Paper], dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(paper) for paper in papers]

        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"Salvos {len(papers)} papers em {dest}")
        return dest
