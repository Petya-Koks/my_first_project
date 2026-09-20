import math
from src.planning.coverage_planner import BaseCoveragePlanner
from src.geometry.polygon import Polygon
from src.planning.route import Route
from src.planning.waypoint import Waypoint, ActionType
from src.core.vector import Vec3


class LawnmowerPlanner(BaseCoveragePlanner):
    """Классическая «змейка» внутри полигона.

    Идея:
      1) повернуть полигон так, чтобы «змейка» шла вдоль оси X;
      2) для каждой строки y=const найти пересечения с рёбрами полигона
         (получить x_start и x_end вдоль галса);
      3) идти вдоль галса с шагом step_fwd, добавляя точки съёмки;
      4) перейти на следующий галс через step_side, сменить направление.
    """

    def plan(self, polygon: Polygon, orientation_deg: float = 0.0) -> Route:
        h_agl = self._height_agl()
        width_m, height_m = self.camera.footprint_at(h_agl)
        step_side = width_m * (1 - self.side_overlap)
        step_fwd = height_m * (1 - self.forward_overlap)

        angle = math.radians(orientation_deg)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        c = polygon.centroid()

        # локальные координаты вершин
        local = []
        for p in polygon.vertices():
            dx, dy = p.x - c.x, p.y - c.y
            lx = cos_a * dx + sin_a * dy
            ly = -sin_a * dx + cos_a * dy
            local.append((lx, ly))

        minx = min(p[0] for p in local)
        maxx = max(p[0] for p in local)
        miny = min(p[1] for p in local)
        maxy = max(p[1] for p in local)
        print(f"[DEBUG planner] local bbox: minx={minx:.1f} maxx={maxx:.1f} "
            f"miny={miny:.1f} maxy={maxy:.1f}")
        print(f"[DEBUG planner] step_side={step_side:.1f} step_fwd={step_fwd:.1f}")


        
        def to_global(px: float, py: float) -> Vec3:
            return Vec3(
                c.x + cos_a * px - sin_a * py,
                c.y + sin_a * px + cos_a * py,
                0.0,
            )

        route = Route(name="coverage")

        y = miny + step_side / 2
        direction = 1  # +1 — слева направо, -1 — справа налево
        while y <= maxy:
            xs = self._line_polygon_intersections(local, y)
            if xs:
                x_start = min(xs)
                x_end = max(xs)
                if direction < 0:
                    x_start, x_end = x_end, x_start

                # идём вдоль галса
                x = x_start
                # защита от бесконечного цикла
                max_iter = 10000
                it = 0
                while ((direction > 0 and x <= x_end) or
                       (direction < 0 and x >= x_end)) and it < max_iter:
                    gp = to_global(x, y)
                    if polygon.contains_xy(gp.x, gp.y):
                        z_g = self.terrain.elevation_at(gp.x, gp.y)
                        wp = Waypoint(
                            x=gp.x, y=gp.y,
                            z=z_g + h_agl + self.safety_clearance_m,
                            action=ActionType.PHOTO,
                            heading_deg=orientation_deg if direction > 0 else orientation_deg + 180,
                        )
                        route.add(wp)
                    x += step_fwd * direction
                    it += 1

            y += step_side
            direction *= -1

        return route

    @staticmethod
    def _line_polygon_intersections(local_pts: list, y_local: float) -> list:
        """X-координаты пересечения горизонтальной линии y=y_local
        с рёбрами полигона (в локальных координатах)."""
        xs = []
        n = len(local_pts)
        # определяем, замкнут ли список (последняя = первой)
        closed = (n >= 2 and local_pts[0] == local_pts[-1])
        m = n - 1 if closed else n
        for i in range(m):
            x1, y1 = local_pts[i]
            x2, y2 = local_pts[(i + 1) % m]
            if (y1 > y_local) != (y2 > y_local):
                t = (y_local - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        return xs