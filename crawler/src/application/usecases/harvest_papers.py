from shared.entities.paper import Paper
from domain.interfaces.harvest_repository import HarvestRepository
from shared.logger import get_logger

logger = get_logger(__name__)


class HarvestPapersUseCase:
    """
    Orquestra o harvesting paginado de papers, percorrendo
    todas as páginas via resumptionToken até não haver mais.
    """

    def __init__(self, repository: HarvestRepository):
        self.repository = repository

    def execute(self, max_pages: int | None = None) -> list[Paper]:
        all_papers: list[Paper] = []
        resumption_token: str | None = None
        page_count = 0

        while True:
            page_count += 1
            logger.info(f"Buscando página {page_count}...")

            papers, resumption_token = self.repository.harvest_page(resumption_token)
            all_papers.extend(papers)

            logger.info(f"Total acumulado: {len(all_papers)} papers")

            if not resumption_token:
                logger.info("Harvesting concluído — sem mais páginas.")
                break

            if max_pages and page_count >= max_pages:
                logger.info(f"Limite de {max_pages} páginas atingido.")
                break

        return all_papers