from dataclasses import dataclass, field
from datetime import date

@dataclass
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    published_date: date | None = None
    updated_date: date | None = None

    @property
    def is_valid(self) -> bool:
        return bool(self.title and self.abstract)

    @property
    def primary_category(self) -> str | None:
        return self.categories[0] if self.categories else None

    def to_chunk_text(self) -> str:
        """Monta o texto que vai ser usado para embedding/RAG."""
        parts = [
            f"Título: {self.title}",
            f"Categorias: {', '.join(self.categories)}",
            f"Autores: {', '.join(self.authors)}",
            f"Abstract: {self.abstract.strip()}",
        ]
        return " | ".join(parts)