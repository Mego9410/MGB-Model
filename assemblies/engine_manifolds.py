"""Inlet and exhaust manifolds (Haynes Sec 15): nuts and washers off, inlet manifold
away, exhaust manifold away, gasket last. On the left of the head."""
from pathlib import Path

from build123d import Location, Rot

from mgb import spec as S
from mgb.head_layout import layout as head_layout

ID = "engine.manifolds"
NAME = "Inlet and exhaust manifolds"
PARENT = "engine"
HAYNES = {"figures": [], "section": 15}

ROOT = Path(__file__).resolve().parent.parent
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "manifolds" / "manifolds.yaml")}
LEFT = [0, 1, 0]
GROUPS = {}


def ex(order, d, axis=LEFT):
    return {"axis": axis, "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "engine.manifolds." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


face = HL.y_max + SP["engine.manifolds.gasket"].nom("thickness")
t = SP["engine.manifolds.exhaust"].nom("flange_thickness")
add("gasket", Location((0, 0, 0)), explode=ex(4, 30))
add("exhaust", Location((0, 0, 0)), explode=ex(3, 200, [0, 0.55, -0.85]))
add("inlet", Location((0, 0, 0)), explode=ex(2, 220, [0, 0.8, 0.6]))
for k, (x, z, kind) in enumerate(HL.manifold_studs):
    w = "washer-large" if kind == "centre" else "washer-small"
    wt = SP["engine.manifolds." + w].nom("thickness")
    add(w, Location((x, face + t, z)) * Rot(-90, 0, 0), explode=ex(1.5, 60), label=k in (0, 4))
    add("nut", Location((x, face + t + wt, z)) * Rot(-90, 0, 0), explode=ex(1, 90), label=k == 0)
INSTANCES = I
