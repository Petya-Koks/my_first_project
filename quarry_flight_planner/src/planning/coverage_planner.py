from abc import ABC, abstractmethod
from src.sensors.base_camera import BaseCamera
from src.terrain.base_terrain import BaseTerrain
from src.geometry.polygon import Polygon
from src.planning.route import Route


class BaseCoveragePlanner(ABC):
    """Абстрактный планировщик покрытия.

    Содержит общие параметры (камера, рельеф, перекрытия, GSD)
    и абстрактный метод plan(). Наследники реализуют стратегию
    облёта: «змейка», спираль, облёт по контуру и т.д.
    """

    def __init__(self,
                 camera: BaseCamera,
                 terrain: BaseTerrain,
                 forward_overlap: float = 0.80,
                 side_overlap: float = 0.70,
                 target_gsd_cm: float = 1.0,
                 safety_clearance_m: float = 30.0):
        self.camera = camera
        self.terrain = terrain
        self.forward_overlap = forward_overlap
        self.side_overlap = side_overlap
        self.target_gsd_cm = target_gsd_cm
        self.safety_clearance_m = safety_clearance_m

    @abstractmethod
    def plan(self, polygon: Polygon, orientation_deg: float = 0.0) -> Route:
        """Построить маршрут облёта полигона."""
        ...

    def _height_agl(self) -> float:
        """Высота полёта над рельефом для заданного GSD."""
        gsd_m = self.target_gsd_cm / 100.0
        return self.camera.height_for_gsd(gsd_m)