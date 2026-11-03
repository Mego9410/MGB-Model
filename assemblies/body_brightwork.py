"""Bumpers, overriders, grille, strips, badges and number plates (Haynes Ch 12 Sec 7, 10, 14; Fig 12.1). Explode
follows Sec 10: the overriders off the bars, the bars forward and back on their spring bars; the grille out (Sec 7);
the strips off their clips."""
from build123d import Location, Rot

from mgb import body_layout as BL
from parts.body import brightwork as B

ID = "body.brightwork"
NAME = "Bumpers, grille and bright work"
PARENT = "body"
HAYNES = {"section": 10}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"front": {"axis": FWD, "order": 2, "distance_mm": 300}, "rear": {"axis": BACK, "order": 2, "distance_mm": 300}, "grille": {"axis": FWD, "order": 3, "distance_mm": 400}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    pid = part if "." in part else f"body.brightwork.{part}"
    I.append((f"{pid}#{n}", pid, loc, o))


for n, out in (("l", LEFT), ("r", RIGHT)):
    add(f"front-overrider-{n}", groups=["front"], explode=ex(FWD, 1, 120))
    add(f"rear-overrider-{n}", groups=["rear"], explode=ex(BACK, 1, 120))
    add(f"front-spring-bar-{n}", explode=ex(FWD, 4, 150))
    add(f"rear-bracket-{n}", explode=ex(BACK, 4, 150))
    for w in ("front", "door", "rear"):
        add(f"strip-{w}-{n}", explode=ex(out, 1, 80))
add("front-bar", groups=["front"])
add("rear-bar", groups=["rear"])
add("front-plinth", groups=["front"])
add("front-plate", groups=["front"], explode=ex(FWD, 1, 60))
add("rear-plinth", explode=ex(BACK, 1, 80))
add("rear-plate", explode=ex(BACK, 0.5, 120))
add("boot-badge", explode=ex(BACK, 1, 100))
add("scuttle-vent", explode=ex(UP, 1, 80))
for k, (n, y) in enumerate((("l", BL.OVERRIDER_Y), ("r", -BL.OVERRIDER_Y))):
    add("overrider-rubber-rear", Location((0, y, 0)), n=k + 1, groups=["rear"], explode=ex(BACK, 0.5, 60), label=k == 0)
for k, y in enumerate((B.OVR_FRONT_Y, -B.OVR_FRONT_Y)):
    add("overrider-rubber-front", Location((0, y, 0)), n=k + 1, groups=["front"], explode=ex(FWD, 0.5, 60), label=k == 0)
for p in ("grille-surround", "grille-slats", "grille-bar", "grille-rail"):
    add(p, groups=["grille"])
add("grille-badge", groups=["grille"], explode=ex(FWD, 1, 60))
INSTANCES = I
