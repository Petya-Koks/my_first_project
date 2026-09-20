import csv
from pathlib import Path
from src.planning.route import Route


def export_route_csv(route: Route, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["idx", "x", "y", "z", "heading_deg",
                    "gimbal_pitch_deg", "action"])
        for i, wp in enumerate(route.waypoints):
            w.writerow([i, wp.x, wp.y, wp.z, wp.heading_deg,
                        wp.gimbal_pitch_deg, wp.action.value])