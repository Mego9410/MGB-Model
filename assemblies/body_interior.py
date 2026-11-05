"""Facia, seats, carpets, door trim and tunnel fittings (Haynes Ch 12 Sec 3, 29, 47, 54; Fig 12.19; Ch 6 Fig 6.3).
Explode: the door fittings and trim pads off (Sec 29), the seats out (Sec 54), the carpets up, the grommet off the
tunnel, the facia back (Sec 47)."""
from build123d import Location, Rot

ID = "body.interior"
NAME = "Interior and trim"
PARENT = "body"
HAYNES = {"section": 47}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"seat-l": {"axis": UP, "order": 2, "distance_mm": 500}, "seat-r": {"axis": UP, "order": 2, "distance_mm": 500}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    pid = part if "." in part else f"body.interior.{part}"
    I.append((f"{pid}#{n}", pid, loc, o))


for n, out in (("l", LEFT), ("r", RIGHT)):
    add(f"inner-handle-{n}", explode=ex(out, 1, -60))
    add(f"winder-{n}", explode=ex(out, 1, -80))
    add(f"door-card-{n}", explode=ex(out, 2, -150))
    add(f"door-capping-{n}", explode=ex(UP, 2, 150))
    g = [f"seat-{n}"]
    add(f"seat-cushion-{n}", groups=g, explode=ex(UP, 1, 60))
    add(f"seat-squab-{n}", groups=g, explode=ex(BACK, 1, 100))
    add(f"seat-frame-{n}", groups=g)
    add(f"seat-piping-{n}", groups=g, explode=ex(UP, 1, 70))
    add(f"floor-carpet-{n}", explode=ex(UP, 3, 300))
add("cockpit-rim", explode=ex(UP, 2, 150))
add("tunnel-carpet", explode=ex(UP, 3, 380))
add("rear-carpet", explode=ex(UP, 3, 300))
add("lever-grommet", explode=ex(UP, 1, 200))
add("grommet-retainer", explode=ex(UP, 1, 160))
add("dipstick-plug", explode=ex(UP, 1, 140))
add("glovebox-lid", explode=ex(BACK, 1, 120))
add("crash-roll", explode=ex(BACK, 4, 200))
add("facia", explode=ex(BACK, 5, 300))
add("centre-panel", explode=ex(BACK, 4.5, 220))
add("plaque", explode=ex(BACK, 3, 120))
add("plaque-field", explode=ex(BACK, 3, 110))
add("heater-knob-upper", explode=ex(BACK, 2, 90))
add("heater-knob-lower", explode=ex(BACK, 2, 90))
add("heater-knob-caps", explode=ex(BACK, 1.5, 110))
add("binnacle", explode=ex(BACK, 4, 160))
add("glovebox-strip", explode=ex(BACK, 1, 140))
add("console", explode=ex(BACK, 4, 260))
add("speaker-grille", explode=ex(BACK, 3, 200))
INSTANCES = I
