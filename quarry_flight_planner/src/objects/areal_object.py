from dataclasses import dataclass
from src.objects.base_survey_object import BaseSurveyObject
from src.geometry.polygon import Polygon


@dataclass
class ArealObject(BaseSurveyObject):
    """Площадной объект (блок, площадка)."""

    def survey_polygon(self) -> Polygon:
        return self.geometry.buffer_2d(self.buffer_m)