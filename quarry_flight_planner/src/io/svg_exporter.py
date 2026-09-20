"""
Экспорт маршрута и объектов в SVG.
Без внешних библиотек — только стандартный Python.

Координаты мира (метры) отображаются в пиксели SVG через
линейное преобразование с сохранением пропорций.
"""
from pathlib import Path
from src.planning.route import Route
from src.geometry.polygon import Polygon


class SVGExporter:
    """Рисует сцену (рельеф, объект, маршрут, следы кадров) в SVG."""

    def __init__(self,
                 width_px: int = 1200,
                 height_px: int = 900,
                 margin_px: int = 40,
                 background: str = "#ffffff"):
        self.width_px = width_px
        self.height_px = height_px
        self.margin = margin_px
        self.background = background

    # ---------- координатные преобразования ----------
    def _setup_transform(self, bbox_world):
        """Считает коэффициенты перевода world → px с сохранением пропорций."""
        minx, miny, maxx, maxy = bbox_world
        w_world = maxx - minx
        h_world = maxy - miny
        # избегаем деления на ноль
        if w_world <= 0:
            w_world = 1.0
        if h_world <= 0:
            h_world = 1.0

        avail_w = self.width_px - 2 * self.margin
        avail_h = self.height_px - 2 * self.margin
        scale = min(avail_w / w_world, avail_h / h_world)

        # центрирование
        offset_x = self.margin + (avail_w - w_world * scale) / 2
        offset_y = self.margin + (avail_h - h_world * scale) / 2

        self._scale = scale
        self._offset_x = offset_x
        self._offset_y = offset_y
        self._minx = minx
        self._maxy = maxy  # SVG Y растёт вниз, поэтому инвертируем

    def _to_px(self, x: float, y: float) -> tuple[float, float]:
        px = self._offset_x + (x - self._minx) * self._scale
        py = self._offset_y + (self._maxy - y) * self._scale
        return px, py

    # ---------- примитивы SVG ----------
    @staticmethod
    def _polyline_points(points_px: list) -> str:
        return " ".join(f"{x:.2f},{y:.2f}" for x, y in points_px)

    # ---------- основной метод ----------
    def render(self,
               output_path: str | Path,
               route: Route = None,
               survey_polygon: Polygon = None,
               footprints: list = None,
               terrain=None,
               title: str = "Маршрут БПЛА"):
        """Собирает SVG-документ и сохраняет в файл."""

        # 1) Определяем общий bbox сцены
        bboxes = []
        if terrain is not None:
            bboxes.append(terrain.bounds())
        if survey_polygon is not None:
            bboxes.append(survey_polygon.bbox())
        if route is not None and route.waypoints:
            xs = [wp.x for wp in route.waypoints]
            ys = [wp.y for wp in route.waypoints]
            bboxes.append((min(xs), min(ys), max(xs), max(ys)))
        if not bboxes:
            raise ValueError("Нечего рисовать: нет ни рельефа, ни объекта, ни маршрута")

        minx = min(b[0] for b in bboxes)
        miny = min(b[1] for b in bboxes)
        maxx = max(b[2] for b in bboxes)
        maxy = max(b[3] for b in bboxes)
        self._setup_transform((minx, miny, maxx, maxy))

        # 2) Собираем SVG
        parts = []
        parts.append(self._svg_header(title))
        parts.append(self._svg_background())

        # 3) Сетка TIN
        if terrain is not None and hasattr(terrain, "rows") and hasattr(terrain, "cols"):
            parts.append(self._svg_tin_grid(terrain))

        # 4) Следы кадров
        if footprints:
            parts.append(self._svg_footprints(footprints))

        # 5) Объект съёмки
        if survey_polygon is not None:
            parts.append(self._svg_polygon(survey_polygon))

        # 6) Маршрут
        if route is not None:
            parts.append(self._svg_route(route))

        # 7) Легенда и подписи
        parts.append(self._svg_legend(route, footprints))

        parts.append("</svg>")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(parts), encoding="utf-8")
        return output_path

    # ---------- сборка частей ----------
    def _svg_header(self, title: str) -> str:
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width_px}" height="{self.height_px}" '
            f'viewBox="0 0 {self.width_px} {self.height_px}">\n'
            f'  <title>{title}</title>'
        )

    def _svg_background(self) -> str:
        return (f'  <rect x="0" y="0" width="{self.width_px}" '
                f'height="{self.height_px}" fill="{self.background}"/>')

    def _svg_tin_grid(self, terrain) -> str:
        """Рисует только внешний контур TIN, чтобы не засорять сцену."""
        b = terrain.bounds()
        corners = [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])]
        pts = [self._to_px(x, y) for x, y in corners]
        return (f'  <polygon points="{self._polyline_points(pts)}" '
                f'fill="none" stroke="#cccccc" stroke-width="1" '
                f'stroke-dasharray="4 4"/>')

    def _svg_footprints(self, footprints: list) -> str:
        lines = []
        for fp in footprints:
            pts = [self._to_px(v.x, v.y) for v in fp.vertices()]
            lines.append(
                f'  <polygon points="{self._polyline_points(pts)}" '
                f'fill="#ffe680" fill-opacity="0.15" '
                f'stroke="#e6b800" stroke-width="0.5"/>'
            )
        return "\n".join(lines)

    def _svg_polygon(self, polygon: Polygon) -> str:
        pts = [self._to_px(v.x, v.y) for v in polygon.vertices()]
        return (f'  <polygon points="{self._polyline_points(pts)}" '
                f'fill="#cfe2ff" fill-opacity="0.3" '
                f'stroke="#1f6feb" stroke-width="2"/>')

    def _svg_route(self, route: Route) -> str:
        lines = []

        # линия маршрута
        pts = [self._to_px(wp.x, wp.y) for wp in route.waypoints]
        if len(pts) >= 2:
            lines.append(
                f'  <polyline points="{self._polyline_points(pts)}" '
                f'fill="none" stroke="#d11a2a" stroke-width="1.5"/>'
            )

        # точки
        for wp in route.waypoints:
            px, py = self._to_px(wp.x, wp.y)
            lines.append(
                f'  <circle cx="{px:.2f}" cy="{py:.2f}" r="2" '
                f'fill="#d11a2a"/>'
            )

        # выделяем старт и финиш
        if route.waypoints:
            sx, sy = self._to_px(route.waypoints[0].x, route.waypoints[0].y)
            ex, ey = self._to_px(route.waypoints[-1].x, route.waypoints[-1].y)
            lines.append(
                f'  <circle cx="{sx:.2f}" cy="{sy:.2f}" r="6" '
                f'fill="none" stroke="#0a8f2b" stroke-width="2"/>'
                f'  <text x="{sx + 8:.2f}" y="{sy - 8:.2f}" '
                f'font-family="Arial" font-size="12" fill="#0a8f2b">Старт</text>'
            )
            lines.append(
                f'  <circle cx="{ex:.2f}" cy="{ey:.2f}" r="6" '
                f'fill="none" stroke="#6a0dad" stroke-width="2"/>'
                f'  <text x="{ex + 8:.2f}" y="{ey - 8:.2f}" '
                f'font-family="Arial" font-size="12" fill="#6a0dad">Финиш</text>'
            )

        return "\n".join(lines)

    def _svg_legend(self, route: Route, footprints: list) -> str:
        lines = []
        x0 = 20
        y0 = 20
        lines.append(
            f'  <text x="{x0}" y="{y0}" font-family="Arial" '
            f'font-size="14" font-weight="bold">Легенда</text>'
        )
        legend = [
            ("#1f6feb", "Объект съёмки (с буфером)"),
            ("#d11a2a", "Маршрут"),
            ("#e6b800", "След кадра камеры"),
            ("#cccccc", "Граница TIN"),
        ]
        for i, (color, text) in enumerate(legend):
            yy = y0 + 20 + i * 18
            lines.append(
                f'  <rect x="{x0}" y="{yy - 10}" width="14" height="10" '
                f'fill="{color}" fill-opacity="0.5" stroke="{color}"/>'
                f'  <text x="{x0 + 22}" y="{yy}" font-family="Arial" '
                f'font-size="12">{text}</text>'
            )

        # числовые показатели
        if route is not None and route.waypoints:
            yy = y0 + 20 + len(legend) * 18 + 10
            lines.append(
                f'  <text x="{x0}" y="{yy}" font-family="Arial" font-size="12">'
                f'Точек: {len(route.waypoints)}</text>'
            )
            lines.append(
                f'  <text x="{x0}" y="{yy + 16}" font-family="Arial" font-size="12">'
                f'Длина: {route.length_m():.0f} м</text>'
            )

        return "\n".join(lines)