"""Door mechanisms (Haynes Ch 12 Secs 29, 35, 38, 39, 42; Figs 12.13, 12.15, 12.17): each door's window regulator
with its arms and the glass's lower channel, the lock, remote control and lock barrel, the check strap, the interior
pull and trim clips, and the aperture seals and striker backing on the body. Hide body.doors.skin-* and
body.interior.door-card-* to see them.

Explode follows the removal order: the trim's pull and clips (Sec 29), then the regulator out through the aperture
(Sec 38: regulator and extension screws, the arms' studs out of the channel), then the lock and remote control (Sec
35), then the lock barrel (Sec 33), the check strap and the body's seals and striker backing.
"""
from build123d import Location

ID = "body.door-mechanisms"
NAME = "Door mechanisms"
PARENT = "body"
HAYNES = {"section": 38}
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"left": {"axis": LEFT, "order": 5, "distance_mm": 250}, "right": {"axis": RIGHT, "order": 5, "distance_mm": 250}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, **o):
    I.append((f"body.door-mechanisms.{part}#1", f"body.door-mechanisms.{part}", O, o))


for n, inward, out in (("l", RIGHT, LEFT), ("r", LEFT, RIGHT)):
    g = ["left" if n == "l" else "right"]
    add(f"door-pull-{n}", groups=g, explode=ex(inward, 1, 120))
    add(f"card-clips-{n}", groups=g, explode=ex(inward, 1, 80))
    add(f"arm-stop-{n}", groups=g, explode=ex(inward, 2, 120))
    add(f"regulator-{n}", groups=g, explode=ex(inward, 2, 180))
    add(f"lift-arm-{n}", groups=g, explode=ex(inward, 2, 180))
    add(f"extension-arm-{n}", groups=g, explode=ex(inward, 2, 180))
    add(f"lower-channel-{n}", groups=g, explode=ex(UP, 3, 200))
    add(f"remote-control-{n}", groups=g, explode=ex(inward, 3, 140))
    add(f"lock-{n}", groups=g, explode=ex(FWD, 3, 120))
    add(f"lock-barrel-{n}", groups=g, explode=ex(out, 4, 100))
    add(f"check-strap-{n}", groups=g, explode=ex(BACK, 4, 100))
    add(f"striker-backing-{n}", groups=g, explode=ex(BACK, 4, 60))
    add(f"door-seal-{n}", groups=g, explode=ex(out, 4, 80))

INSTANCES = I
