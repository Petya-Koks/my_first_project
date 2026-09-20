import math
from src.sensors.base_camera import BaseCamera
from src.terrain.base_terrain import BaseTerrain
from src.planning.waypoint import Waypoint
from src.geometry.polygon import Polygon
from src.core.vector import Vec3


class FootprintTracer:
    """Трассирует кадр камеры на поверхность рельефа."""

    def __init__(self, camera: BaseCamera, terrain: BaseTerrain):
        self.camera = camera
        self.terrain = terrain

    def trace(self, wp: Waypoint) -> Polygon:
        """Возвращает полигон следа кадра на поверхности."""
        hx = math.radians(self.camera.fov_x_deg / 2)
        hy = math.radians(self.camera.fov_y_deg / 2)
        corners = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]

        origin = Vec3(wp.x, wp.y, wp.z)
        heading = math.radians(wp.heading_deg)
        cos_h, sin_h = math.cos(heading), math.sin(heading)

        pts = []
        for fx, fy in corners:
            dx = math.tan(fx)
            dy = math.tan(fy)
            # gimbal вниз: ось камеры смотрит вниз (0, 0, -1)
            local = Vec3(dx, dy, -1).normalized()
            gx = cos_h * local.x - sin_h * local.y
            gy = sin_h * local.x + cos_h * local.y
            gz = local.z
            direction = Vec3(gx, gy, gz)

            hit = self.terrain.ray_cast(origin, direction)
            if hit is None:
                # fallback — проекция на плоскость z = рельеф под дроном
                flat_z = self.terrain.elevation_at(wp.x, wp.y)
                t = (origin.z - flat_z) / max(-direction.z, 1e-6)
                hit = origin + direction * t
            pts.append(hit)

        return Polygon(pts)