from src.io.config_loader import load_config
from src.io.tin_loader import load_tin_from_csv
from src.sensors.alpha_air_450 import AlphaAir450
from src.objects.areal_object import ArealObject
from src.geometry.polygon import Polygon
from src.core.vector import Vec3
from src.planning.lawnmower_planner import LawnmowerPlanner
from src.planning.footprint_tracer import FootprintTracer
from src.planning.overlap_checker import OverlapChecker
from src.safety.safety_checker import SafetyChecker
from src.io.route_exporter import export_route_csv
from pathlib import Path
from src.io.svg_exporter import SVGExporter

def main():
    cfg = load_config("config/settings.json")

    camera = AlphaAir450(
        name=cfg["camera"]["name"],
        sensor_width_mm=cfg["camera"]["sensor_width_mm"],
        sensor_height_mm=cfg["camera"]["sensor_height_mm"],
        resolution_x=cfg["camera"]["resolution_x"],
        resolution_y=cfg["camera"]["resolution_y"],
        focal_length_mm=cfg["camera"]["focal_length_mm"],
    )
    print(camera.describe())

    terrain = load_tin_from_csv(
        cfg["terrain"]["source"],
        name="quarry",
        rows=cfg["terrain"]["rows"],
        cols=cfg["terrain"]["cols"],
    )
    print(terrain.describe())

    # Демо-объект
    obj = ArealObject(
        name="block_1",
        geometry=Polygon([
            Vec3(0, 0, 0), Vec3(200, 0, 0),
            Vec3(200, 150, 0), Vec3(0, 150, 0),
        ]),
        buffer_m=20.0,
    )
    print(obj.describe())

    planner = LawnmowerPlanner(
        camera=camera, terrain=terrain,
        forward_overlap=cfg["flight"]["forward_overlap"],
        side_overlap=cfg["flight"]["side_overlap"],
        target_gsd_cm=cfg["flight"]["target_gsd_cm"],
        safety_clearance_m=cfg["flight"]["safety_clearance_m"],
    )

    poly = obj.survey_polygon()
    print("Вершины полигона съёмки:")
    for v in poly.vertices():
        print(f"  ({v.x:.1f}, {v.y:.1f}, {v.z:.1f})")
    print(f"BBox полигона: {poly.bbox()}")
    print(f"BBox TIN:      {terrain.bounds()}")
    print(f"Центроид:      {poly.centroid()}")

    # проверим contains_xy на центроиде
    c = poly.centroid()
    print(f"contains_xy(центроид) = {poly.contains_xy(c.x, c.y)}")

    poly = obj.survey_polygon()
    print(f"[DEBUG] poly area = {poly.area():.1f}")
    print(f"[DEBUG] poly bbox = {poly.bbox()}")
    print(f"[DEBUG] poly contains (min corner) = {poly.contains_xy(*poly.bbox()[:2])}")
    
    # проверим elevation_at
    for x, y in [(50, 50), (100, 100), (77, 58)]:
        print(f"[DEBUG] elevation_at({x},{y}) = {terrain.elevation_at(x, y)}")

    route = planner.plan(poly, orientation_deg=0.0)
    route = planner.plan(obj.survey_polygon(), orientation_deg=0.0)
    print(route.describe())

    out_dir = Path("data/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    export_route_csv(route, out_dir / "route_block_1.csv")
    print(f"Маршрут сохранён: {out_dir / 'route_block_1.csv'}")

    tracer = FootprintTracer(camera, terrain)
    footprints = [tracer.trace(wp) for wp in route.waypoints]
    overlaps = OverlapChecker.longitudinal_overlap(footprints)
    print("Перекрытие (первые 5):", [f"{o:.2f}" for o in overlaps[:5]])

    problems = SafetyChecker(terrain).check(route)
    print("Проблемы безопасности:", problems or "нет")
    # SVG-визуализация
    svg = SVGExporter(width_px=1400, height_px=1000)
    out_svg = svg.render(
        output_path="data/output/route_block_1.svg",
        route=route,
        survey_polygon=obj.survey_polygon(),
        footprints=footprints,
        terrain=terrain,
        title="Маршрут БПЛА над block_1",
    )
    print(f"SVG сохранён: {out_svg}")

if __name__ == "__main__":
    main()