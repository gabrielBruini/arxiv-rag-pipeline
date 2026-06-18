import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from ingestion.application.usecases.ingest_papers import IngestPapersUseCase
from shared.infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)
from shared.infrastructure.vector_store.qdrant_repository import QdrantRepository

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

def _latest_crawler_output() -> Path:
    files = sorted(RAW_DATA_DIR.glob("arxiv_papers_*.json"))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo arxiv_papers_*.json encontrado em {RAW_DATA_DIR}"
        )
    return files[-1]

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingere papers do arXiv no Qdrant.")
    parser.add_argument(
        "file_path",
        nargs="?",
        type=Path,
        default=None,
        help="Caminho do JSON do crawler. Default: arquivo mais recente em ../data/raw.",
    )
    parser.add_argument(
        "--collection",
        default=os.environ.get("QDRANT_COLLECTION", "arxiv_cs_papers"),
        help="Nome da collection no Qdrant.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("QDRANT_HOST", "localhost"),
        help="Host do Qdrant.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("QDRANT_PORT", "6333")),
        help="Porta HTTP do Qdrant.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("INGEST_BATCH_SIZE", "64")),
        help="Tamanho do lote de processamento.",
    )
    return parser.parse_args()

def main() -> None:
    args = _parse_args()
    file_path = args.file_path or _latest_crawler_output()

    embedder = SentenceTransformerRepository(
        model_name=os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        device=os.environ.get("EMBEDDING_DEVICE") or None,
    )
    store = QdrantRepository(
        collection_name=args.collection, host=args.host, port=args.port
    )
    use_case = IngestPapersUseCase(embedder, store, batch_size=args.batch_size)

    use_case.execute(file_path)
    print("Ingestion concluída.")

if __name__ == "__main__":
    main()
