import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    arxiv_base_url: str = os.environ.get("ARXIV_OAI_BASE_URL", "https://oaipmh.arxiv.org/oai")
    arxiv_metadata_prefix: str = os.environ.get("ARXIV_METADATA_PREFIX", "arXiv")
    arxiv_set_spec: str = os.environ.get("ARXIV_SET_SPEC", "cs")
    arxiv_request_delay: int = int(os.environ.get("ARXIV_REQUEST_DELAY", "3"))

    timeout: int = int(os.environ.get("HTTP_TIMEOUT", "120"))
    chunk_size: int = int(os.environ.get("HTTP_CHUNK_SIZE", "8192"))

settings = Settings()
