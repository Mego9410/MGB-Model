"""Engine-bay fuel hoses and the rocker cover breather pipe (Haynes Ch 3 Sec 3, Sec 18).

Explode order follows Haynes: the breather pipe comes off first (Sec 3 para 1, before
the air cleaners), then the fuel hose clips and hoses (Sec 18 para 1).
"""
from build123d import Location

from mgb import carb_layout as K

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_m = importlib.util.spec_from_file_location("fuel_pipes_parts", ROOT / "parts" / "fuel" / "pipes.py")
P = importlib.util.module_from_spec(_m)
_m.loader.exec_module(P)

ID = "fuel.pipes"
NAME = "Fuel hoses and breather pipe"
PARENT = "fuel"
HAYNES = {"figures": [], "section": 18}
OUT, DOWN, UP = [0, 1, 0], [0, 0, -1], [0, 0, 1]
GROUPS = {}

I, _n = [], {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc, **o):
    pid = "fuel.pipes." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
bp = P.breather_points()
add("breather-hose", O, explode=ex(UP, 1, 120))
add("breather-clip", P.clip_locations(bp, 7.0), explode=ex(UP, 0.5, 150))
add("breather-clip", P.clip_locations(bp[::-1], 7.0), explode=ex(UP, 0.5, 150), label=False)
for k, x in enumerate(K.CARB_X):
    pts = P.float_hose_points(x)
    name = "front" if k == 0 else "rear"
    add(f"float-hose-{name}", O, explode=ex(DOWN, 3, 70))
    add("fuel-clip", P.clip_locations(pts, 6.0), explode=ex(DOWN, 2, 90), label=k == 0)
    add("fuel-clip", P.clip_locations(pts[::-1], 6.0), explode=ex(DOWN, 2, 90), label=False)
add("tee", O, explode=ex(DOWN, 4, 110))
fp = P.feed_points()
add("feed-hose", O, explode=ex(DOWN, 3, 140))
add("fuel-clip", P.clip_locations(fp, 6.0), explode=ex(DOWN, 2, 160), label=False)
end = P.clip_locations(fp[::-1], 0.0)
add("feed-union", end, explode=ex(DOWN, 2.5, 180))
INSTANCES = I
