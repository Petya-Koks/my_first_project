from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime


@dataclass
class BaseEntity(ABC):
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)

    @abstractmethod
    def describe(self) -> str:
        ...