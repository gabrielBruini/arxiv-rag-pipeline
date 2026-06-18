from abc import ABC, abstractmethod

from shared.domain.entities.paper import Paper


class HarvestRepository(ABC):

    @abstractmethod
    def harvest_page(
        self,
        resumption_token: str | None = None,
        from_date: str | None = None,
        until_date: str | None = None,
    ) -> tuple[list[Paper], str | None]:
        ...
