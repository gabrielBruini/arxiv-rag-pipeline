from application.usecases.harvest_papers import HarvestPapersUseCase
from shared.domain.entities.paper import Paper


class FakeHarvestRepo:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = 0

    def harvest_page(self, resumption_token=None):
        self.calls += 1
        return self.pages.pop(0)


def _paper(i):
    return Paper(arxiv_id=str(i), title="T", abstract="A")


def test_harvests_all_pages_until_no_token():
    pages = [
        ([_paper(1), _paper(2)], "tok1"),
        ([_paper(3)], None),
    ]
    papers = HarvestPapersUseCase(FakeHarvestRepo(pages)).execute()
    assert [p.arxiv_id for p in papers] == ["1", "2", "3"]


def test_respects_max_pages():
    pages = [
        ([_paper(1)], "tok1"),
        ([_paper(2)], "tok2"),
        ([_paper(3)], "tok3"),
    ]
    repo = FakeHarvestRepo(pages)
    papers = HarvestPapersUseCase(repo).execute(max_pages=2)
    assert [p.arxiv_id for p in papers] == ["1", "2"]
    assert repo.calls == 2
