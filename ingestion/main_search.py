"""Script de teste manual de busca semântica.

Gera o embedding de uma query em texto e busca os papers mais similares no Qdrant,
imprimindo título, categorias e score de cada resultado.

Uso:
    python main_search.py                              # usa a query default
    python main_search.py "graph neural networks"      # query custom
"""

import argparse
import os

# O modelo de embedding já está em cache local; forçamos modo offline para usar o
# cache e evitar a falha de SSL ao contatar o HuggingFace. Precisa vir antes do import
# que carrega huggingface_hub/transformers, pois a env var é lida na importação.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)
from infrastructure.vector_store.qdrant_repository import QdrantRepository

DEFAULT_QUERY = "neural networks for image classification"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Busca semântica de papers no Qdrant.")
    parser.add_argument(
        "query",
        nargs="?",
        default=DEFAULT_QUERY,
        help=f'Query em texto. Default: "{DEFAULT_QUERY}".',
    )
    parser.add_argument(
        "--collection",
        default="arxiv_cs_papers",
        help="Nome da collection no Qdrant.",
    )
    parser.add_argument("--host", default="localhost", help="Host do Qdrant.")
    parser.add_argument("--port", type=int, default=6333, help="Porta HTTP do Qdrant.")
    parser.add_argument(
        "--limit", type=int, default=5, help="Quantidade de resultados."
    )
    return parser.parse_args()


def _print_results(query: str, results: list[dict]) -> None:
    print(f'\nQuery: "{query}"')
    print(f"{len(results)} resultados (ordenados por relevância):\n")

    for rank, result in enumerate(results, start=1):
        payload = result.get("payload") or {}
        title = payload.get("title", "(sem título)")
        categories = ", ".join(payload.get("categories", [])) or "(sem categorias)"
        print(f"{rank}. [{result['score']:.4f}] {title}")
        print(f"   categorias: {categories}\n")


def main() -> None:
    args = _parse_args()

    embedder = SentenceTransformerRepository()
    store = QdrantRepository(
        collection_name=args.collection, host=args.host, port=args.port
    )

    vector = embedder.embed(args.query)
    results = store.search(vector, limit=args.limit)

    _print_results(args.query, results)


if __name__ == "__main__":
    main()
