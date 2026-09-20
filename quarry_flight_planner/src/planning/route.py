from dataclasses import dataclass, field
from src.core.base_entity import BaseEntity
from src.planning.waypoint import Waypoint


@dataclass
class Route(BaseEntity):
    """Маршрут — упорядоченный список путевых точек."""
    waypoints: list = field(default_factory=list)

    def add(self, wp: Waypoint):
        self.waypoints.append(wp)

    def extend(self, wps: list):
        self.waypoints.extend(wps)

    def length_m(self) -> float:
        import math
        total = 0.0
        for a, b in zip(self.waypoints[:-1], self.waypoints[1:]):
            total += math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))
        return total

    def describe(self) -> str:
        return f"Маршрут '{self.name}': {len(self.waypoints)} точек, {self.length_m():.0f} м"