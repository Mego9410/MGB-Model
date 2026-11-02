"""Wiring loom (Haynes Fig 10.26): engine-bay main harness, facia harness, rear harness and the
overdrive leads. Explode: each harness lifts away from the body as a whole."""
from build123d import Location

ID = "electrical.loom"
NAME = "Wiring loom"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


O = Location((0, 0, 0))
INSTANCES = [
    ("electrical.loom.engine-bay#1", "electrical.loom.engine-bay", O, {"explode": ex([0, 0, 1], 1, 160)}),
    ("electrical.loom.facia#1", "electrical.loom.facia", O, {"explode": ex([-1, 0, 0], 1, 160)}),
    ("electrical.loom.rear#1", "electrical.loom.rear", O, {"explode": ex([0, -1, 0], 1, 200)}),
    ("electrical.loom.overdrive#1", "electrical.loom.overdrive", O, {"explode": ex([0, 0, -1], 1, 120)}),
]
