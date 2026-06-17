from abc import ABC, abstractmethod
from domain.entities.dataset import Dataset

class CrawlerRepository(ABC):

    @abstractmethod
    def build_url(self, dataset: Dataset) -> str:
        ...

    @abstractmethod
    def download(self, dataset: Dataset) -> Dataset:
        ...

    @abstractmethod
    def extract(self, dataset: Dataset) -> Dataset:
        ...