from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.core.base_entity import BaseEntity


@dataclass
class BaseTerrain(BaseEntity, ABC):
    """Абстрактная поверхность (DEM, TIN, плоскость)."""

    @abstractmethod
    def elevation_at(self, x: float, y: float) -> float:
        """Высота поверхности в точке (x, y)."""
        ...

    @abstractmethod
    def bounds(self) -> tuple[float, float, float, float]:
        """Границы (minx, miny, maxx, maxy)."""
        ...

    def describe(self) -> str:
        b = self.bounds()
        return f"Рельеф '{self.name}', границы: {b}"