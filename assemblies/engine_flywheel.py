"""Flywheel and ring gear (Haynes Sec 22): lock ring tabs knocked back, bolts out,
flywheel off, then the spigot bush. Bolts to the rear flange of the crankshaft."""
import math

from build123d import Location, Rot

from pathlib import Path

from mgb import engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ID = "engine.flywheel"
NAME = "Flywheel and ring gear"
PARENT = "engine"
HAYNES = {"figures": [], "section": 22}

ROOT = Path(__file__).resolve().parent.parent
EL = E.layout(head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml")))
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "flywheel" / "flywheel.yaml")}
BACK = [-1, 0, 0]
GROUPS = {"flywheel": {"axis": BACK, "order": 3, "distance_mm": 220}}
FLANGE_REAR = EL.main_x[2] - 16 - 34          # rear face of the crankshaft flange (crank model)
BOLT_R = 37.0


def ex(order, d):
    return {"axis": BACK, "order": order, "distance_mm": d}


I = []
add = lambda part, loc, **o: I.append((f"engine.flywheel.{part}#{sum(1 for i in I if i[1].endswith(part)) + 1}",  # noqa: E731
                                        f"engine.flywheel.{part}", loc, o))
cz = EL.crank_z
FW_X = FLANGE_REAR + 4.5                      # crankshaft flange sits 4.5 mm into the flywheel register
add("spigot-bush", Location((FLANGE_REAR + 15, 0, cz)) * Rot(0, -90, 0), explode=ex(4, 260))
add("flywheel", Location((FW_X, 0, cz)), groups=["flywheel"])
add("ring-gear", Location((FW_X, 0, cz)), groups=["flywheel"])
hub_t = SP["engine.flywheel.flywheel"].nom("hub_thickness")
lp_t = SP["engine.flywheel.lock-plate"].nom("thickness")
add("lock-plate", Location((FW_X - hub_t, 0, cz)), explode=ex(2, 60))
for k in range(6):
    a = math.radians(30 + 60 * k)
    add("bolt", Location((FW_X - hub_t - lp_t, BOLT_R * math.cos(a), cz + BOLT_R * math.sin(a))) * Rot(0, 90, 0),
        explode=ex(1, 100), label=k == 0)
INSTANCES = I
