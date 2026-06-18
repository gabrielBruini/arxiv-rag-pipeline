from abc import ABC, abstractmethod


class SessionStore(ABC):

    @abstractmethod
    def get_history(self, session_id: str) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def append_message(self, session_id: str, role: str, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_healthy(self) -> bool:
        raise NotImplementedError
