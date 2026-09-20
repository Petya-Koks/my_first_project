from dataclasses import dataclass
from src.sensors.base_camera import BaseCamera


@dataclass
class AlphaAir450(BaseCamera):
    """Камера сенсора AlphaAir 450 (только фотомодуль)."""

    def footprint_at(self, height_agl: float) -> tuple[float, float]:
        """Размер кадра на плоскости на высоте H."""
        import math
        width = 2 * height_agl * math.tan(math.radians(self.fov_x_deg / 2))
        height = 2 * height_agl * math.tan(math.radians(self.fov_y_deg / 2))
        return width, height