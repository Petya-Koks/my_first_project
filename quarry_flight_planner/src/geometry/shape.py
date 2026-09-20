from abc import ABC, abstractmethod
from src.core.vector import Vec3


class Shape(ABC):
    """Абстрактная геометрическая фигура."""

    @abstractmethod
    def vertices(self) -> list[Vec3]:
        ...

    @abstractmethod
    def bbox(self) -> tuple[float, float, float, float]:
        ...

    def centroid(self) -> Vec3:
        vs = self.vertices()
        n = len(vs)
        if n == 0:
            return Vec3()
        return Vec3(
            sum(v.x for v in vs) / n,
            sum(v.y for v in vs) / n,
            sum(v.z for v in vs) / n,
        )

    def describe(self) -> str:
        return f"{self.__class__.__name__} ({len(self.vertices())} вершин)"