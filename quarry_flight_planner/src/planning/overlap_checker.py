from src.geometry.polygon import Polygon


class OverlapChecker:
    """Оценка перекрытия между следами кадров.

    Точное пересечение полигонов (Sutherland–Hodgman) — задача следующей
    итерации. Пока используем оценку через bounding box: она даёт верхнюю
    границу перекрытия и подходит для валидации шага маршрута.
    """

    @staticmethod
    def _bbox(poly: Polygon) -> tuple:
        return poly.bbox()

    @staticmethod
    def _polygon_area(poly: Polygon) -> float:
        return poly.area()

    @staticmethod
    def _bbox_intersection_area(a: Polygon, b: Polygon) -> float:
        ax1, ay1, ax2, ay2 = a.bbox()
        bx1, by1, bx2, by2 = b.bbox()
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        if ix1 >= ix2 or iy1 >= iy2:
            return 0.0
        return (ix2 - ix1) * (iy2 - iy1)

    @staticmethod
    def overlap_ratio(a: Polygon, b: Polygon) -> float:
        """Отношение площади пересечения bbox к площади меньшего полигона."""
        inter = OverlapChecker._bbox_intersection_area(a, b)
        ref = min(a.area(), b.area())
        return inter / ref if ref > 0 else 0.0

    @staticmethod
    def longitudinal_overlap(footprints: list) -> list:
        """Перекрытие между последовательными кадрами (вдоль маршрута)."""
        return [
            OverlapChecker.overlap_ratio(a, b)
            for a, b in zip(footprints[:-1], footprints[1:])
        ]

    @staticmethod
    def lateral_overlap(row_a: list, row_b: list) -> float:
        """Среднее перекрытие между двумя соседними галсами."""
        ratios = []
        for pa in row_a:
            for pb in row_b:
                r = OverlapChecker.overlap_ratio(pa, pb)
                if r > 0:
                    ratios.append(r)
        return sum(ratios) / len(ratios) if ratios else 0.0