import csv
from src.terrain.tin_model import TINModel
from src.core.vector import Vec3


def load_tin_from_csv(path: str, name: str = "tin",
                      rows: int = 0, cols: int = 0) -> TINModel:
    pts = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        first = next(reader)
        try:
            float(first[0])
            pts.append(Vec3(float(first[0]), float(first[1]), float(first[2])))
        except ValueError:
            pass
        for row in reader:
            pts.append(Vec3(float(row[0]), float(row[1]), float(row[2])))
    return TINModel(name=name, points=pts, rows=rows, cols=cols)