"""Gear selector mechanism, early three-synchro box: selector rods and forks with their locating
bolts and locknuts, the detent block with its balls and springs, the selectors on the rod ends,
the interlock plate, and the front selector lever.
Haynes Ch 6: Fig 6.3 items 2, 49-75, 82, 119-121, 125 (printed p114-115); Sec 4 paras 6, 8-9;
Sec 7 paras 9-12, 14, 16-17 (p123); photos 4.21(a)-(c), 7.9-7.12.

Built in the gearbox frame (mgb.gearbox_layout GF): local z rearward from the casing front face,
x up, y to the car's left.

Layout (D): the three rods run high on the left of the gear train (Haynes photos 4.21a/b show
them along the top of the side cover opening), side by side; each fork is clamped to its rod by a
bolt through the fork boss into the rod with a locknut (Sec 7 para 11). The rods pass out through
the rear face and through the detent block bolted to it (two dowels, two screws; a ball and spring
from above onto each rod, Sec 7 para 10). Behind the block a selector is bolted to each rod end and
wired (Sec 7 para 12); their slots line up in neutral on an arc round the selector lever shaft, the
front selector lever's finger sits in one, and the interlock plate's two arms sit in the others
(Sec 7 para 16) so only one rod can move.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Polygon, Rot, Sphere, extrude, Plane

from mgb import fasteners as F, gearbox_layout as G, probes, shapes as Sh
from mgb.poly2d import ccw, circle_pts, hull

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
IN = 25.4
RODS = G.ROD_LEFT
RR = G.ROD_D / 2
SU, SL = G.SEL_SHAFT_UP, G.SEL_SHAFT_LEFT
SLOT_R = (40.0, 52.0)                  # selector slot, radius from the selector shaft axis (bottom, top)


def _l(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def xyprism(pts, z0, z1):
    return extrude(Polygon(*ccw(pts), align=None), z1 - z0).moved(Location((0, 0, z0)))


def ring_sector(cx, cy, r0, r1, a0, a1, z0, z1, n=24):
    """Annular sector about (cx, cy) in the (up, left) plane, angles from up toward left."""
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
             for k in range(n + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * k / n)), cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * k / n)))
             for k in range(n + 1)]
    return xyprism(outer + inner, z0, z1)


def rod_angle(key):
    """Angle (from up toward left) of a rod seen from the selector shaft axis."""
    return math.degrees(math.atan2(RODS[key] - SL, G.ROD_UP - SU)) % 360.0


# ---- rods -----------------------------------------------------------------------------------------
ROD_D0, ROD_D1 = 2.0, G.SEL_D[1] + 2.0
DETENT_D = G.CASE_LEN + 9.0            # detent notches under the balls, neutral
FORK_D = {"third-fourth": (G.SYN34[0] + G.SYN34[1]) / 2, "first-second": G.G1[0] + 4.8,
          "reverse": (G.REV_POS[0] + 10.5 + G.REV_POS[1] - 11.0) / 2}
BOSS_L = 20.0
# fork bolt direction from each rod (unit (up, left)): out to the right of the 1st/2nd rod, down from
# the 3rd/4th rod (between its neighbours) and out to the left of the reverse rod, all reachable
# through the side cover opening
BOLT_DIR = {"first-second": (0.0, -1.0), "third-fourth": (1.0, 0.0), "reverse": (0.0, 1.0)}
PAD_OFF = {"first-second": 9.0, "third-fourth": 5.0, "reverse": 9.0}   # pad centre off the rod axis
BOSS_D = {"third-fourth": FORK_D["third-fourth"], "first-second": FORK_D["first-second"] + 4.0,
          "reverse": FORK_D["reverse"] - 6.0}


def rod(key):
    def b(spec):
        y = RODS[key]
        r = Sh.chamfered_cyl(G.ROD_D, ROD_D1 - ROD_D0, 0.8).moved(Location((G.ROD_UP, y, ROD_D0)))
        for dz in (-8.0, 0.0, 8.0):                                     # three detent notches (gear, neutral, gear)
            r = r - Location((G.ROD_UP + RR + 1.2, y, DETENT_D + dz)) * Sphere(3.3)
        r = r - _along(key, 3.25, -12.0, 12.0, BOSS_D[key])                                         # fork bolt hole
        r = r - Location((G.ROD_UP, y, sum(G.SEL_D) / 2)) * Rot(0, 90, 0) * Cylinder(3.25, 20.0)    # selector bolt hole
        # interlock grooves in the rods' sides where they pass each other in the block
        return _l(r, spec)
    return b


def distance_piece(spec) -> Part:
    """Distance tube over the 3rd/4th rod (Sec 4 para 9, Sec 7 para 10)."""
    y = RODS["third-fourth"]
    z0 = BOSS_D["third-fourth"] + BOSS_L / 2 + 0.5
    L = spec.nom("length")
    return _l(Sh.tube(G.ROD_D + 5.0, G.ROD_D + 0.4, L, z0).moved(Location((G.ROD_UP, y, 0))), spec)


# ---- forks ------------------------------------------------------------------------------------------
def _along(key, r, t0, t1, z):
    """Cylinder of radius r along the fork bolt direction of a rod, from t0 to t1 off the rod axis."""
    du, dl = BOLT_DIR[key]
    from build123d import Plane as Pl
    pl = Pl(origin=(G.ROD_UP + du * t0, RODS[key] + dl * t0, z), z_dir=(du, dl, 0.0))
    return pl.location * Cylinder(r, t1 - t0, align=BASE)


def bolt_frame(key, t):
    """Frame on the fork bolt axis at t off the rod axis, local z pointing back to the rod."""
    du, dl = BOLT_DIR[key]
    from build123d import Plane as Pl
    return Pl(origin=(G.ROD_UP + du * t, RODS[key] + dl * t, BOSS_D[key]), z_dir=(-du, -dl, 0.0)).location


def _boss(key):
    y = RODS[key]
    zb = BOSS_D[key]
    du, dl = BOLT_DIR[key]
    b = Location((G.ROD_UP, y, zb - BOSS_L / 2)) * Cylinder(9.0, BOSS_L, align=BASE)
    po = PAD_OFF[key]
    b = b + Location((G.ROD_UP + du * po, y + dl * po, zb)) * Box(8.0 + 4 * abs(dl), 8.0 + 4 * abs(du), 12.0)
    return b


def _boss_holes(key):
    y = RODS[key]
    zb = BOSS_D[key]
    h = Location((G.ROD_UP, y, zb - BOSS_L)) * Cylinder(RR + 0.1, 2 * BOSS_L, align=BASE)
    h = h + _along(key, 3.18, 0.0, 20.0, zb)
    return h


def _yoke(key, r0, r1, t):
    """Half ring round the mainshaft sleeve or gear, centred toward the rod, with shoes."""
    zf = FORK_D[key]
    a = math.degrees(math.atan2(RODS[key], G.ROD_UP))
    y = ring_sector(0, 0, r0, r1, a - 80.0, a + 80.0, zf - t / 2, zf + t / 2, 32)
    for s in (-80.0, 80.0):                                                       # bronze shoes at the tips
        aa = math.radians(a + s)
        y = y + Location(((r0 + 2.5) * math.cos(aa), (r0 + 2.5) * math.sin(aa), zf)) * Rot(0, 0, a + s) * Box(5.0, 7.0, t + 0.6)
    return y


def fork_34(spec) -> Part:
    key = "third-fourth"
    zf = FORK_D[key]
    t = spec.nom("tip_thickness")
    f = _yoke(key, 34.6, 46.0, t)
    f = f + _boss(key)
    # web from the yoke crown up to the boss
    a = math.atan2(RODS[key], G.ROD_UP)
    f = f + xyprism([(44.0 * math.cos(a - 0.25), 44.0 * math.sin(a - 0.25)), (44.0 * math.cos(a + 0.25), 44.0 * math.sin(a + 0.25)),
                     (G.ROD_UP + 3.0, RODS[key] + 7.0), (G.ROD_UP - 6.0, RODS[key] - 7.0)], zf - 4.0, zf + 4.0)
    f = f - _boss_holes(key)
    return _l(f, spec)


def fork_12(spec) -> Part:
    key = "first-second"
    zf = FORK_D[key]
    t = spec.nom("tip_thickness")
    f = _yoke(key, 37.6, 48.5, t)
    f = f + _boss(key)
    a = math.atan2(RODS[key], G.ROD_UP)
    f = f + xyprism([(46.0 * math.cos(a - 0.22), 46.0 * math.sin(a - 0.22)), (46.0 * math.cos(a + 0.22), 46.0 * math.sin(a + 0.22)),
                     (G.ROD_UP + 2.0, RODS[key] + 7.0), (G.ROD_UP - 6.0, RODS[key] - 7.0)], zf - 2.5, zf + 2.5)
    f = f + box(G.ROD_UP - 12.0, G.ROD_UP - 4.0, RODS[key] - 4.0, RODS[key] + 4.0, zf - 2.5, BOSS_D[key] + BOSS_L / 2)
    f = f - _boss_holes(key)
    return _l(f, spec)


def fork_rev(spec) -> Part:
    """Reverse fork: a dog-leg arm from its rod down the left of the gears to a shoe in the
    reverse idler's groove."""
    key = "reverse"
    zf = FORK_D[key]
    t = spec.nom("tip_thickness")
    yr = RODS[key]
    f = _boss(key)
    knee = (-20.0, 64.0)
    w = 5.0
    f = f + xyprism([(G.ROD_UP, yr + w + 2), (G.ROD_UP, yr - w), (knee[0], knee[1] - w), (knee[0], knee[1] + w)],
                    zf - t / 2, zf + t / 2)
    iu, il = G.REV_UP, G.REV_LEFT
    f = f + xyprism([(knee[0] + 4, knee[1] - w), (knee[0] - 4, knee[1] + w), (iu + 8.0, il + 18.0 + w), (iu + 14.0, il + 14.0)],
                    zf - t / 2, zf + t / 2)
    ang = math.degrees(math.atan2(knee[1] - il, knee[0] - iu))
    f = f + ring_sector(iu, il, 15.6, 24.0, ang - 70.0, ang + 70.0, zf - t / 2, zf + t / 2)
    f = f + box(G.ROD_UP - 9.0, G.ROD_UP, yr - 5.0, yr + 5.0, zf - t / 2, BOSS_D[key] + BOSS_L / 2)
    f = f - _boss_holes(key)
    return _l(f, spec)


def fork_bolt(spec) -> Part:
    b = F.hex_bolt("1/4", spec.nom("length") / IN)
    return _l(b, spec)


def locknut(spec) -> Part:
    return _l(F.hex_nut("1/4"), spec)


def shakeproof(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t)
    for k in range(10):                                                           # external teeth
        w = w - Rot(0, 0, 36.0 * k) * Location((od / 2, 0, t / 2)) * Box(2.4, 1.2, t + 1)
    return _l(w, spec)


# ---- detent block (items 65-69, 2) -----------------------------------------------------------------
def _block_rect():
    from parts.gearbox.casing import BLOCK, BLOCK_T
    return BLOCK, BLOCK_T


def detent_block(spec) -> Part:
    (u0, u1, l0, l1), T = _block_rect()
    z0 = G.CASE_LEN
    b = box(u0, u1, l0, l1, z0, z0 + T)
    for key, y in RODS.items():
        b = b + Location((u1, y, z0 + 9.0)) * Rot(0, 90, 0) * Cylinder(5.5, 4.0, align=BASE)     # spring bosses
    b = b - box(u0 - 1, u0 + 5.0, l0 + 8.0, l1 - 8.0, z0 + 4.0, z0 + T + 1)      # relief under the rods
    for y in RODS.values():
        b = b - zc(RR + 0.15, z0 - 1, z0 + T + 1, G.ROD_UP, y)
        b = b - Location((G.ROD_UP, y, DETENT_D)) * Rot(0, 90, 0) * Cylinder(3.6, 40.0, align=BASE)  # ball and spring bore
    from parts.gearbox.casing import BLOCK_DOWELS, BLOCK_SCREWS
    for u, l in BLOCK_DOWELS:
        b = b - zc(3.0, z0 - 1, z0 + 8.0, u, l)
    for u, l in BLOCK_SCREWS:
        b = b - zc(3.4, z0 - 1, z0 + T + 1, u, l)
        b = b - zc(6.5, z0 + T - 6.0, z0 + T + 1, u, l)                         # counterbore
    return _l(b, spec)


def detent_ball(spec) -> Part:
    return _l(Sphere(spec.nom("diameter") / 2), spec)


def detent_spring(spec) -> Part:
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("free_length"), 8), spec)


def block_screw(spec) -> Part:
    b = F.hex_bolt("1/4", spec.nom("length") / IN)
    return _l(b, spec)


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) - Location(((od + id_) / 4, 0, t / 2)) * Rot(0, 0, 20) * Box(od, 1.2, t + 1)
    return _l(w, spec)


# ---- selectors (items 70-75) ------------------------------------------------------------------------
def selector(key):
    def b(spec):
        y = RODS[key]
        z0, z1 = G.SEL_D
        s = Location((G.ROD_UP, y, z0)) * Cylinder(7.8, z1 - z0, align=BASE)
        a = math.radians(rod_angle(key))
        # arm up toward the selector shaft, ending in a slot open to it
        cu, cl = SU + (SLOT_R[0] - 3) * math.cos(a), SL + (SLOT_R[0] - 3) * math.sin(a)
        tu, tl = SU + (SLOT_R[1] - 9) * math.cos(a), SL + (SLOT_R[1] - 9) * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        w, wt = 6.0, 4.9                                                   # half widths at the rod and at the slot
        arm = xyprism([(G.ROD_UP + nx * w, y + ny * w), (G.ROD_UP - nx * w, y - ny * w),
                       (cu - nx * wt, cl - ny * wt), (cu + nx * wt, cl + ny * wt)], z0, z1)
        s = s + arm
        slot = ring_sector(SU, SL, SLOT_R[0] - 4.0, SLOT_R[1], rod_angle(key) - 4.6, rod_angle(key) + 4.6,
                           G.FINGER_D[0] - 0.3, z1 + 1.0)
        s = s - slot
        s = s - zc(RR + 0.1, z0 - 1, z1 + 1, G.ROD_UP, y)
        s = s - Location((G.ROD_UP - 12.0, y, (z0 + z1) / 2)) * Rot(0, 90, 0) * Cylinder(3.2, 30.0, align=BASE)
        s = s - Location((G.ROD_UP - 11.0, y, (z0 + z1) / 2)) * Box(6.0, 14.0, 9.0)       # flat for the bolt head
        return _l(s, spec)
    return b


def selector_screw(spec) -> Part:
    """Locating bolt with a cross-drilled head for the locking wire (Sec 7 para 12)."""
    b = F.hex_bolt("1/4", spec.nom("length") / IN)
    b = b - Location((0, 0, -2.0)) * Rot(90, 0, 0) * Cylinder(0.7, 20.0)
    return _l(b, spec)


def locking_wire(spec) -> Part:
    """Soft wire through the three selector bolt heads (Sec 4 para 8)."""
    from build123d import Polyline, sweep, Circle, Plane as Pl
    z = sum(G.SEL_D) / 2 - 0.0
    pts = [(G.ROD_UP - 16.0, RODS["first-second"] - 6.0, z), (G.ROD_UP - 16.0, RODS["first-second"], z),
           (G.ROD_UP - 16.0, RODS["third-fourth"], z), (G.ROD_UP - 16.0, RODS["reverse"], z),
           (G.ROD_UP - 16.0, RODS["reverse"] + 6.0, z), (G.ROD_UP - 21.0, RODS["reverse"] + 9.0, z)]
    path = Polyline(*pts)
    prof = Pl(origin=pts[0], z_dir=(0, 1, 0)) * Circle(spec.nom("diameter") / 2)
    from build123d import Transition
    w = sweep(prof, path=path, transition=Transition.ROUND)
    return _l(w, spec)


# ---- interlock plate (item 82) and front selector lever (items 119-121, 125) -------------------------
def interlock_plate(spec) -> Part:
    """Plate hung on the selector shaft: two arms in the unselected selectors' slots with the
    finger between them, cheeks joining the arms inside the finger's reach, and a side plate
    that locates in its recess in the adaptor wall so the plate cannot slide (Sec 7 para 16)."""
    z0, z1 = G.FINGER_D[0] + 0.5, G.FINGER_D[1] - 0.5
    t = 2.5
    a12, arv = rod_angle("first-second"), rod_angle("reverse")
    lo, hi = min(a12, arv) - 6.0, max(a12, arv) + 6.0
    p = None
    for a in (a12, arv):                                                           # arms in the slots
        arm = ring_sector(SU, SL, SLOT_R[0] - 4.0, SLOT_R[1] - 0.6, a - 3.6, a + 3.6, z0, z1)
        p = arm if p is None else p + arm
    for zz in (z0, z1 - t):                                                        # cheeks and hub
        p = p + ring_sector(SU, SL, 9.0, SLOT_R[0] - 3.0, lo, hi, zz, zz + t)
        p = p + ring_sector(SU, SL, 9.0, 15.0, 0.0, 360.0, zz, zz + t, 36)
    # side plate (bracket) to the recess in the adaptor's right-hand wall
    p = p + box(SU - 40.0, SU - 22.0, SL - 74.0, SL - 71.0, z0, z1)
    p = p + box(SU - 26.0, SU - 22.0, SL - 74.0, SL - 10.0, z0, z0 + t)
    p = p + box(SU - 26.0, SU - 10.0, SL - 14.0, SL - 10.0, z0, z0 + t)
    p = p - zc(7.2, z0 - 1, z1 + 1, SU, SL)
    return _l(p, spec)


SHAFT_R = 7.0
LEVER_HUB = (G.SEL_D[1] + 1.0, G.SEL_D[1] + 17.0)     # behind the selectors; the finger reaches forward into the slot


def front_lever(spec) -> Part:
    """Front selector lever (item 119): hub keyed and pinch-bolted on the shaft, an arm down
    to a finger that sits in the selected selector's slot."""
    a = math.radians(rod_angle("third-fourth"))
    h0, h1 = LEVER_HUB
    lv = zc(12.0, h0, h1, SU, SL)
    lv = lv + box(SU - 6.0, SU + 6.0, SL - 24.0, SL - 10.0, h0, h1)                  # pinch lug
    tip = SLOT_R[1] - 3.0
    lv = lv + xyprism([(SU + 6.0 * math.sin(a), SL - 6.0 * math.cos(a)), (SU - 6.0 * math.sin(a), SL + 6.0 * math.cos(a)),
                       (SU + (tip - 4) * math.cos(a) - 6.0 * math.sin(a), SL + (tip - 4) * math.sin(a) + 6.0 * math.cos(a)),
                       (SU + (tip - 4) * math.cos(a) + 6.0 * math.sin(a), SL + (tip - 4) * math.sin(a) - 6.0 * math.cos(a))],
                      h0, h0 + 6.0)
    lv = lv + ring_sector(SU, SL, SLOT_R[0] - 3.0, tip, rod_angle("third-fourth") - 3.6, rod_angle("third-fourth") + 3.6,
                          G.FINGER_D[0] + 0.3, h0 + 6.0)
    lv = lv - zc(SHAFT_R + 0.05, h0 - 1, h1 + 1, SU, SL)
    lv = lv - box(SU - 1.0, SU + 1.0, SL - 26.0, SL - 4.0, h0 - 1, h1 + 1)           # pinch slot
    lv = lv - Location((SU, SL - 18.0, (h0 + h1) / 2)) * Rot(0, 90, 0) * Cylinder(3.2, 30.0)
    lv = lv - Location((SU + SHAFT_R, SL, (h0 + h1) / 2)) * Box(4.0, 3.2, 14.0)       # keyway
    return _l(lv, spec)


def pinch_bolt(spec) -> Part:
    b = F.hex_bolt("1/4", spec.nom("length") / IN)
    return _l(b, spec)


WASHER = {"outside_diameter": lambda p: probes.bbox_size(p, "y"), "thickness": lambda p: probes.bbox_size(p, "z")}   # y: clear of the split

PARTS = {
    "gearbox.selectors.rod-12": {"build": rod("first-second"), "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.selectors.rod-34": {"build": rod("third-fourth"), "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.selectors.rod-rev": {"build": rod("reverse"), "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.selectors.distance-piece": {"build": distance_piece},
    "gearbox.selectors.fork-12": {"build": fork_12},
    "gearbox.selectors.fork-34": {"build": fork_34},
    "gearbox.selectors.fork-rev": {"build": fork_rev},
    "gearbox.selectors.fork-bolt": {"build": fork_bolt},
    "gearbox.selectors.fork-washer": {"build": shakeproof, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.selectors.fork-locknut": {"build": locknut},
    "gearbox.selectors.detent-block": {"build": detent_block},
    "gearbox.selectors.detent-ball": {"build": detent_ball, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.selectors.detent-spring": {"build": detent_spring},
    "gearbox.selectors.block-screw": {"build": block_screw},
    "gearbox.selectors.block-washer": {"build": spring_washer, "probes": WASHER},
    "gearbox.selectors.selector-12": {"build": selector("first-second")},
    "gearbox.selectors.selector-34": {"build": selector("third-fourth")},
    "gearbox.selectors.selector-rev": {"build": selector("reverse")},
    "gearbox.selectors.selector-screw": {"build": selector_screw},
    "gearbox.selectors.locking-wire": {"build": locking_wire},
    "gearbox.selectors.interlock-plate": {"build": interlock_plate},
    "gearbox.selectors.front-lever": {"build": front_lever},
    "gearbox.selectors.pinch-bolt": {"build": pinch_bolt},
    "gearbox.selectors.pinch-washer": {"build": spring_washer, "probes": WASHER},
}
