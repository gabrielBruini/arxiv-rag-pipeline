import time

from domain.interfaces.harvest_repository import HarvestRepository
from infrastructure.crawler.http_client import HttpClient
from lxml import etree
from shared.config import settings
from shared.domain.entities.paper import Paper
from shared.logger import get_logger

logger = get_logger(__name__)

NAMESPACES = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "arxiv": "http://arxiv.org/OAI/arXiv/",
}

class ArxivRepository(HarvestRepository):

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.base_url = settings.arxiv_base_url
        self.metadata_prefix = settings.arxiv_metadata_prefix
        self.set_spec = settings.arxiv_set_spec
        self.request_delay = settings.arxiv_request_delay

    def harvest_page(
        self,
        resumption_token: str | None = None,
        from_date: str | None = None,
        until_date: str | None = None,
    ) -> tuple[list[Paper], str | None]:
        params = self._build_params(resumption_token, from_date, until_date)

        time.sleep(self.request_delay)
        response_xml = self.http_client.get(self.base_url, params=params)

        root = etree.fromstring(response_xml.encode("utf-8"))
        papers = self._parse_records(root)
        next_token = self._extract_resumption_token(root)

        return papers, next_token

    def _build_params(
        self,
        resumption_token: str | None,
        from_date: str | None = None,
        until_date: str | None = None,
    ) -> dict:
        if resumption_token:
            return {"verb": "ListRecords", "resumptionToken": resumption_token}

        params = {
            "verb": "ListRecords",
            "metadataPrefix": self.metadata_prefix,
            "set": self.set_spec,
        }
        if from_date:
            params["from"] = from_date
        if until_date:
            params["until"] = until_date
        return params

    def _parse_records(self, root: etree._Element) -> list[Paper]:
        papers = []
        records = root.findall(".//oai:record", NAMESPACES)

        for record in records:
            paper = self._parse_record(record)
            if paper and paper.is_valid:
                papers.append(paper)

        logger.info(f"{len(papers)} papers parseados nesta página")
        return papers

    def _parse_record(self, record: etree._Element) -> Paper | None:
        try:
            metadata = record.find(".//arxiv:arXiv", NAMESPACES)
            if metadata is None:
                return None

            arxiv_id = self._get_text(metadata, "arxiv:id")
            title = self._get_text(metadata, "arxiv:title")
            abstract = self._get_text(metadata, "arxiv:abstract")

            authors = [
                self._get_text(author, "arxiv:keyname", default="")
                for author in metadata.findall(".//arxiv:author", NAMESPACES)
            ]

            categories_raw = self._get_text(metadata, "arxiv:categories", default="")
            categories = categories_raw.split() if categories_raw else []

            return Paper(
                arxiv_id=arxiv_id,
                title=title.strip() if title else "",
                abstract=abstract.strip() if abstract else "",
                authors=[a for a in authors if a],
                categories=categories,
            )

        except (AttributeError, ValueError) as e:
            logger.warning(f"Erro ao parsear record: {e}")
            return None

    def _get_text(self, element: etree._Element, xpath: str, default: str = "") -> str:
        found = element.find(xpath, NAMESPACES)
        return found.text if found is not None and found.text else default

    def _extract_resumption_token(self, root: etree._Element) -> str | None:
        token_el = root.find(".//oai:resumptionToken", NAMESPACES)
        if token_el is not None and token_el.text:
            return token_el.text.strip()
        return None
