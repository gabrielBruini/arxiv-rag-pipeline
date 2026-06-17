from pathlib import Path
from dataclasses import dataclass

@dataclass
class Settings:
    BASE_URL: str = "https://portaldatransparencia.gov.br/download-de-dados/servidores"
    RAW_DATA_DIR: Path = Path("data/raw")
    TIMEOUT: int = 120
    CHUNK_SIZE: int = 8192
    # Zips de placeholder/vazios do portal vêm com ~1,5 KB; os reais têm dezenas de MB.
    MIN_DOWNLOAD_SIZE: int = 10_240  # 10 KB

    def __post_init__(self):
        self.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()