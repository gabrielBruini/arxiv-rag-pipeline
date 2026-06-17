"""
Script de teste manual para a etapa de embedding da ingestion.

Roda um Paper de exemplo pelo SentenceTransformerRepository e mostra
a dimensão e o vetor gerado, só para confirmar que a implementação
está funcionando antes de plugar no Qdrant.
"""

from shared.domain.entities.paper import Paper
from infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)


def main() -> None:
    paper = Paper(
        arxiv_id="2501.12345",
        title="Efficient Fine-Tuning of Large Language Models",
        abstract=(
            "We propose a method for efficient fine-tuning of LLMs using "
            "low-rank adaptation, reducing compute cost significantly "
            "while maintaining performance."
        ),
        authors=["Jane Doe", "John Smith"],
        categories=["cs.LG", "cs.CL"],
    )

    repo = SentenceTransformerRepository()
    print(f"Dimensão do vetor: {repo.dimension}")

    text = paper.to_chunk_text()
    print(f"\nTexto usado no embedding:\n{text}")

    vector = repo.embed(text)
    print(f"\nTamanho do vetor gerado: {len(vector)}")
    print(f"Primeiros 5 valores: {vector[:5]}")


if __name__ == "__main__":
    main()