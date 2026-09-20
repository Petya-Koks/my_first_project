from src.geometry.polyline import Polyline
from src.geometry.polygon import Polygon
from src.geometry.point import Point
from src.core.vector import Vec3


def load_dxf_entities(path: str) -> list:
    """Минимальный парсер DXF: LWPOLYLINE (с elevation), POLYLINE, POINT."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = [line.strip() for line in f]

    tokens = []
    for i in range(0, len(raw) - 1, 2):
        try:
            code = int(raw[i])
        except ValueError:
            continue
        tokens.append((code, raw[i + 1]))

    entities = []
    i = 0
    while i < len(tokens):
        code, value = tokens[i]

        if code == 0 and value == "LWPOLYLINE":
            ent = {"pts": [], "closed": 0, "elev": 0.0}
            i += 1
            while i < len(tokens) and tokens[i][0] != 0:
                c, v = tokens[i]
                if c == 70:
                    ent["closed"] = int(v) & 1
                elif c == 38:
                    ent["elev"] = float(v)
                elif c == 10:
                    x = float(v)
                    y = float(tokens[i + 1][1])
                    ent["pts"].append(Vec3(x, y, ent["elev"]))
                    i += 1
                i += 1
            if len(ent["pts"]) >= 2:
                if ent["closed"]:
                    entities.append(Polygon(ent["pts"]))
                else:
                    entities.append(Polyline(ent["pts"]))
            continue

        elif code == 0 and value == "POINT":
            i += 1
            x = y = z = 0.0
            while i < len(tokens) and tokens[i][0] != 0:
                c, v = tokens[i]
                if c == 10:
                    x = float(v)
                elif c == 20:
                    y = float(v)
                elif c == 30:
                    z = float(v)
                i += 1
            entities.append(Point(Vec3(x, y, z)))
            continue

        i += 1

    return entities