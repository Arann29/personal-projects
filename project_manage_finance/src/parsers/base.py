from abc import ABC, abstractmethod
from datetime import datetime


class EmailParser(ABC):
    @abstractmethod
    def parse(self, email_content: str) -> tuple[datetime, float] | None:
        raise NotImplementedError
