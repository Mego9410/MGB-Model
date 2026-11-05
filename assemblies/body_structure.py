"""Body shell inner structure: floor, tunnel, bulkhead, chassis legs, inner wings, sills, pillars, heelboard, tonneau
floor, rear bulkhead, wheel houses, boot floor, rear rails and the brackets the earlier phases hang from (Haynes Ch 12
Sec 1; mountings from P8-P11a).

The shell is one welded unit, so its explode is by area rather than a removal order: the front structure forward, the
rear structure back, the sides out, the floor down; the bolt-on covers and grommets come away first.
"""
from build123d import Location

from mgb import underbody_layout as U

ID = "body.structure"
NAME = "Body shell structure"
PARENT = "body"
HAYNES = {"section": 1}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"front": {"axis": FWD, "order": 3, "distance_mm": 500}, "rear": {"axis": BACK, "order": 3, "distance_mm": 500},
          "floor": {"axis": DOWN, "order": 2, "distance_mm": 300}, "left": {"axis": LEFT, "order": 2, "distance_mm": 300},
          "right": {"axis": RIGHT, "order": 2, "distance_mm": 300}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    I.append((f"body.structure.{part}#{n}", f"body.structure.{part}", loc, o))


def side_group(part):
    return "left" if part.endswith("-l") else "right"


for p in ("tunnel", "floor-l", "floor-r", "toe-board-l", "toe-board-r", "heelboard"):
    add(p, groups=["floor"])
for k, (x, y) in enumerate([(-860.0, 545.0), (-1380.0, 545.0), (-860.0, -545.0), (-1380.0, -545.0)]):
    add("floor-bung", Location((x, y, U.FLOOR_Z)), n=k + 1, label=k == 0, explode=ex(DOWN, 1, 60))
for p in ("bulkhead", "column-toe-mount", "clutch-hose-support", "scuttle-inner", "wiper-motor-bracket",
          "column-top-bracket", "front-leg-l", "front-leg-r", "inner-wing-l", "inner-wing-r", "front-apron",
          "lock-platform", "bulkhead-upper", "bulkhead-brackets", "inner-wing-brackets", "front-pan", "slam-stays"):
    add(p, groups=["front"])
for p in ("outer-sill-l", "outer-sill-r", "inner-sill-l", "castle-l", "jack-socket-l", "hinge-pillar-l", "shut-pillar-l",
          "inner-sill-r", "castle-r", "jack-socket-r", "hinge-pillar-r", "shut-pillar-r"):
    add(p, groups=[side_group(p)])
for p in ("tonneau-floor", "rear-bulkhead", "rear-wheelhouse-l", "rear-wheelhouse-r", "boot-floor", "tank-tabs",
          "rear-rail-l", "rear-rail-r", "rear-hose-bracket"):
    add(p, groups=["rear"])
add("handbrake-abutment", groups=["floor"])
add("battery-cover-l", explode=ex(UP, 1, 120))
add("battery-cover-r", explode=ex(UP, 1, 120))
add("cable-grommet", explode=ex(DOWN, 1, 80))
add("harness-grommets", explode=ex(UP, 1, 60))
add("harness-clips", explode=ex(UP, 1, 60))
add("arch-liners", explode=ex(DOWN, 1, 200))
add("arch-lips", explode=ex(DOWN, 1, 220))
INSTANCES = I
