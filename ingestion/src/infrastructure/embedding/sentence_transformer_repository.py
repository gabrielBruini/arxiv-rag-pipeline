from sentence_transformers import SentenceTransformer

from domain.interfaces.embedding_repository import EmbeddingRepository


class SentenceTransformerRepository(EmbeddingRepository):
    """Implementação do EmbeddingRepository usando sentence-transformers (modelo local)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str | None = None):
        self._model = SentenceTransformer(model_name, device=device)
        self._dimension = self._model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> list[float]:
        vector = self._model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            batch_size=32,
        )
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        return self._dimension