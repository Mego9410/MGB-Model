"""Remote control, overdrive cars: housing, selector lever shaft, gear lever and knob, plungers,
detents, isolation switch, dipstick and support bracket (Haynes Ch 6 Fig 6.4; Sec 4 paras 2, 4;
Sec 5 paras 29-31).

Built in the gearbox frame (mgb.gearbox_layout GF). Explode stages (shared numbering):
  Sec 4 para 2   dipstick out                                                    order 2
  Sec 4 para 4   remote housing bolts out, the housing lifted off back and up
                 (its shaft slides out of the front selector lever)              orders 3-4
  Sec 5 para 29  circlip off, pins out, the lever out with its cover and spring  orders 47-48
  Sec 5 para 30  reverse plunger: screw (plug), spring and ball, then the plunger
                 and spring; the spring plunger and cap; switch and its plunger   orders 49-50
  (rear lever, shaft and keys)                                                   order 51
"""
from build123d import Location, Rot

from mgb import gearbox_layout as G
from parts.gearbox import casing as C, remote as R, selectors as SE

ID = "gearbox.remote"
NAME = "Remote control and gear lever"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.4"}], "section": 4}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
LIFT = [-0.6, 0.0, 0.8]
GROUPS = {"remote": {"axis": LIFT, "order": 4, "distance_mm": 260},
          "lever": {"axis": UP, "order": 48, "distance_mm": 160}}
RM = ["remote"]
LV = RM + ["lever"]


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.remote." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF

add("dipstick", GF, explode=ex(UP, 2, 260))
top = R.FL_UP + 14.0
for l, d in C.AD_TOP_BOLTS:
    add("housing-washer", GF * Location((top, l, d)) * Rot(0, 90, 0), explode=ex(UP, 3, 50))
    add("housing-bolt", GF * Location((top + 2.0, l, d)) * Rot(0, -90, 0), explode=ex(UP, 3, 90))
add("gasket", GF, explode=ex(UP, 5, 30))
add("dowel", GF, explode=ex(UP, 5, 15))
add("housing", GF, groups=RM)
add("welch-plug", GF, groups=RM, explode=ex(BACK, 51, 40))

# shaft and the rear lever
add("shaft", GF, groups=RM, explode=ex(BACK, 51.5, 220))
add("key", GF, groups=RM, explode=ex(UP, 51.7, 30))
add("key", GF * Location((0, 0, sum(R.REAR_LEVER_D) / 2 - sum(SE.LEVER_HUB) / 2)), groups=RM, explode=ex(UP, 51.7, 30))
add("rear-screw", GF, groups=RM, explode=ex(UP, 51, 60))
add("rear-lever", GF, groups=RM, explode=ex(DOWN, 51.8, 60))

# gear lever in its socket
add("circlip", GF, groups=RM, explode=ex(UP, 47, 120))
add("pin-washer", GF, groups=RM, explode=ex(FWD, 47.5, 50))
add("locating-pin", GF, groups=RM, explode=ex(FWD, 47.5, 80))
add("cover", GF, groups=LV, explode=ex(UP, 48.5, 40))
add("ball-spring", GF, groups=LV, explode=ex(UP, 48.5, 20))
add("gear-lever", GF, groups=LV)
add("knob-locknut", GF, groups=LV, explode=ex(UP, 48.7, 40))
add("knob", GF, groups=LV, explode=ex(UP, 48.7, 70))
add("knob-print", GF, groups=LV, explode=ex(UP, 48.7, 70))

# plungers and detents (Sec 5 para 30)
add("retainer-plug", GF, groups=RM, explode=ex(DOWN, 49, 50))
add("plug-washer", GF, groups=RM, explode=ex(DOWN, 49, 35))
add("detent-spring", GF, groups=RM, explode=ex(DOWN, 49.2, 30))
add("detent-ball", GF, groups=RM, explode=ex(DOWN, 49.2, 20))
add("reverse-peg", GF, groups=RM, explode=ex(UP, 49.4, 30))
add("reverse-plunger", GF, groups=RM, explode=ex(RIGHT, 49.6, 60))
add("reverse-spring", GF, groups=RM, explode=ex(RIGHT, 49.6, 40))
add("cap", GF, groups=RM, explode=ex(LEFT, 49.8, 70))
add("cap-washer", GF, groups=RM, explode=ex(LEFT, 49.8, 50))
add("plunger-spring", GF, groups=RM, explode=ex(LEFT, 49.9, 40))
add("plunger", GF, groups=RM, explode=ex(LEFT, 49.9, 25))
add("isolation-switch", GF, groups=RM, explode=ex(RIGHT, 50, 70))
add("switch-gasket", GF, groups=RM, explode=ex(RIGHT, 50, 50))
add("switch-spring", GF, groups=RM, explode=ex(RIGHT, 50.2, 40))
add("switch-plunger", GF, groups=RM, explode=ex(RIGHT, 50.2, 30))
add("switch-pin", GF, groups=RM, explode=ex(UP, 50.1, 30))
add("detent-plug", GF, groups=RM, explode=ex(LEFT, 50.4, 50))
add("detent-plunger", GF, groups=RM, explode=ex(LEFT, 50.4, 30))

# support bracket under the turret feet
(d, la), (_, lb) = R.FEET
for l in (la, lb):
    add("bracket-washer", GF * Location((R.FLOOR_UP + 8.0, l, d)) * Rot(0, 90, 0), groups=RM, explode=ex(UP, 3.5, 40))
    add("bracket-bolt", GF * Location((R.FLOOR_UP + 10.0, l, d)) * Rot(0, -90, 0), groups=RM, explode=ex(UP, 3.5, 70))
for l in G.REMOTE_BRACKET_HOLES:
    add("bracket-screw", GF * Location((G.REMOTE_BRACKET_UP + 3.0, l, d)) * Rot(0, -90, 0), explode=ex(UP, 3.2, 50))
add("bracket", GF, explode=ex(DOWN, 3.6, 60))
INSTANCES = I
