from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task
from airflow.models.param import Param


@dag(
    dag_id="arxiv_harvester",
    schedule="0 3 * * 1",  # Toda segunda às 3h
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["crawler", "arxiv", "cs"],
    params={
        "max_pages": Param(
            default=1,
            type="integer",
            minimum=1,
            description="Número máximo de páginas OAI-PMH a coletar.",
        ),
    },
)
def arxiv_harvester():

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
        use_case = HarvestPapersUseCase(repo)
        papers = use_case.execute(max_pages=params["max_pages"])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = Path("/opt/airflow/data/raw") / f"arxiv_papers_{timestamp}.json"
        JsonWriter().write(papers, dest)

        return str(dest)

    harvest()


arxiv_harvester()
