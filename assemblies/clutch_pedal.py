"""Clutch pedal, early cars (Haynes Ch 5 Sec 8, Fig 5.3 items 1-6). The pedal box and the
common pivot bolt come with the body (P11); positions are in mgb.clutch_layout.

Explode stages follow Sec 5 para 3 and Sec 8 (as for the brake pedal, Ch 9): the clevis pin
out of the pushrod fork, the return spring freed, the pedal off its pivot with the bush and
distance tube, then the pad off the foot plate.
"""
from build123d import Location

ID = "clutch.pedal"
NAME = "Clutch pedal"
PARENT = "clutch"
HAYNES = {"figures": [{"figure": "5.3"}], "section": 8}

LEFT, RIGHT, BACK, DOWN = [0, 1, 0], [0, -1, 0], [-1, 0, 0], [0, 0, -1]
GROUPS = {"pedal": {"axis": DOWN, "order": 3, "distance_mm": 90}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


O = Location((0, 0, 0))
INSTANCES = [
    ("clutch.pedal.clevis-pin#1", "clutch.pedal.clevis-pin", O, {"explode": ex(LEFT, 1, 50)}),
    ("clutch.pedal.return-spring#1", "clutch.pedal.return-spring", O, {"explode": ex(LEFT, 2, 40)}),
    ("clutch.pedal.pedal#1", "clutch.pedal.pedal", O, {"groups": ["pedal"]}),
    ("clutch.pedal.distance-tube#1", "clutch.pedal.distance-tube", O, {"groups": ["pedal"], "explode": ex(RIGHT, 4, 60)}),
    ("clutch.pedal.bush#1", "clutch.pedal.bush", O, {"groups": ["pedal"], "explode": ex(LEFT, 4, 40)}),
    ("clutch.pedal.pad#1", "clutch.pedal.pad", O, {"groups": ["pedal"], "explode": ex(BACK, 5, 40)}),
]
