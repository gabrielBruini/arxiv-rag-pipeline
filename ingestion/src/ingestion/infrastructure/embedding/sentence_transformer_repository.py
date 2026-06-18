from sentence_transformers import SentenceTransformer

from ingestion.domain.interfaces.embedding_repository import EmbeddingRepository

class SentenceTransformerRepository(EmbeddingRepository):

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        local_files_only: bool = False,
    ):
        self._model = self._load_model(model_name, device, local_files_only)
        self._dimension = self._model.get_sentence_embedding_dimension()

    @staticmethod
    def _load_model(
        model_name: str, device: str | None, local_files_only: bool
    ) -> SentenceTransformer:
        if local_files_only:
            return SentenceTransformer(model_name, device=device, local_files_only=True)
        try:
            return SentenceTransformer(model_name, device=device, local_files_only=True)
        except Exception:
            return SentenceTransformer(model_name, device=device, local_files_only=False)

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
