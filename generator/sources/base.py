from abc import ABC, abstractmethod


class DocumentSource(ABC):

    @abstractmethod
    def fetch(self, query: str) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
