"""Bonnet and boot fittings (Haynes Ch 12 Secs 6, 25, 26): the bonnet's lock plate and catch, its control cable and
pull knob, the safety catch; the boot lid's stay and its guide, and the boot aperture seal. The bonnet lock pin,
bonnet stay and hinges stay in body.front, the boot lock, handle and hinges in body.rear.

Explode follows Sec 6 paras 3-4 (the safety catch, then the cable, then the lock plate) and Sec 26 (the stay, then
the seal).
"""
from build123d import Location

ID = "body.closure-fittings"
NAME = "Bonnet and boot fittings"
PARENT = "body"
HAYNES = {"section": 6}
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"bonnet": {"axis": FWD, "order": 4, "distance_mm": 300}, "boot": {"axis": BACK, "order": 4, "distance_mm": 300}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, **o):
    I.append((f"body.closure-fittings.{part}#1", f"body.closure-fittings.{part}", O, o))


add("bonnet-safety-catch", groups=["bonnet"], explode=ex(UP, 1, 150))
add("bonnet-cable", groups=["bonnet"], explode=ex(LEFT, 2, 150))
add("bonnet-knob", groups=["bonnet"], explode=ex(BACK, 2, 100))
add("bonnet-catch", groups=["bonnet"], explode=ex(DOWN, 3, 120))
add("boot-stay", groups=["boot"], explode=ex(UP, 1, 150))
add("boot-stay-guide", groups=["boot"], explode=ex(LEFT, 2, 100))
add("boot-seal", groups=["boot"], explode=ex(UP, 2, 120))

INSTANCES = I
