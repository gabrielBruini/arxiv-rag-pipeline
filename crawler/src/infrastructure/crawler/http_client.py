from pathlib import Path

import requests
from shared.config import settings
from shared.logger import get_logger
from tqdm import tqdm

logger = get_logger(__name__)

class HttpClient:

    def get(self, url: str, params: dict | None = None) -> str:
        logger.info(f"GET: {url} | params={params}")
        response = requests.get(url, params=params, timeout=settings.timeout)
        response.raise_for_status()
        return response.text
