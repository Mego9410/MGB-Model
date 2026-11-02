"""Brake pedal and the common pedal pivot (Haynes Ch 9 Sec 17 para 3, Sec 24, Fig 9.16 items 1-10).

Built in the car frame in the pedal box (brakes.master) beside the clutch pedal (clutch.pedal), which shares the
pivot bolt and spacers placed here.
Explode stages, in the Haynes order:
  Sec 17 para 3  split pin, washer and clevis pin out of the pushrod fork               orders 1-2
  Sec 24 para 2  the pull-off spring off; the nut and spring washer off the pivot bolt,
                 the bolt drawn out with the washers and spacers                         orders 3-5
                 the pedal down and out with its bush and distance tube; the pad off     orders 6-7
"""
from build123d import Location

ID = "brakes.pedal"
NAME = "Brake pedal and pedal pivot"
PARENT = "brakes"
HAYNES = {"figures": [{"figure": "9.16"}], "section": 24}

LEFT, RIGHT, BACK, DOWN = [0, 1, 0], [0, -1, 0], [-1, 0, 0], [0, 0, -1]
GROUPS = {"pedal": {"axis": DOWN, "order": 6, "distance_mm": 110}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


O = Location((0, 0, 0))
INSTANCES = [
    ("brakes.pedal.clevis-split-pin#1", "brakes.pedal.clevis-split-pin", O, {"explode": ex(LEFT, 1, 40)}),
    ("brakes.pedal.clevis-washer#1", "brakes.pedal.clevis-washer", O, {"explode": ex(LEFT, 1.5, 30)}),
    ("brakes.pedal.clevis-pin#1", "brakes.pedal.clevis-pin", O, {"explode": ex(RIGHT, 2, 50)}),
    ("brakes.pedal.return-spring#1", "brakes.pedal.return-spring", O, {"explode": ex(LEFT, 3, 40)}),
    ("brakes.pedal.pivot-nut#1", "brakes.pedal.pivot-nut", O, {"explode": ex(RIGHT, 4, 60)}),
    ("brakes.pedal.pivot-spring-washer#1", "brakes.pedal.pivot-spring-washer", O, {"explode": ex(RIGHT, 4, 40)}),
    ("brakes.pedal.pivot-bolt#1", "brakes.pedal.pivot-bolt", O, {"explode": ex(LEFT, 5, 200)}),
    ("brakes.pedal.washer-inner#1", "brakes.pedal.washer-inner", O, {"explode": ex(DOWN, 5, 60)}),
    ("brakes.pedal.spacer-inner#1", "brakes.pedal.spacer-inner", O, {"explode": ex(DOWN, 5, 70)}),
    ("brakes.pedal.spacer-centre#1", "brakes.pedal.spacer-centre", O, {"explode": ex(DOWN, 5, 80)}),
    ("brakes.pedal.spacer-outer#1", "brakes.pedal.spacer-outer", O, {"explode": ex(DOWN, 5, 70)}),
    ("brakes.pedal.washer-outer#1", "brakes.pedal.washer-outer", O, {"explode": ex(DOWN, 5, 60)}),
    ("brakes.pedal.pedal#1", "brakes.pedal.pedal", O, {"groups": ["pedal"]}),
    ("brakes.pedal.distance-tube#1", "brakes.pedal.distance-tube", O, {"groups": ["pedal"], "explode": ex(RIGHT, 6.5, 60)}),
    ("brakes.pedal.bush#1", "brakes.pedal.bush", O, {"groups": ["pedal"], "explode": ex(LEFT, 6.5, 40)}),
    ("brakes.pedal.pad#1", "brakes.pedal.pad", O, {"groups": ["pedal"], "explode": ex(BACK, 7, 40)}),
]
