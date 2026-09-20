from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.core.base_entity import BaseEntity


@dataclass
class BaseCamera(BaseEntity, ABC):
    """Абстрактная камера."""
    sensor_width_mm: float = 0.0
    sensor_height_mm: float = 0.0
    resolution_x: int = 0
    resolution_y: int = 0
    focal_length_mm: float = 0.0

    @property
    def fov_x_deg(self) -> float:
        """Угол поля зрения по горизонтали."""
        import math
        return math.degrees(2 * math.atan(self.sensor_width_mm / (2 * self.focal_length_mm)))

    @property
    def fov_y_deg(self) -> float:
        """Угол поля зрения по вертикали."""
        import math
        return math.degrees(2 * math.atan(self.sensor_height_mm / (2 * self.focal_length_mm)))

    @abstractmethod
    def footprint_at(self, height_agl: float) -> tuple[float, float]:
        """Размер кадра на земле (ширина, высота) при заданной высоте."""
        ...

    def height_for_gsd(self, gsd_m_per_px: float) -> float:
        """Высота полёта (в метрах) для получения заданного GSD (м/пиксель)."""
        gsd_mm = gsd_m_per_px * 1000.0
        h_mm = (gsd_mm * self.focal_length_mm) / (self.sensor_width_mm / self.resolution_x)
        return h_mm / 1000.0

    def describe(self) -> str:
        return f"Камера {self.name}: {self.resolution_x}x{self.resolution_y}, FOV {self.fov_x_deg:.1f}°x{self.fov_y_deg:.1f}°"