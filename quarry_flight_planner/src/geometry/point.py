from src.geometry.shape import Shape
from src.core.vector import Vec3


class Point(Shape):
    def __init__(self, position: Vec3):
        self.position = position

    def vertices(self) -> list[Vec3]:
        return [self.position]

    def bbox(self):
        p = self.position
        return (p.x, p.y, p.x, p.y)