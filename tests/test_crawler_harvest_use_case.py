from application.usecases.harvest_papers import HarvestPapersUseCase
from shared.domain.entities.paper import Paper


class FakeHarvestRepo:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def harvest_page(self, resumption_token=None, from_date=None, until_date=None):
        self.calls.append((resumption_token, from_date, until_date))
        return self.pages.pop(0)


def _paper(i):
    return Paper(arxiv_id=str(i), title="T", abstract="A")


def test_harvests_all_pages_until_no_token():
    pages = [
        ([_paper(1), _paper(2)], "tok1"),
        ([_paper(3)], None),
    ]
    papers = list(HarvestPapersUseCase(FakeHarvestRepo(pages)).execute())
    assert [p.arxiv_id for p in papers] == ["1", "2", "3"]


def test_respects_max_pages():
    pages = [
        ([_paper(1)], "tok1"),
        ([_paper(2)], "tok2"),
        ([_paper(3)], "tok3"),
    ]
    repo = FakeHarvestRepo(pages)
    papers = list(HarvestPapersUseCase(repo).execute(max_pages=2))
    assert [p.arxiv_id for p in papers] == ["1", "2"]
    assert len(repo.calls) == 2


def test_forwards_date_filters_to_repository():
    repo = FakeHarvestRepo([([_paper(1)], None)])
    list(
        HarvestPapersUseCase(repo).execute(
            from_date="2024-01-01", until_date="2024-02-01"
        )
    )
    assert repo.calls[0] == (None, "2024-01-01", "2024-02-01")


def test_execute_is_lazy():
    repo = FakeHarvestRepo([([_paper(1)], "tok1"), ([_paper(2)], None)])
    gen = HarvestPapersUseCase(repo).execute()
    assert repo.calls == []
    next(gen)
    assert len(repo.calls) == 1
