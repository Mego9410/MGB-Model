"""Front outer panels: front wings, grille panel, front valance, bonnet and scuttle (Haynes Ch 12 Sec 6-7).

Explode: the bonnet off its hinges first (Sec 6 para 1), then the bolt-on wings outward, the grille panel and valance
forward, the scuttle up."""
from build123d import Location

ID = "body.front"
NAME = "Front panels and bonnet"
PARENT = "body"
HAYNES = {"section": 6}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"bonnet": {"axis": UP, "order": 1, "distance_mm": 450}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    I.append((f"body.front.{part}#{n}", f"body.front.{part}", loc, o))


add("bonnet-skin", groups=["bonnet"])
add("bonnet-frame", groups=["bonnet"])
add("bonnet-lock", explode=ex(UP, 0.5, 120))
add("bonnet-hinge-l", explode=ex(UP, 1.5, 150))
add("bonnet-hinge-r", explode=ex(UP, 1.5, 150))
add("bonnet-stay", explode=ex(LEFT, 1.5, 150))
add("front-wing-l", explode=ex(LEFT, 2, 350))
add("front-wing-r", explode=ex(RIGHT, 2, 350))
add("grille-panel", explode=ex(FWD, 3, 300))
add("front-valance", explode=ex(FWD, 3, 220))
add("scuttle", explode=ex(UP, 4, 250))
INSTANCES = I
