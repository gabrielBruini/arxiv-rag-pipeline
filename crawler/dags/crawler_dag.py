from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task
from airflow.models.param import Param

@dag(
    dag_id="arxiv_pipeline",
    schedule="0 3 * * 1",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["arxiv", "rag", "cs"],
    params={
        "max_pages": Param(
            default=1,
            type="integer",
            minimum=1,
            description="Número máximo de páginas OAI-PMH a coletar.",
        ),
    },
)
def arxiv_pipeline():

    @task
    def harvest(params: dict) -> str:
        import sys
        from datetime import datetime
        from pathlib import Path

        sys.path.insert(0, "/opt/airflow/src")

        from application.usecases.harvest_papers import HarvestPapersUseCase
        from infrastructure.crawler.arxiv_repository import ArxivRepository
        from infrastructure.crawler.http_client import HttpClient
        from infrastructure.crawler.json_writer import JsonWriter

        repo = ArxivRepository(HttpClient())
        papers = HarvestPapersUseCase(repo).execute(max_pages=params["max_pages"])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = Path("/opt/airflow/data/raw") / f"arxiv_papers_{timestamp}.json"
        JsonWriter().write(papers, dest)

        return str(dest)

    @task
    def ingest(json_path: str | None = None) -> None:
        import os
        from pathlib import Path

        from ingestion.application.usecases.ingest_papers import IngestPapersUseCase
        from shared.infrastructure.embedding.sentence_transformer_repository import (
            SentenceTransformerRepository,
        )
        from shared.infrastructure.vector_store.qdrant_repository import (
            QdrantRepository,
        )

        if not json_path:
            raw_dir = Path("/opt/airflow/data/raw")
            files = sorted(raw_dir.glob("arxiv_papers_*.json"))
            if not files:
                raise FileNotFoundError(
                    f"Sem caminho vindo da harvest e nenhum JSON em {raw_dir}. "
                    "Rode a DAG inteira (harvest -> ingest)."
                )
            json_path = str(files[-1])

        embedder = SentenceTransformerRepository(
            model_name=os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            device=os.environ.get("EMBEDDING_DEVICE") or None,
        )
        store = QdrantRepository(
            collection_name=os.environ.get("QDRANT_COLLECTION", "arxiv_cs_papers"),
            host=os.environ.get("QDRANT_HOST", "qdrant"),
            port=int(os.environ.get("QDRANT_PORT", "6333")),
        )
        use_case = IngestPapersUseCase(
            embedder, store, batch_size=int(os.environ.get("INGEST_BATCH_SIZE", "64"))
        )
        use_case.execute(json_path)

    ingest(harvest())

arxiv_pipeline()
