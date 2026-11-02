"""Brake pipes, connections and hoses (Haynes Ch 9 Fig 9.1; Secs 8-9). Built in the car frame.

Explode stages, in the Haynes order (Sec 8: the pipe's union nut off the hose, the locknut and washer off, the
hose out of its bracket, then unscrewed from the connection; Sec 9 for the pipes):
  the rear hose and its fixings                                                         orders 1-3
  the axle pipes, clips and the three-way connection                                    orders 4-5
  the pipes from the four-way connection; the stop lamp switch; the connection off      orders 6-8
"""
from build123d import Location, Rot

from mgb import rear_axle_layout as A

ID = "brakes.lines"
NAME = "Brake pipes, connections and hoses"
PARENT = "brakes"
HAYNES = {"figures": [{"figure": "9.1"}], "section": 9}

UP, DOWN, FWD, BACK, LEFT, RIGHT = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]
GROUPS = {"union": {"axis": UP, "order": 5, "distance_mm": 120},
          "four-way": {"axis": FWD, "order": 8, "distance_mm": 120}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


O = Location((0, 0, 0))
I = []


def add(part, **o):
    pid = "brakes.lines." + part
    I.append((f"{pid}#1", pid, O, o))


add("rear-hose-locknut", explode=ex(UP, 1, 40))
add("rear-hose-lockwasher", explode=ex(UP, 1, 25))
add("rear-locking-plate", explode=ex(DOWN, 1.5, 30))
add("rear-hose", explode=ex(DOWN, 2, 90))
add("rear-hose-copper-washer", explode=ex(DOWN, 2.5, 40))
add("rear-hose-bracket")
add("axle-clip", explode=ex(BACK, 3.5, 40))
I.append(("brakes.lines.axle-clip#2", "brakes.lines.axle-clip", A.AF * Rot(0, 0, 180) * A.AF.inverse(),
          {"label": False, "explode": ex(BACK, 3.5, 40)}))
add("axle-pipe-lh", explode=ex(BACK, 4, 80))
add("axle-pipe-rh", explode=ex(BACK, 4, 80))
add("union-bolt", groups=["union"], explode=ex(UP, 4.5, 40))
add("union-spring-washer", groups=["union"], explode=ex(UP, 4.5, 25))
add("union", groups=["union"])
add("rear-pipe", explode=ex(DOWN, 6, 80))
add("front-pipe-lh", explode=ex(LEFT, 6, 80))
add("front-pipe-rh", explode=ex(RIGHT, 6, 80))
add("mc-pipe", explode=ex(UP, 6, 80))
add("grommet", explode=ex(UP, 6.5, 50))
add("stop-switch", explode=ex(UP, 7, 70))
add("switch-washer", explode=ex(UP, 7, 40))
add("four-way-nut", explode=ex(BACK, 7.5, 40))
add("four-way-spring-washer", groups=["four-way"], explode=ex(FWD, 7.5, 30))
add("four-way-bolt", groups=["four-way"], explode=ex(FWD, 7.5, 70))
add("four-way", groups=["four-way"])
add("four-way-spacer", groups=["four-way"], explode=ex(BACK, 8.5, 20))
INSTANCES = I
