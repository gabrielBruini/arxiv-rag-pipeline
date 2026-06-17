from abc import ABC, abstractmethod
from domain.entities.paper import Paper

class HarvestRepository(ABC):
    """
    Contrato para fontes de dados que usam paginação via token
    (ao invés de download de arquivo único, como o CrawlerRepository).
    """

    @abstractmethod
    def harvest_page(self, resumption_token: str | None = None) -> tuple[list[Paper], str | None]:
        """
        Busca uma página de resultados.

        Args:
            resumption_token: token da página anterior (None = primeira página)

        Returns:
            (lista de papers da página, próximo resumption_token ou None se acabou)
        """
        ...