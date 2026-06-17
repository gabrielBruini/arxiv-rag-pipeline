from domain.entities.dataset import Dataset
from domain.interfaces.crawler_repository import CrawlerRepository
from shared.logger import get_logger

logger = get_logger(__name__)

class CrawlDatasetUseCase:

    def __init__(self, repository: CrawlerRepository):
        self.repository = repository

    def execute(self, year: int, month: int, dataset_type: str) -> Dataset:
        dataset = Dataset(year=year, month=month, dataset_type=dataset_type)

        logger.info(f"Baixando {dataset.reference} - {dataset_type}")
        dataset = self.repository.download(dataset)

        logger.info(f"Extraindo {dataset.zip_path.name}")
        dataset = self.repository.extract(dataset)

        logger.info(f"Concluído: {len(dataset.csv_paths)} CSVs extraídos")
        return dataset