"""Rear drum brakes on the banjo axle, wire wheels (Haynes Ch 9 Fig 9.9; Secs 13-15).

Drawn at the left-hand wheel in the axle frame (mgb.rear_axle_layout AF); the right-hand wheel's parts are
turned half round z, except the handed backplate, handbrake lever and lever boot, which have mirrored parts.
Explode stages (each side outward), in the Haynes order:
  Sec 13 para 3  the four drum nuts off, the drum off                               orders 1-2
  Sec 13 para 4  steady washers pressed and turned, springs and pins out; the shoes
                 off together with the pull-off springs                             orders 3-5
  Sec 13 para 5  the two nuts and washers behind the backplate, the adjuster off,
                 the tappets and wedge out                                          orders 6-8
  Sec 14         the boots, pistons and seals out of the wheel cylinder; the clip
                 off and the cylinder out with the handbrake lever and its boot     orders 9-12
  Sec 15         the four bolts, nuts and washers; the backplate off                orders 13-14
"""
from build123d import Location, Rot

from mgb import brake_layout as B, rear_axle_layout as A
from parts.brakes import rear as R

ID = "brakes.rear"
NAME = "Rear drum brakes"
PARENT = "brakes"
HAYNES = {"figures": [{"figure": "9.9"}], "section": 13}

LEFT, RIGHT, FWD, BACK, UP, DOWN = [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]
GROUPS = {}
for k, ax in (("l", LEFT), ("r", RIGHT)):
    GROUPS[f"drum-{k}"] = {"axis": ax, "order": 2, "distance_mm": 230}
    GROUPS[f"shoes-{k}"] = {"axis": ax, "order": 5, "distance_mm": 150}
    GROUPS[f"adjuster-{k}"] = {"axis": ax, "order": 7, "distance_mm": 90}
    GROUPS[f"cylinder-{k}"] = {"axis": ax, "order": 12, "distance_mm": 110}
    GROUPS[f"backplate-{k}"] = {"axis": ax, "order": 14, "distance_mm": 120}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "brakes.rear." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


AF = A.AF
FLIP_X = Location((0, 0, 0)) * Rot(0, 180, 0)          # about the axle axis: front shoe -> rear shoe


def about_z(z):
    """Half turn about the axle-parallel line at height z through x = 0 (rear piston, tappet)."""
    return Location((0, 0, 2 * z)) * Rot(0, 180, 0)


for s in (1, -1):
    F = AF if s > 0 else AF * Rot(0, 0, 180)
    out = LEFT if s > 0 else RIGHT
    inn = RIGHT if s > 0 else LEFT
    k = "l" if s > 0 else "r"
    fwd = FWD if s > 0 else BACK
    hand = "lh" if s > 0 else "rh"
    # drum and nuts
    for a in A.STUD_ANGLES:
        x, z = R._pt(A.STUD_PCD / 2, a)
        add("drum-nut", F * Location((x, B.DRUM_PLATE_Y[1], z)) * Rot(-90, 0, 0), explode=ex(out, 1, 60))
    add("drum", F, groups=[f"drum-{k}"])
    # steady pins, springs, washers
    for fl in (Location((0, 0, 0)), FLIP_X):
        add("steady-washer", F * fl, explode=ex(out, 3, 60))
        add("steady-spring", F * fl, explode=ex(out, 3, 40))
        add("steady-pin", F * fl, explode=ex(inn, 3.5, 60))
    # shoes, linings, pull-off springs
    for fl in (Location((0, 0, 0)), FLIP_X):
        add("shoe", F * fl, groups=[f"shoes-{k}"])
        add("lining", F * fl, groups=[f"shoes-{k}"])
    add("pull-off-spring-adjuster", F, groups=[f"shoes-{k}"], explode=ex(UP, 4.5, 40))
    add("pull-off-spring-cylinder", F, groups=[f"shoes-{k}"], explode=ex(DOWN, 4.5, 40))
    # adjuster
    for sx in (1, -1):
        wl = F * Location((sx * B.ADJ_STUD_X, 581.0, B.ADJ_Z)) * Rot(90, 0, 0)
        add("adjuster-spring-washer", wl, explode=ex(inn, 6, 30))
        add("adjuster-nut", wl * Location((0, 0, 1.6)), explode=ex(inn, 6, 50))
    add("adjuster-body", F, groups=[f"adjuster-{k}"])
    add("wedge", F, groups=[f"adjuster-{k}"], explode=ex(inn, 8, 50))
    add("tappet", F, groups=[f"adjuster-{k}"], explode=ex(fwd, 8, 30))
    add("tappet", F * about_z(B.ADJ_Z), groups=[f"adjuster-{k}"], explode=ex([-v for v in fwd], 8, 30))
    # wheel cylinder
    for fl, d in ((Location((0, 0, 0)), fwd), (about_z(B.WC_Z), [-v for v in fwd])):
        add("wc-boot", F * fl, explode=ex(d, 9, 45))
        add("wc-piston", F * fl, explode=ex(d, 10, 35))
        add("wc-seal", F * fl, explode=ex(d, 10, 25))
    add("wc-clip", F, explode=ex(DOWN, 11, 40))
    add("wc-bleed-screw", F, groups=[f"cylinder-{k}"], explode=ex(UP, 9, 30))
    add("wheel-cylinder", F, groups=[f"cylinder-{k}"])
    add(f"hb-lever-{hand}", AF, groups=[f"cylinder-{k}"], explode=ex(BACK, 12.5, 40))
    add(f"hb-lever-boot-{hand}", AF, explode=ex(inn, 12.5, 30))
    # backplate and its fixings
    for a in A.BACKPLATE_BOLT_ANGLES:
        x, z = R._pt(A.BACKPLATE_BOLT_PCD / 2, a)
        add("backplate-bolt", F * Location((x, B.BP_FACE_Y + B.BP_T, z)) * Rot(90, 0, 0), explode=ex(out, 13, 90))
        wl = F * Location((x, B.BP_FACE_Y - A.BACKPLATE_FLANGE_T, z)) * Rot(90, 0, 0)
        add("backplate-spring-washer", wl, explode=ex(inn, 13, 30))
        add("backplate-nut", wl * Location((0, 0, 1.2)), explode=ex(inn, 13, 50))
    add(f"backplate-{hand}", AF, groups=[f"backplate-{k}"])
INSTANCES = I
