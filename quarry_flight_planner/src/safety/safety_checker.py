from src.terrain.base_terrain import BaseTerrain
from src.planning.route import Route


class SafetyChecker:
    """Проверка высот: AGL ≥ минимум, AMSL ≤ максимум."""

    def __init__(self, terrain: BaseTerrain,
                 min_agl: float = 30.0,
                 max_amsl: float = 500.0):
        self.terrain = terrain
        self.min_agl = min_agl
        self.max_amsl = max_amsl

    def check(self, route: Route) -> list[str]:
        problems = []
        for i, wp in enumerate(route.waypoints):
            z_g = self.terrain.elevation_at(wp.x, wp.y)
            if z_g != z_g:  # NaN
                problems.append(f"WP#{i}: высота рельефа неизвестна")
                continue
            agl = wp.z - z_g
            if agl < self.min_agl:
                problems.append(f"WP#{i}: AGL = {agl:.1f} м < {self.min_agl} м")
            if wp.z > self.max_amsl:
                problems.append(f"WP#{i}: AMSL = {wp.z:.1f} м > {self.max_amsl} м")
        return problems