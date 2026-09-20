from abc import abstractmethod
from src.geometry.shape import Shape
from src.core.vector import Vec3

class Line(Shape):
    """Абстрактная линия (общий предок Segment и Polyline)."""

    @abstractmethod
    def length(self) -> float:
        ...

    @abstractmethod
    def point_at(self, t: float) -> "Vec3":
        """Точка на линии, t ∈ [0, 1] вдоль всей длины."""
        ...