from __future__ import annotations

from datetime import datetime
from airflow.decorators import dag, task
from airflow.models.param import Param

@dag(
    dag_id="crawler_portal_transparencia",
    schedule="0 3 * * 1",  # Toda segunda às 3h
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["crawler", "governo", "siape"],
    params={
        "year": Param(default=2026, type="integer", description="Ano de referência"),
        "month": Param(default=4, type="integer", minimum=1, maximum=12, description="Mês de referência (portal publica com ~2 meses de atraso)"),
        "dataset_type": Param(default="Servidores_SIAPE", type="string", description="Tipo do dataset"),
    },
)
def crawler_dag():

    @task
    def crawl(params: dict = None) -> list[str]:
        import sys
        sys.path.insert(0, "/opt/airflow/src")

        from infrastructure.crawler.http_client import HttpClient
        from infrastructure.crawler.zip_extractor import ZipExtractor
        from infrastructure.crawler.portal_repository import PortalTransparenciaRepository
        from application.usecases.crawl_dataset import CrawlDatasetUseCase

        repo = PortalTransparenciaRepository(HttpClient(), ZipExtractor())
        use_case = CrawlDatasetUseCase(repo)

        dataset = use_case.execute(
            year=params["year"],
            month=params["month"],
            dataset_type=params["dataset_type"],
        )

        return [str(p) for p in dataset.csv_paths]

    crawl()

crawler_dag()