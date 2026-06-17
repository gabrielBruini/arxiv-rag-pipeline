
from dataclasses import dataclass, field
from datetime import datetime

from anyio import Path;


@dataclass
class Dataset:
    year: int
    month: int
    dataset_type: str
    zip_path: Path | None = None
    csv_paths: list[Path] = field(default_factory=list) # type: ignore
    downloaded_at: datetime | None = None

    @property
    def reference(self) -> str:
        return f"{self.year}{self.month:02d}"
    
    @property
    def is_downloaded(self) -> bool:
        return self.zip_path is not None and self.zip_path.exists() # type: ignore