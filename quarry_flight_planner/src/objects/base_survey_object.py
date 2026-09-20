from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.core.base_entity import BaseEntity
from src.geometry.shape import Shape
from src.geometry.polygon import Polygon


@dataclass
class BaseSurveyObject(BaseEntity, ABC):
    """ABC объекта съёмки. Все поля имеют дефолты, чтобы наследники
    (PointObject, LinearObject, ArealObject) не конфликтовали с BaseEntity."""
    geometry: Shape = None
    buffer_m: float = 20.0

    @abstractmethod
    def survey_polygon(self) -> Polygon:
        ...

    def describe(self) -> str:
        return f"{self.__class__.__name__} '{self.name}', буфер {self.buffer_m} м"