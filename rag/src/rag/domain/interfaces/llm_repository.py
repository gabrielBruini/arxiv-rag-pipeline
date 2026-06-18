from abc import ABC, abstractmethod

NO_ANSWER_SIGNAL = "NO_ANSWER"

class LLMRepository(ABC):

    @abstractmethod
    def generate(self, messages: list[dict[str, str]], context: str) -> str:
        raise NotImplementedError
