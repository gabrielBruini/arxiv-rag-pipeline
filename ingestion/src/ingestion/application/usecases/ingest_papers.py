from pathlib import Path

from shared.domain.entities.paper import Paper

from shared.domain.interfaces.embedding_repository import EmbeddingRepository
from shared.domain.interfaces.vector_store_repository import VectorStoreRepository
from ingestion.infrastructure.readers.json_reader import read_papers

def _to_payload(paper: Paper) -> dict:
    return {
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "authors": paper.authors,
        "categories": paper.categories,
        "primary_category": paper.primary_category,
    }

class IngestPapersUseCase:

    def __init__(self, embedder: EmbeddingRepository, store: VectorStoreRepository, batch_size: int = 64):
        self._embedder = embedder
        self._store = store
        self._batch_size = batch_size

    def execute(self, file_path: str | Path) -> None:
        self._store.ensure_collection(dimension=self._embedder.dimension)

        papers = read_papers(file_path)
        print(f"Lidos {len(papers)} papers de {file_path}")

        valid = [p for p in papers if p.is_valid]
        already_indexed = self._store.exists_batch([p.arxiv_id for p in valid])
        pending = [p for p in valid if p.arxiv_id not in already_indexed]
        skipped = len(papers) - len(pending)
        print(f"{skipped} já indexados ou inválidos (pulados), {len(pending)} a processar")

        for start in range(0, len(pending), self._batch_size):
            batch = pending[start : start + self._batch_size]
            self._process_batch(batch)
            print(f"Processados {min(start + self._batch_size, len(pending))}/{len(pending)}")

    def _process_batch(self, batch: list[Paper]) -> None:
        texts = [p.to_chunk_text() for p in batch]
        vectors = self._embedder.embed_batch(texts)

        for paper, vector in zip(batch, vectors):
            self._store.upsert(paper.arxiv_id, vector, _to_payload(paper))
