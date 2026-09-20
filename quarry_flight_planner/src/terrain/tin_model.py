from dataclasses import dataclass, field
from src.terrain.base_terrain import BaseTerrain
from src.terrain.triangle import Triangle
from src.core.vector import Vec3


@dataclass
class TINModel(BaseTerrain):
    points: list[Vec3] = field(default_factory=list)
    rows: int = 0
    cols: int = 0
    _triangles: list[Triangle] = field(default_factory=list, init=False, repr=False)
    _bbox: tuple = field(default=None, init=False)

    def __post_init__(self):
        if self.points:
            self._build()

    def _build(self):
        pts = self.points
        for r in range(self.rows - 1):
            for c in range(self.cols - 1):
                i = r * self.cols + c
                a = pts[i]
                b = pts[i + 1]
                cc = pts[i + self.cols]
                d = pts[i + self.cols + 1]
                self._triangles.append(Triangle(a, b, d))
                self._triangles.append(Triangle(a, d, cc))
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        self._bbox = (min(xs), min(ys), max(xs), max(ys))

    def elevation_at(self, x: float, y: float) -> float:
      # 1) точное попадание в треугольник
        for tri in self._triangles:
            if tri.contains_xy(x, y):
                return tri.elevation_at_xy(x, y)
        # 2) если точка вне TIN или между треугольниками —
        #    берём ближайшую вершину
        best_d2 = None
        best_z = float("nan")
        for p in self.points:
            dx = p.x - x
            dy = p.y - y
            d2 = dx * dx + dy * dy
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                best_z = p.z
        return best_z

    def ray_cast(self, origin: Vec3, direction: Vec3):
        best_t = None
        for tri in self._triangles:
            t = tri.intersect_ray(origin, direction)
            if t is not None and (best_t is None or t < best_t):
                best_t = t
        if best_t is None:
            return None
        return origin + direction * best_t

    def bounds(self):
        return self._bbox

    def describe(self) -> str:
        b = self._bbox
        return (f"TIN '{self.name}': {self.rows}x{self.cols} узлов, "
                f"{len(self._triangles)} треугольников, "
                f"границы ({b[0]:.1f}, {b[1]:.1f})-({b[2]:.1f}, {b[3]:.1f})")