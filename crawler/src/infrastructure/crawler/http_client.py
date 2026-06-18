from pathlib import Path

import requests
from shared.config import settings
from shared.logger import get_logger
from tqdm import tqdm

logger = get_logger(__name__)

class HttpClient:

    def download(self, url: str, dest: Path) -> Path:
        if dest.exists():
            logger.info(f"Arquivo já existe, pulando: {dest.name}")
            return dest

        logger.info(f"Baixando: {url}")
        response = requests.get(url, stream=True, timeout=settings.timeout)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))

        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
            for chunk in response.iter_content(chunk_size=settings.chunk_size):
                f.write(chunk)
                bar.update(len(chunk))

        return dest

    def get(self, url: str, params: dict | None = None) -> str:
        logger.info(f"GET: {url} | params={params}")
        response = requests.get(url, params=params, timeout=settings.timeout)
        response.raise_for_status()
        return response.text
