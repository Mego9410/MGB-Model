"""Propeller shaft, overdrive length, non-sealed joints (Haynes Ch 7 Fig 7.1, Fig 7.4; Sec 3-4).

Placed from mgb.propshaft_layout: the front flange yoke on the overdrive coupling flange
(overdrive_layout FLANGE_*), the rear on the axle pinion flange (rear_axle_layout), the shaft
between the two joint centres 4.3 deg down toward the rear, the sliding stub at the supplier
length. Bolt heads on the yoke side, washers and self-locking nuts on the companion flanges (Fig
7.1). Explode stages follow Haynes:
  Sec 3 para 3   the self-locking nuts, washers and bolts out; the shaft lowered       orders 101-103
  Sec 4 para 3   dust cap unscrewed, the sleeve slid off the shaft; steel and cork
                 washers off the splines                                              orders 104-105
  Sec 4 para 5   circlips out, the cups tapped out                                    orders 106-107
  Sec 4 para 6   the spiders out of the yokes; lubricators, gaskets and retainers     orders 108-109
"""
import math

from build123d import Location, Rot

from mgb import propshaft_layout as P
from parts.propshaft import shaft as PS

ID = "propshaft.shaft"
NAME = "Propeller shaft"
PARENT = "propshaft"
HAYNES = {"figures": [{"figure": "7.1"}, {"figure": "7.4"}], "section": 4}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"shaft": {"axis": DOWN, "order": 103, "distance_mm": 260},
          "sleeve": {"axis": FWD, "order": 104, "distance_mm": 200},
          "front-spider": {"axis": FWD, "order": 108, "distance_mm": 60},
          "rear-spider": {"axis": BACK, "order": 108, "distance_mm": 60}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "propshaft.shaft." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def car_dir(frame, v):
    """A local direction of a frame as a car-frame list."""
    o = (frame * Location((0, 0, 0))).position
    p = (frame * Location(v)).position
    return [round(p.X - o.X, 4), round(p.Y - o.Y, 4), round(p.Z - o.Z, 4)]


C = P.FACE_TO_JOINT
R_CUP = P.CUP_SPAN / 2
TO = {"+x": Rot(0, 90, 0), "-x": Rot(0, -90, 0), "+y": Rot(-90, 0, 0), "-y": Rot(90, 0, 0)}   # local z -> that axis
VEC = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0)}
INWARD = {"+x": "-x", "-x": "+x", "+y": "-y", "-y": "+y"}


def joint(frame, groups, spider_group):
    """Spider, four cups, gaskets, retainers, circlips and the lubricator about the joint centre at
    local z = C of a flange yoke frame (journals along local x and y)."""
    jc = frame * Location((0, 0, C))
    add("spider", jc, groups=groups + [spider_group])
    d = PS._nipple_dir()
    add("lubricator", jc * PS._along(d) * Location((0, 0, PS.NIPPLE_SEAT)), groups=groups + [spider_group],
        explode=ex(car_dir(jc, d), 109, 40))
    for k in ("+x", "-x", "+y", "-y"):
        v = VEC[k]
        out = car_dir(jc, v)
        at = lambda r: jc * Location((v[0] * r, v[1] * r, v[2] * r))
        add("needle-bearing", at(R_CUP) * TO[INWARD[k]], groups=groups, explode=ex(out, 107, 60))
        add("circlip", at(R_CUP + 0.15) * TO[k], groups=groups, explode=ex(out, 106, 90))
        add("gasket", at(P.SHOULDER_R) * TO[k], groups=groups + [spider_group], explode=ex(out, 109, 14))
        add("gasket-retainer", at(P.SHOULDER_R + 1.8) * TO[k], groups=groups + [spider_group], explode=ex(out, 109, 24))


# front: flange yoke and joint go off with the sleeve; rear: with the shaft
FY, RY = P.FRONT_YOKE, P.REAR_YOKE
add("flange-yoke", FY, groups=["shaft", "sleeve"])
joint(FY, ["shaft", "sleeve"], "front-spider")
add("flange-yoke", RY, groups=["shaft"])
joint(RY, ["shaft"], "rear-spider")

# sleeve yoke, its lubricator, dust cap and washers
S = P.SHAFT
add("sleeve-yoke", S, groups=["shaft", "sleeve"])
add("sleeve-lubricator", S * Location((P.SLEEVE_R + 4.0, 0, P.NIPPLE_Z)) * Rot(0, 90, 0), groups=["shaft", "sleeve"],
    explode=ex(UP, 109, 40))
add("dust-cap", S, groups=["shaft", "sleeve"], explode=ex(BACK, 104.5, 60))
add("steel-washer", S, groups=["shaft"], explode=ex(BACK, 105, 90))
add("cork-washer", S, groups=["shaft"], explode=ex(BACK, 105, 110))

# shaft assembly at its sliding position, balance weights
add("shaft", P.SHAFT_AT_STUB, groups=["shaft"])
for z, a in ((P.STUB_LEN + P.CONE_LEN + 40.0, 90.0), (P.STUB_FRONT_TO_JOINT - P.REAR_YOKE_NECK - 46.0, 205.0)):
    add("balance-weight", P.SHAFT_AT_STUB * Location((0, 0, z)) * Rot(0, 0, a), groups=["shaft"])

# flange fixings: heads on the yoke flange's back face, washer and nut on the companion flange's ears
EAR_FACE = 13.0                                   # companion flange face to its ear (nut) face: overdrive and pinion flanges
for frame, back in ((FY, BACK), (RY, FWD)):
    for a in P.FLANGE_HOLE_ANGLES:
        r = P.PCD / 2
        x, y = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        add("flange-bolt", frame * Location((x, y, P.FLANGE_T)) * Rot(180, 0, 0), explode=ex(back, 102, 70))
        add("flange-washer", frame * Location((x, y, -EAR_FACE)) * Rot(180, 0, 0), explode=ex([-v for v in back], 101, 40))
        add("flange-nut", frame * Location((x, y, -EAR_FACE - 2.0)) * Rot(180, 0, 0), explode=ex([-v for v in back], 101, 70))
INSTANCES = I
