import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.crawler.http_client import HttpClient
from infrastructure.crawler.arxiv_repository import ArxivRepository
from infrastructure.crawler.json_writer import JsonWriter
from application.usecases.harvest_papers import HarvestPapersUseCase

if __name__ == "__main__":
    max_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    repo = ArxivRepository(HttpClient())
    use_case = HarvestPapersUseCase(repo)

    papers = use_case.execute(max_pages=max_pages)

    print(f"\nTotal de papers coletados: {len(papers)}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path("data/raw") / f"arxiv_papers_{timestamp}.json"

    writer = JsonWriter()
    writer.write(papers, dest)

    print(f"Arquivo salvo em: {dest}")