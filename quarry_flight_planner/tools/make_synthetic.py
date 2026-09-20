"""
Создаёт синтетический TIN (CSV) и объект (DXF) для отладки.
Запуск: python tools/make_synthetic.py
"""
import csv
from pathlib import Path


def synth_terrain(path: str, rows: int = 51, cols: int = 51, step: float = 10.0):
    """Плоскость с ямой посередине."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "z"])
        cx, cy = (cols - 1) * step / 2, (rows - 1) * step / 2
        for r in range(rows):
            for c in range(cols):
                x, y = c * step, r * step
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d < 100:
                    z = 100.0
                elif d < 150:
                    z = 100.0 + (d - 100) * 0.5   # откос
                else:
                    z = 125.0
                w.writerow([x, y, round(z, 2)])


def synth_dxf(path: str):
    """Простейший DXF с одной замкнутой LWPOLYLINE (прямоугольник)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pts = [(100, 100), (300, 100), (300, 250), (100, 250)]
    lines = [
        "0", "SECTION", "2", "ENTITIES",
        "0", "LWPOLYLINE",
        "8", "SURVEY",          # слой
        "90", str(len(pts)),
        "70", "1",              # closed
        "38", "0.0",            # elevation
    ]
    for x, y in pts:
        lines += ["10", str(x), "20", str(y)]
    lines += ["0", "ENDSEC", "0", "EOF"]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    synth_terrain("data/terrain/quarry.csv")
    synth_dxf("data/objects/block_1.dxf")
    print("Синтетика создана: data/terrain/quarry.csv, data/objects/block_1.dxf")