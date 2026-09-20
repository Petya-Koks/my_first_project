from dataclasses import dataclass
import math
from src.objects.base_survey_object import BaseSurveyObject
from src.geometry.polygon import Polygon
from src.core.vector import Vec3


@dataclass
class PointObject(BaseSurveyObject):
    """Точечный объект (устье скважины, репер) — облёт по кругу."""

    def survey_polygon(self) -> Polygon:
        c = self.geometry.centroid()
        n = 12
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            pts.append(Vec3(c.x + self.buffer_m * math.cos(a),
                            c.y + self.buffer_m * math.sin(a),
                            c.z))
        return Polygon(pts)