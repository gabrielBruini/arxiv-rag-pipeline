from collections.abc import Iterable, Iterator
from pathlib import Path

from ingestion.infrastructure.readers.json_reader import read_papers
from shared.domain.entities.paper import Paper
from shared.domain.interfaces.embedding_repository import EmbeddingRepository
from shared.domain.interfaces.vector_store_repository import VectorStoreRepository
from shared.logger import get_logger

logger = get_logger(__name__)


def _to_payload(paper: Paper) -> dict:
    return {
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "authors": paper.authors,
        "categories": paper.categories,
        "primary_category": paper.primary_category,
    }


def _batched(items: Iterable[Paper], size: int) -> Iterator[list[Paper]]:
    batch: list[Paper] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


class IngestPapersUseCase:

    def __init__(
        self, embedder: EmbeddingRepository, store: VectorStoreRepository, batch_size: int = 64
    ):
        self._embedder = embedder
        self._store = store
        self._batch_size = batch_size

    def execute(self, file_path: str | Path) -> None:
        self._store.ensure_collection(dimension=self._embedder.dimension)

        total = 0
        indexed = 0
        skipped = 0
        for batch in _batched(read_papers(file_path), self._batch_size):
            total += len(batch)
            valid = [p for p in batch if p.is_valid]
            already_indexed = self._store.exists_batch([p.arxiv_id for p in valid])
            pending = [p for p in valid if p.arxiv_id not in already_indexed]
            skipped += len(batch) - len(pending)
            if pending:
                self._process_batch(pending)
                indexed += len(pending)
            logger.info(f"Processados {total} (indexados {indexed}, pulados {skipped})")

    def _process_batch(self, batch: list[Paper]) -> None:
        texts = [p.to_chunk_text() for p in batch]
        vectors = self._embedder.embed_batch(texts)

        for paper, vector in zip(batch, vectors, strict=True):
            self._store.upsert(paper.arxiv_id, vector, _to_payload(paper))
