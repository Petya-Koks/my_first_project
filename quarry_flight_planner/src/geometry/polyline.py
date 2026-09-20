from src.geometry.line import Line
from src.core.vector import Vec3


class Polyline(Line):
    def __init__(self, points: list[Vec3], closed: bool = False):
        if len(points) < 2:
            raise ValueError("Polyline требует минимум 2 точки")
        self.points = list(points)
        self.closed = closed
        if closed and self.points[0] != self.points[-1]:
            self.points.append(self.points[0])

    def vertices(self) -> list[Vec3]:
        return list(self.points)

    def bbox(self):
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))

    def length(self) -> float:
        return sum((b - a).length() for a, b in zip(self.points[:-1], self.points[1:]))

    def point_at(self, t: float) -> Vec3:
        total = self.length()
        target = t * total
        acc = 0.0
        for a, b in zip(self.points[:-1], self.points[1:]):
            seg_len = (b - a).length()
            if acc + seg_len >= target:
                local_t = (target - acc) / seg_len if seg_len > 0 else 0
                return a + (b - a) * local_t
            acc += seg_len
        return self.points[-1]