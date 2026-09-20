"""Проверка, что все модули проекта на месте и импортируются."""
import importlib

MODULES = [
    "src.core.vector",
    "src.core.base_entity",
    "src.geometry.shape",
    "src.geometry.point",
    "src.geometry.line",
    "src.geometry.segment",
    "src.geometry.polyline",
    "src.geometry.polygon",
    "src.sensors.base_camera",
    "src.sensors.alpha_air_450",
    "src.terrain.base_terrain",
    "src.terrain.triangle",
    "src.terrain.tin_model",
    "src.objects.base_survey_object",
    "src.objects.point_object",
    "src.objects.linear_object",
    "src.objects.areal_object",
    "src.planning.waypoint",
    "src.planning.route",
    "src.planning.coverage_planner",
    "src.planning.lawnmower_planner",
    "src.planning.footprint_tracer",
    "src.planning.overlap_checker",
    "src.safety.safety_checker",
    "src.io.config_loader",
    "src.io.tin_loader",
    "src.io.dxf_loader",
    "src.io.route_exporter",
]

ok, fail = 0, 0
for m in MODULES:
    try:
        importlib.import_module(m)
        print(f"  OK   {m}")
        ok += 1
    except Exception as e:
        print(f"  FAIL {m}: {type(e).__name__}: {e}")
        fail += 1

print(f"\nИтого: {ok} OK, {fail} FAIL")