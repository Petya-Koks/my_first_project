from src.geometry.polyline import Polyline
from src.core.vector import Vec3


class Polygon(Polyline):
    """Замкнутая полилиния + простые операции (площадь, contains)."""

    def __init__(self, points: list[Vec3]):
        super().__init__(points, closed=True)

    def area(self) -> float:
        """Площадь через формулу шнуровки (проекция на XY)."""
        s = 0.0
        pts = self.points
        for a, b in zip(pts[:-1], pts[1:]):
            s += a.x * b.y - b.x * a.y
        return abs(s) / 2.0

    def contains_xy(self, x: float, y: float) -> bool:
        """Метод трассировки луча (ray casting) для точки в полигоне."""
        inside = False
        pts = self.points
        n = len(pts) - 1  # последняя = первой
        j = n - 1
        for i in range(n):
            xi, yi = pts[i].x, pts[i].y
            xj, yj = pts[j].x, pts[j].y
            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
                inside = not inside
            j = i
        return inside

    def buffer_2d(self, distance: float) -> "Polygon":
        """Упрощённый буфер: смещаем вершины наружу от центроида."""
        c = self.centroid()
        new_pts = []
        for p in self.points[:-1]:  # без дубля последней
            dx, dy = p.x - c.x, p.y - c.y
            d = (dx * dx + dy * dy) ** 0.5
            if d > 1e-9:
                k = (d + distance) / d
                new_pts.append(Vec3(c.x + dx * k, c.y + dy * k, p.z))
            else:
                new_pts.append(p)
        return Polygon(new_pts)