from src.core.vector import Vec3


class Triangle:
    """Треугольник TIN + пересечение с лучом."""

    def __init__(self, a: Vec3, b: Vec3, c: Vec3):
        self.a, self.b, self.c = a, b, c
        self.normal = (b - a).cross(c - a).normalized()

    def bbox_xy(self):
        xs = (self.a.x, self.b.x, self.c.x)
        ys = (self.a.y, self.b.y, self.c.y)
        return (min(xs), min(ys), max(xs), max(ys))

    def contains_xy(self, x: float, y: float) -> bool:
        """Проекция точки на XY внутри треугольника (барицентрика)."""
        v0 = self.b - self.a
        v1 = self.c - self.a
        v2 = Vec3(x - self.a.x, y - self.a.y, 0.0)
        den = v0.x * v1.y - v1.x * v0.y
        if abs(den) < 1e-12:
            return False
        u = (v2.x * v1.y - v1.x * v2.y) / den
        v = (v0.x * v2.y - v2.x * v0.y) / den
        return u >= 0 and v >= 0 and (u + v) <= 1

    def elevation_at_xy(self, x: float, y: float) -> float:
        """Высота z внутри треугольника (барицентрика)."""
        v0 = self.b - self.a
        v1 = self.c - self.a
        v2 = Vec3(x - self.a.x, y - self.a.y, 0.0)
        den = v0.x * v1.y - v1.x * v0.y
        if abs(den) < 1e-12:
            return self.a.z
        u = (v2.x * v1.y - v1.x * v2.y) / den
        v = (v0.x * v2.y - v2.x * v0.y) / den
        w = 1 - u - v
        return w * self.a.z + u * self.b.z + v * self.c.z

    def intersect_ray(self, origin: Vec3, direction: Vec3):
        """Möller–Trumbore. Возвращает t или None."""
        eps = 1e-9
        e1 = self.b - self.a
        e2 = self.c - self.a
        pvec = direction.cross(e2)
        det = e1.dot(pvec)
        if abs(det) < eps:
            return None
        inv_det = 1.0 / det
        tvec = origin - self.a
        u = tvec.dot(pvec) * inv_det
        if u < 0 or u > 1:
            return None
        qvec = tvec.cross(e1)
        v = direction.dot(qvec) * inv_det
        if v < 0 or u + v > 1:
            return None
        t = e2.dot(qvec) * inv_det
        return t if t > eps else None