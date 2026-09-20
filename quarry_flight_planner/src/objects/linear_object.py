from src.objects.base_survey_object import BaseSurveyObject
from src.geometry.line import Line
from src.geometry.polygon import Polygon
from src.core.vector import Vec3
import math


class LinearObject(BaseSurveyObject):
    """Линейный объект (траншея, дорога) — буфер-полоса вокруг линии."""

    def survey_polygon(self) -> Polygon:
        pts = self.geometry.vertices()
        left, right = [], []
        for i, p in enumerate(pts):
            if i == 0:
                d = pts[1] - pts[0]
            elif i == len(pts) - 1:
                d = pts[-1] - pts[-2]
            else:
                d = pts[i + 1] - pts[i - 1]
            n = Vec3(-d.y, d.x, 0.0)
            if n.length() > 0:
                n = n.normalized() * self.buffer_m
            left.append(Vec3(p.x + n.x, p.y + n.y, p.z))
            right.append(Vec3(p.x - n.x, p.y - n.y, p.z))
        return Polygon(left + list(reversed(right)))