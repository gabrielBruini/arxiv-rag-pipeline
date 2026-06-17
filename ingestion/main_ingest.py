"""Entry-point do pipeline de ingestion.

Lê o JSON gerado pelo crawler (array de objetos), gera embeddings e faz upsert
no Qdrant via IngestPapersUseCase.

Uso:
    python main_ingest.py                      # usa o JSON mais recente em ../crawler/data/raw
    python main_ingest.py caminho/para/arquivo.json
"""

import argparse
import os
from pathlib import Path

# O modelo de embedding já está em cache local; forçamos modo offline para usar o
# cache e evitar a falha de SSL ao contatar o HuggingFace. Precisa vir antes do import
# que carrega huggingface_hub/transformers, pois a env var é lida na importação.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from application.usecases.ingest_papers import IngestPapersUseCase
from infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)
from infrastructure.vector_store.qdrant_repository import QdrantRepository

CRAWLER_RAW_DIR = Path(__file__).resolve().parent.parent / "crawler" / "data" / "raw"


def _latest_crawler_output() -> Path:
    files = sorted(CRAWLER_RAW_DIR.glob("arxiv_papers_*.json"))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo arxiv_papers_*.json encontrado em {CRAWLER_RAW_DIR}"
        )
    return files[-1]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingere papers do arXiv no Qdrant.")
    parser.add_argument(
        "file_path",
        nargs="?",
        type=Path,
        default=None,
        help="Caminho do JSON do crawler. Default: arquivo mais recente em ../crawler/data/raw.",
    )
    parser.add_argument(
        "--collection",
        default="arxiv_cs_papers",
        help="Nome da collection no Qdrant.",
    )
    parser.add_argument(
        "--host", default="localhost", help="Host do Qdrant."
    )
    parser.add_argument(
        "--port", type=int, default=6333, help="Porta HTTP do Qdrant."
    )
    parser.add_argument(
        "--batch-size", type=int, default=64, help="Tamanho do lote de processamento."
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    file_path = args.file_path or _latest_crawler_output()

    embedder = SentenceTransformerRepository()
    store = QdrantRepository(
        collection_name=args.collection, host=args.host, port=args.port
    )
    use_case = IngestPapersUseCase(embedder, store, batch_size=args.batch_size)

    use_case.execute(file_path)
    print("Ingestion concluída.")


if __name__ == "__main__":
    main()
