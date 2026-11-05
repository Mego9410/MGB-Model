"""Remote control, overdrive cars: remote control housing (tower) on the gearbox adaptor, the
selector lever shaft with its rear lever, the gear lever and knob, the plungers, detents, the
overdrive isolation switch, the dipstick, the rear support bracket and the fixings.
Haynes Ch 6: Fig 6.4 (remote control arrangement, overdrive fitted, printed p116) items 1, 3,
10-15, 17, 19-29, 33-41, 44-48, 51, 53-54; Sec 2 para 1 (dipstick under a rubber cover in the
tunnel), Sec 4 paras 2, 4; Sec 5 paras 29-31 (control tower).
Not fitted to this car: item 52 (alternative reverse plunger), items 55-56 (reverse light switch,
later cars).

Built in the gearbox frame (mgb.gearbox_layout GF): local z rearward from the casing front face,
x up, y to the car's left.

Forms (Fig 6.4): a cast housing with a flanged front box that bolts down on the adaptor (gasket
29, dowel 12), a tube running back over the overdrive carrying the selector lever shaft (37), and
at the back the lever turret: a round socket the gear lever ball sits in under its spring (19),
cover (20) and circlip (21), with the locating pin (17) in the ball's slot, the reverse plunger
(22) and its ball detent (25-28) on one side and the spring plunger (33-36) on the other. Two
feet under the turret bolt (40, 41) to the support bracket (39). The shaft end is closed by a
Welch plug (13).
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Plane, Polygon, Rot, Sphere, Torus, extrude, \
    Circle, Polyline, sweep, Transition, loft

from mgb import fasteners as F, gearbox_layout as G, probes, shapes as Sh
from mgb.poly2d import ccw, circle_pts, grow, hull, inset
from parts.gearbox import casing as C
from parts.gearbox import selectors as SE

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
IN = 25.4
SU, SL = G.SEL_SHAFT_UP, G.SEL_SHAFT_LEFT
BALL_D = G.LEVER_BALL_D
BALL_U = G.LEVER_BALL_UP
BALL_R = 12.7
FRONT = (C.AD_D0 + 4.0, C.AD_D1 - 4.0)            # front box on the adaptor pad
FL_UP = C.AD_TOP + G.JOINT_T                      # flange underside, on the gasket on the adaptor
TUBE_R = 15.0
TUBE_D = (FRONT[1] - 6.0, G.REMOTE_D[1] - 18.0)
TURRET_R = 27.0
TURRET_TOP = BALL_U + 22.0
FLOOR_UP = G.REMOTE_BOTTOM_UP + 3.0
SHAFT_D = (FRONT[0] + 8.0, G.REMOTE_D[1] - 10.0)
REAR_LEVER_D = (BALL_D - 7.0, BALL_D + 7.0)
LEVER_END_UP = BALL_U - 23.0                      # lower ball end of the gear lever, in the rear lever's socket
FEET = [(G.REMOTE_BRACKET_D, G.REMOTE_FEET_LEFT[0]), (G.REMOTE_BRACKET_D, G.REMOTE_FEET_LEFT[1])]   # (d, left)
PIN_D0 = REAR_LEVER_D[0] - 22.0 - 8.0             # front face of the locating pin boss
DIP = (-26.0, FRONT[0] + 13.0)                    # dipstick (left, d)
DIP_LOW = -46.0                                   # dipstick blade tip (local up)
SWITCH_D = 360.0                                  # overdrive isolation switch station
DETENT_D = 382.0
PL_U = BALL_U + 1.0                               # the two plungers bear on the lever ball's equator
COVER_U = BALL_U + 15.8                           # underside of the lever cover's flange
CLIP_U = COVER_U + 1.3                            # circlip above it
SW_L0 = SL - TUBE_R - 18.0                        # outer face of the isolation switch boss
DET_L = -36.0                                     # reverse detent bore, under the reverse plunger
DET_LUG = FLOOR_UP + 7.0                          # bottom face of its lug, clear of the bracket


def _l(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def ucyl(r, u0, u1, l, d):
    """Vertical cylinder (along local up) from u0 to u1 at (left l, station d)."""
    return Location((u0, l, d)) * Rot(0, 90, 0) * Cylinder(r, u1 - u0, align=BASE)


def ycyl(r, l0, l1, u, d):
    """Cylinder across the car (along local y) from l0 to l1."""
    return Location((u, l0, d)) * Rot(-90, 0, 0) * Cylinder(r, l1 - l0, align=BASE)


def zprism(pts, z0, z1):
    return extrude(Polygon(*ccw(pts), align=None), z1 - z0).moved(Location((0, 0, z0)))


def rounded_prism(pts, z0, z1, r):
    """Prism with its fore-and-aft edges rounded (cast corners)."""
    from build123d import Axis, fillet
    p = zprism(pts, z0, z1)
    try:
        q = fillet(p.edges().filter_by(Axis.Z), r)
        return q if q.is_valid else p
    except Exception:
        return p


# ---- remote control housing (item 11) ------------------------------------------------------------
def housing(spec) -> Part:
    pad = [(FL_UP, C.AD_PAD[0] + 1), (FL_UP, C.AD_PAD[1] - 1), (FL_UP + 8, C.AD_PAD[1] - 1), (FL_UP + 8, C.AD_PAD[0] + 1)]
    h = box(FL_UP, FL_UP + 8.0, C.AD_PAD[0] + 1.0, C.AD_PAD[1] - 1.0, FRONT[0], FRONT[1])        # flange
    # front box over the front selector lever, with sloping cheeks up to the shaft
    fb = rounded_prism([(FL_UP + 6, -36.0), (FL_UP + 6, 72.0), (SU + 14.0, 72.0), (SU + 24.0, 58.0), (SU + 24.0, -10.0),
                        (FL_UP + 26.0, -36.0)], FRONT[0] + 4.0, FRONT[1] + 2.0, 5.0)
    h = h + fb
    # triangular web from the front box down onto the tube (Fig 6.4)
    web = extrude(Plane(origin=(0, SL - 3.0, 0), x_dir=(0, 0, 1), z_dir=(0, 1, 0)) * Polygon((FRONT[1] - 14.0, SU + 23.0), (FRONT[1] + 1.0, SU + 23.0),
                                                       (FRONT[1] + 46.0, SU + TUBE_R - 2.0), (FRONT[1] - 14.0, SU + TUBE_R - 2.0),
                                                       align=None), 6.0)
    h = h + web
    for l, d in C.AD_TOP_BOLTS:                                                       # bolt bosses
        h = h + ucyl(8.0, FL_UP, FL_UP + 14.0, l, d)
    h = h + ucyl(9.0, FL_UP, SU + 28.0, DIP[0], DIP[1])                               # dipstick boss
    # tube back to the turret
    h = h + zc(TUBE_R, TUBE_D[0], TUBE_D[1], SU, SL)
    h = h + box(SU - 4.0, SU + 4.0, SL - TUBE_R - 4.0, SL - TUBE_R + 6.0, TUBE_D[0], TUBE_D[1])   # rib under the tube
    # turret: the gear lever socket, and the rear chamber round the rear lever
    h = h + ucyl(TURRET_R, FLOOR_UP - 3.0, TURRET_TOP, 0.0, BALL_D)
    h = h + rounded_prism([(FLOOR_UP - 3.0, -22.0), (FLOOR_UP - 3.0, SL + 18.0), (SU + 16.0, SL + 18.0), (SU + 20.0, SL),
                           (SU + 20.0, -10.0), (BALL_U, -22.0)], REAR_LEVER_D[0] - 22.0, G.REMOTE_D[1], 4.0)
    for d, l in FEET:                                                                 # feet on the bracket
        h = h + ucyl(9.0, G.REMOTE_BOTTOM_UP, FLOOR_UP + 8.0, l, d)
        h = h + box(G.REMOTE_BOTTOM_UP + 2.0, FLOOR_UP + 6.0, min(l, 0) - 2, max(l, 0) + 2, d - 4.0, d + 4.0)
    # side bosses: isolation switch (right of the tube), detent plug (left), plungers on the turret
    h = h + ycyl(11.0, SW_L0, SL, SU, SWITCH_D)
    h = h + ycyl(7.5, SL, SL + TUBE_R + 8.0, SU, DETENT_D)
    h = h + ycyl(8.5, -SIDE_R0, 0.0, PL_U, BALL_D)                            # reverse plunger boss (right)
    h = h + ycyl(8.5, 0.0, SIDE_LL0, PL_U, BALL_D)                            # spring plunger boss (left)
    h = h + Location((BALL_U - 2.0, 0.0, PIN_D0)) * Cylinder(8.0, BALL_D - TURRET_R - PIN_D0 + 4.0, align=BASE)  # locating pin boss
    h = h + box(DET_LUG, PL_U, DET_L - 7.0, DET_L + 7.0, BALL_D - 7.0, BALL_D + 7.0)          # reverse detent lug
    # ---- cavities ----
    h = h - zprism([(FL_UP - 1, -30.0), (FL_UP - 1, 66.0), (SU + 8.0, 66.0), (SU + 18.0, 54.0), (SU + 18.0, -4.0),
                    (FL_UP + 20.0, -30.0)], FRONT[0] + 8.0, FRONT[1] - 2.0)
    h = h - zprism([(FLOOR_UP, -16.0), (FLOOR_UP, SL + 12.0), (SU + 12.0, SL + 12.0), (SU + 15.0, SL),
                    (SU + 15.0, -4.0), (BALL_U - 8.0, -16.0)], REAR_LEVER_D[0] - 16.0, G.REMOTE_D[1] - 6.0)
    h = h - zc(7.05, SHAFT_D[0] - 4.0, G.REMOTE_D[1] + 1, SU, SL)                    # shaft bore
    h = h - zc(9.5, G.REMOTE_D[1] - 4.0, G.REMOTE_D[1] + 1, SU, SL)                  # Welch plug recess
    h = h - ucyl(BALL_R + 0.2, BALL_U - 30.0, TURRET_TOP + 1, 0.0, BALL_D)          # ball seat and lever passage
    h = h - ucyl(20.0, BALL_U + 2.0, TURRET_TOP + 1, 0.0, BALL_D)                   # spring and cover recess
    h = h - ucyl(21.6, CLIP_U - 0.1, CLIP_U + 1.4, 0.0, BALL_D)                      # circlip groove
    h = h - ucyl(4.0, FL_UP - 1, SU + 29.0, DIP[0], DIP[1])                          # dipstick hole
    h = h - ucyl(5.7, SU + 16.0, SU + 29.0, DIP[0], DIP[1])                          # its plug's bore
    for l, d in C.AD_TOP_BOLTS:
        h = h - ucyl(4.2, FL_UP - 1, FL_UP + 15.0, l, d)
    l, d = C.AD_DOWEL
    h = h - ucyl(3.0, FL_UP - 1, FL_UP + 6.0, l, d)
    for d, l in FEET:
        h = h - ucyl(4.2, G.REMOTE_BOTTOM_UP - 1, FLOOR_UP + 9.0, l, d)
    h = h - ycyl(7.5, SW_L0 - 1.0, SW_L0 + 10.0, SU, SWITCH_D)                        # switch thread
    h = h - ycyl(3.2, SW_L0 - 1.0, SL, SU, SWITCH_D)
    h = h - ucyl(1.25, SU + 1.0, SU + 12.0, SW_L0 + 22.0, SWITCH_D + 4.2)              # plunger locating pin
    h = h - ycyl(4.0, SL, SL + TUBE_R + 9.0, SU, DETENT_D)
    h = h - box(FLOOR_UP - 4.0, FLOOR_UP + 1.0, -8.0, 8.0, REAR_LEVER_D[0] - 2.0, REAR_LEVER_D[1] + 2.0)   # well under the lever end
    h = h - ycyl(4.6, -SIDE_R0 - 1.0, 0.0, PL_U, BALL_D)
    h = h - ucyl(3.4, DET_LUG - 1.0, PL_U, DET_L, BALL_D)                    # detent ball and spring bore
    h = h - ucyl(1.25, PL_U + 3.0, PL_U + 16.0, PEG_L, BALL_D)               # peg hole
    h = h - ycyl(4.6, 0.0, SIDE_LL0 + 1.0, PL_U, BALL_D)
    h = h - Location((BALL_U - 2.0, 0.0, PIN_D0 - 1.0)) * Cylinder(4.05, BALL_D - PIN_D0 - BALL_R + 3.0, align=BASE)
    return _l(h, spec)


def gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = box(FL_UP - t, FL_UP, C.AD_PAD[0] + 1.0, C.AD_PAD[1] - 1.0, FRONT[0], FRONT[1])
    g = g - box(FL_UP - t - 1, FL_UP + 1, -30.0, 66.0, FRONT[0] + 8.0, FRONT[1] - 2.0)
    for l, d in C.AD_TOP_BOLTS:
        g = g - ucyl(4.2, FL_UP - 2, FL_UP + 1, l, d)
    l, d = C.AD_DOWEL
    g = g - ucyl(3.2, FL_UP - 2, FL_UP + 1, l, d)
    return _l(g, spec)


def dowel(spec) -> Part:
    l, d = C.AD_DOWEL
    L = spec.nom("length")
    return _l(Location((FL_UP - L / 2, l, d)) * Rot(0, 90, 0) * Sh.chamfered_cyl(spec.nom("diameter"), L, 0.4), spec)


def welch_plug(spec) -> Part:
    dd = spec.nom("diameter")
    p = Sh.revolved([(0, 0), (dd / 2, 0), (dd / 2, 1.5), (dd / 2 - 2.0, 2.2), (0, 3.2)])
    return _l(p.moved(Location((SU, SL, G.REMOTE_D[1] - 3.3))), spec)


# ---- selector lever shaft (item 37) and the rear lever ----------------------------------------------
def shaft(spec) -> Part:
    r = spec.nom("diameter") / 2
    s = Sh.chamfered_cyl(2 * r, SHAFT_D[1] - SHAFT_D[0], 0.6).moved(Location((SU, SL, SHAFT_D[0])))
    for d in ((SE.LEVER_HUB[0] + SE.LEVER_HUB[1]) / 2, (REAR_LEVER_D[0] + REAR_LEVER_D[1]) / 2):   # Woodruff key seats
        s = s - Location((SU + 7.0, SL, d)) * Rot(90, 0, 0) * Cylinder(6.45, 3.3)
    for dz in (-5.0, 5.0):                                                       # detent notches for the plunger (53)
        s = s - Location((SU, SL + r + 1.6, DETENT_D + dz)) * Sphere(2.6)
    s = s - Location((SU, SL - r - 2.2, SWITCH_D)) * Box(6.0, 6.0, 12.0)         # flat the switch plunger rides on
    s = s - ucyl(3.25, SU - r - 1.0, SU - r + 3.2, SL, sum(REAR_LEVER_D) / 2)    # dimple for the rear selector screw
    return _l(s, spec)


def woodruff_key(spec) -> Part:
    """1/8 x 1/2 in Woodruff key, built on the shaft at the front lever; the assembly moves it."""
    w = spec.nom("width")
    k = Location((SU + 7.0, SL, (SE.LEVER_HUB[0] + SE.LEVER_HUB[1]) / 2)) * Rot(90, 0, 0) * Cylinder(6.35, w)
    k = k & box(SU + 7.0 - 7.0, SU + 7.0 + 1.6, SL - 5, SL + 5, 0, 600)
    return _l(k, spec)


def rear_lever(spec) -> Part:
    """Lever keyed and screwed to the back of the shaft; its boss takes the ball on the lower
    end of the gear lever in a vertical socket, so moving the lever across turns the shaft and
    moving it fore and aft slides it."""
    d0, d1 = REAR_LEVER_D
    lv = zc(12.0, d0, d1, SU, SL)
    eu, el = LEVER_END_UP, 0.0
    lv = lv + zprism([(SU + 6.0, SL), (SU - 6.0, SL), (eu - 4.0, el + 9.0), (eu + 8.0, el + 9.0)], d0 + 1.0, d1 - 1.0)
    lv = lv + ucyl(11.0, eu - 10.0, eu + 8.0, el, (d0 + d1) / 2)
    lv = lv - ucyl(7.2, eu - 11.0, eu + 9.0, el, (d0 + d1) / 2)                     # socket for the lever end
    lv = lv - zc(7.05, d0 - 1, d1 + 1, SU, SL)
    lv = lv - Location((SU + 7.0, SL, (d0 + d1) / 2)) * Box(4.0, 3.2, 14.0)       # keyway
    lv = lv - ucyl(3.2, SU - 14.0, SU - 6.0, SL, (d0 + d1) / 2)                   # rear selector screw
    return _l(lv, spec)


def rear_screw(spec) -> Part:
    """Rear selector screw (item 1), up through the lever hub into the shaft."""
    b = F.hex_bolt("1/4", spec.nom("length") / IN)
    return _l(Location((SU - 12.0, SL, sum(REAR_LEVER_D) / 2)) * Rot(0, 90, 0) * b, spec)   # point in a dimple in the shaft


def screw_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) - Location(((od + id_) / 4, 0, t / 2)) * Rot(0, 0, 20) * Box(od, 1.2, t + 1)
    return _l(w, spec)


# ---- gear lever (14), knob (15) and the socket parts ---------------------------------------------
def _lever_path():
    top = G.to_local(G.KNOB)
    bend = (BALL_U + 48.0, 0.0, BALL_D + 4.0)
    return [(LEVER_END_UP, 0.0, BALL_D), (BALL_U, 0.0, BALL_D), bend, (top[0] - 30.0, 0.0, top[2] - 6.0)], top


def gear_lever(spec) -> Part:
    pts, top = _lever_path()
    r = spec.nom("diameter") / 2
    path = Polyline(*pts)
    prof = Plane(origin=pts[0], z_dir=(1, 0, 0)) * Circle(r)
    rod = sweep(prof, path=path, transition=Transition.ROUND)
    lv = rod + Sphere(BALL_R).moved(Location((BALL_U, 0.0, BALL_D)))
    lv = lv + Sphere(6.6).moved(Location((LEVER_END_UP, 0.0, BALL_D)))
    # slot in the ball for the locating pin (17), across the car
    lv = lv - Location((BALL_U - 2.0, 0.0, BALL_D - BALL_R)) * Box(6.0, 5.4, 7.0)
    # threaded top for the knob (5/16 UNF)
    a, b = pts[-1], top
    lv = lv + _between(a, (b[0] - 2.0, b[1], b[2] - 0.4), 4.0)
    return _l(lv, spec)


def _between(a, b, r):
    import numpy as np
    a, b = np.array(a), np.array(b)
    v = b - a
    L = float(np.linalg.norm(v))
    pl = Plane(origin=tuple(a), z_dir=tuple(v / L))
    return extrude(pl * Circle(r), L)


def knob(spec) -> Part:
    """Pear-shaped knob with the gear positions moulded in its top (MGOC 1G3706)."""
    top = G.to_local(G.KNOB)
    pts, _ = _lever_path()
    import numpy as np
    axis = np.array(top) - np.array(pts[-1])
    axis = axis / np.linalg.norm(axis)
    H = spec.nom("height")
    D = spec.nom("diameter")
    prof = [(0, 0), (D * 0.24, 0), (D * 0.30, H * 0.12), (D * 0.36, H * 0.42), (D * 0.47, H * 0.70), (D * 0.50, H * 0.84),
            (D * 0.44, H * 0.96), (D * 0.25, H), (0, H)]
    k = Sh.revolved(prof)
    k = k - Sh.chamfered_cyl(8.0, 22.0, 0.3)                                      # threaded insert bore
    # shift pattern on the top: an H with reverse, recessed
    for x0, y0, x1, y1 in ((-8, -6, 8, -6), (-8, 6, 8, 6), (0, -6, 0, 6), (-8, -6, -8, -12)):
        L = math.hypot(x1 - x0, y1 - y0) + 2.0
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        k = k - Location(((x0 + x1) / 2, (y0 + y1) / 2, H - 0.3)) * Rot(0, 0, ang) * Box(L, 1.4, 2.0)
    base = Location(tuple(np.array(top) - axis * (H * 0.40))) * Plane(origin=(0, 0, 0), z_dir=tuple(axis)).location
    return _l(base * k, spec)


def knob_print(spec) -> Part:
    """White fill in the knob top's engraved shift pattern (Oliver's kf122, kf145): the H with reverse, filled flush
    with the top so it reads white on the black knob."""
    top = G.to_local(G.KNOB)
    pts, _ = _lever_path()
    import numpy as np
    axis = np.array(top) - np.array(pts[-1])
    axis = axis / np.linalg.norm(axis)
    H = spec.nom("height")
    D = spec.nom("diameter")
    prof = [(0, 0), (D * 0.24, 0), (D * 0.30, H * 0.12), (D * 0.36, H * 0.42), (D * 0.47, H * 0.70), (D * 0.50, H * 0.84),
            (D * 0.44, H * 0.96), (D * 0.25, H), (0, H)]
    body = Sh.revolved(prof)
    fill = None
    for x0, y0, x1, y1 in ((-8, -6, 8, -6), (-8, 6, 8, 6), (0, -6, 0, 6), (-8, -6, -8, -12)):
        L = math.hypot(x1 - x0, y1 - y0) + 1.6
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        b = Location(((x0 + x1) / 2, (y0 + y1) / 2, H - 0.7)) * Rot(0, 0, ang) * Box(L, 1.2, 1.2)
        fill = b if fill is None else fill + b
    fill = fill & body
    base = Location(tuple(np.array(top) - axis * (H * 0.40))) * Plane(origin=(0, 0, 0), z_dir=tuple(axis)).location
    return _l(base * fill, spec)


def knob_locknut(spec) -> Part:
    """Thin locknut under the knob (MGOC FNP205, 5/16 UNF)."""
    top = G.to_local(G.KNOB)
    pts, _ = _lever_path()
    import numpy as np
    axis = np.array(top) - np.array(pts[-1])
    axis = axis / np.linalg.norm(axis)
    n = F.hex_nut("5/16")
    from build123d import scale
    n = scale(n, by=(1, 1, 0.6))
    H = 52.0
    base = Location(tuple(np.array(top) - axis * (H * 0.40 + 4.6))) * Plane(origin=(0, 0, 0), z_dir=tuple(axis)).location
    return _l(base * n, spec)


def ball_spring(spec) -> Part:
    L = spec.nom("free_length")
    c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, 5)
    return _l(Location((COVER_U - L, 0.0, BALL_D)) * Rot(0, 90, 0) * c, spec)


def cover(spec) -> Part:
    """Top-hat cover (20): its flange presses the spring down on the ball and sits under the
    circlip; the lever passes up through its neck."""
    c = Sh.revolved([(9.0, 0), (19.6, 0), (19.6, 1.2), (12.0, 1.2), (12.0, 11.0), (9.0, 11.0)])
    return _l(Location((COVER_U, 0.0, BALL_D)) * Rot(0, 90, 0) * c, spec)


def circlip(spec) -> Part:
    z0 = CLIP_U
    r = Sh.revolved([(17.0, 0), (21.4, 0), (21.4, 1.3), (17.0, 1.3)])
    r = r - Location((19.0, 0, 0.6)) * Box(6, 3, 3)
    for s in (-1, 1):                                                           # eyes for the pliers
        r = r + Location((17.0, s * 3.5, 0)) * Cylinder(2.2, 1.3, align=BASE) - Location((17.0, s * 3.5, -1)) * Cylinder(0.8, 4, align=BASE)
    return _l(Location((z0, 0.0, BALL_D)) * Rot(0, 90, 0) * r, spec)


def locating_pin(spec) -> Part:
    """Screwed pin through the turret wall into the slot in the gear lever ball (item 17)."""
    L = spec.nom("length")
    p = Sh.revolved([(0, 0), (3.0, 0), (3.0, L - 10.0), (4.0, L - 10.0), (4.0, L), (0, L)])
    from build123d import RegularPolygon
    p = p + extrude(RegularPolygon(6.5, 6), 5.0).moved(Location((0, 0, L)))
    return _l(Location((BALL_U - 2.0, 0.0, BALL_D - BALL_R + 2.0)) * Rot(180, 0, 0) * p, spec)   # hex outside the boss


def pin_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), t)
    return _l(Location((BALL_U - 2.0, 0.0, PIN_D0 - t)) * w, spec)


def _side_bore(left_sign):
    """Frame for a part in a turret side bore: local z inward toward the lever."""
    l0 = SIDE_LL0 if left_sign > 0 else -SIDE_R0
    return Location((PL_U, l0, BALL_D)) * Rot(left_sign * 90.0, 0, 0)


SIDE_L0 = TURRET_R + 9.0                          # (kept for reference)
SIDE_R0, SIDE_LL0 = 50.0, SL + 18.0               # boss faces of the reverse (right) and spring (left) bores
REV_PLUNGER_L, PLUNGER_L = 26.0, 30.0
TIP_R, TIP_L = SIDE_R0 - BALL_R, SIDE_LL0 - BALL_R   # bore depths at which the plungers meet the ball


def reverse_plunger(spec) -> Part:
    """Reverse selector plunger (22): spring loaded against the lever ball; the lever must push
    past it to reach reverse. Its peg (24) runs in the slot; the ball (25) clicks into its notch."""
    L = spec.nom("length")
    p = Sh.revolved([(0, 0), (4.4, 0), (4.4, L - 2.0), (2.6, L), (0, L)])
    p = p - Location((4.4, 0, L * 0.45)) * Box(2.4, 2.6, 8.0)                 # slot for the peg
    p = p - Location((-5.8, 0, (SIDE_R0 + DET_L) - (TIP_R - L))) * Sphere(3.4)    # notch for the detent ball
    return _l(_side_bore(-1) * Location((0, 0, TIP_R - L)) * p, spec)


def plunger_spring(name_r=3.5):
    def b(spec):
        L = spec.nom("free_length")
        c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, 7)
        sign = -1 if "reverse" in spec.id else 1
        z1 = (TIP_R - REV_PLUNGER_L) if sign < 0 else (TIP_L - PLUNGER_L)      # behind its plunger
        return _l(_side_bore(sign) * Location((0, 0, z1 - L)) * c, spec)
    return b


PEG_L = -SIDE_R0 + (TIP_R - REV_PLUNGER_L) + REV_PLUNGER_L * 0.45     # across the plunger's slot


def reverse_peg(spec) -> Part:
    """Peg (24) down through the turret wall into the plunger's slot."""
    L = spec.nom("length")
    p = Sh.chamfered_cyl(2.4, L, 0.3)
    return _l(Location((PL_U + 3.4, PEG_L, BALL_D)) * Rot(0, 90, 0) * p, spec)


def detent_ball(spec) -> Part:
    """Ball (25) pressed up into the reverse plunger's notch by its spring (26)."""
    r = spec.nom("diameter") / 2
    return _l(Sphere(r).moved(Location((PL_U - 4.6 - 1.2, DET_L, BALL_D))), spec)


def detent_spring(spec) -> Part:
    L = spec.nom("free_length")
    c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, 7)
    top = PL_U - 4.6 - 1.2 - 3.0
    return _l(Location((top - L, DET_L, BALL_D)) * Rot(0, 90, 0) * c, spec)


def retainer_plug(spec) -> Part:
    """Spring retainer plug (27) closing the detent bore from below, washer (28) under its head."""
    from build123d import RegularPolygon
    L = spec.nom("length")
    p = Sh.chamfered_cyl(6.8, L, 0.5) + extrude(RegularPolygon(6.5, 6), 5.0).moved(Location((0, 0, -5.0)))
    return _l(Location((DET_LUG - 1.2, DET_L, BALL_D)) * Rot(0, 90, 0) * p, spec)


def plug_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), t)
    return _l(Location((DET_LUG - t, DET_L, BALL_D)) * Rot(0, 90, 0) * w, spec)


def spring_plunger(spec) -> Part:
    """Plunger (33) pressing the lever toward the 3rd/4th plane."""
    L = spec.nom("length")
    p = Sh.revolved([(0, 0), (4.4, 0), (4.4, L - 1.0), (3.4, L), (0, L)])
    return _l(_side_bore(1) * Location((0, 0, TIP_L - L)) * p, spec)


def cap(spec) -> Part:
    """Cap (35) screwed into the plunger bore, washer (36) under its head."""
    from build123d import RegularPolygon
    L = spec.nom("length")
    c = Sh.chamfered_cyl(9.0, L, 0.4) + Sh.revolved([(0, -1.3), (4.0, -1.3), (4.0, 0.1), (0, 0.1)])
    c = c + extrude(RegularPolygon(8.0, 6), 6.0).moved(Location((0, 0, -7.2)))
    return _l(_side_bore(1) * c, spec)


def cap_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), t)
    return _l(_side_bore(1) * Location((0, 0, -t)) * w, spec)


def isolation_switch(spec) -> Part:
    """Overdrive isolation switch (44): hex body screwed into the housing with a terminal block,
    closed by the plunger only in third and top (MGOC BAU1074)."""
    from build123d import RegularPolygon
    t = 0.8                                                                     # the gasket under the hex
    s = Sh.chamfered_cyl(15.0, 10.0, 0.6) + Sh.revolved([(0, -t), (7.0, -t), (7.0, 0.1), (0, 0.1)])
    s = s + extrude(RegularPolygon(12.7, 6), 7.0).moved(Location((0, 0, -7.0 - t)))
    s = s + Sh.revolved([(0, -7.0 - t), (11.0, -7.0 - t), (11.0, -17.0 - t), (9.0, -19.0 - t), (0, -19.0 - t)])
    for dy in (-4.5, 4.5):                                                      # two blade terminals
        s = s + Location((0, dy, -24.0 - t)) * Box(6.4, 0.8, 10.0)
    return _l(Location((SU, SW_L0, SWITCH_D)) * Rot(-90, 0, 0) * s, spec)


def switch_gasket(spec) -> Part:
    t = spec.nom("thickness")
    return _l(Location((SU, SW_L0 - t, SWITCH_D)) * Rot(-90, 0, 0) * Sh.washer(20.0, 15.2, t), spec)


def switch_plunger(spec) -> Part:
    """Plunger (46) between the switch spring and the flat on the shaft."""
    L = spec.nom("length")
    p = Sh.revolved([(0, 0), (3.0, 0), (3.0, L - 1.5), (1.8, L), (0, L)])
    p = p - Location((3.0, 0, L / 2)) * Box(1.6, 8, 3.0)                       # groove for the locating pin
    l1 = SL - 7.0 + 0.8                                                        # tip on the flat of the shaft
    return _l(Location((SU, l1 - L, SWITCH_D)) * Rot(-90, 0, 0) * p, spec)


def switch_plunger_spring(spec) -> Part:
    c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("free_length"), 6)
    return _l(Location((SU, SW_L0 + 10.0, SWITCH_D)) * Rot(-90, 0, 0) * c, spec)


def switch_pin(spec) -> Part:
    """Locating pin (48) in the plunger's groove, keeping it from turning."""
    L = spec.nom("length")
    return _l(ucyl(1.2, SU + 2.4, SU + 2.4 + L, SW_L0 + 22.0, SWITCH_D + 4.2), spec)


def detent_plunger(spec) -> Part:
    """Detent plunger (53) on the shaft notches, under its plug (54)."""
    L = spec.nom("length")
    p = Sh.revolved([(0, 0), (3.6, 0), (3.6, L - 2.0), (2.0, L), (0, L)])
    return _l(Location((SU, SL + TUBE_R + 2.4, DETENT_D)) * Rot(90, 0, 0) * p, spec)


def detent_plug(spec) -> Part:
    from build123d import RegularPolygon
    p = Sh.chamfered_cyl(8.0, 6.0, 0.4) + extrude(RegularPolygon(7.0, 6), 4.0).moved(Location((0, 0, 6.0)))
    return _l(Location((SU, SL + TUBE_R + 2.5, DETENT_D)) * Rot(-90, 0, 0) * p, spec)


def dipstick(spec) -> Part:
    """Combined filler plug and dipstick (10), reached under a rubber cover in the tunnel (Sec 2)."""
    top = SU + 29.0
    stem = ucyl(2.2, DIP_LOW + 30.0, top, DIP[0], DIP[1])
    blade = box(DIP_LOW, DIP_LOW + 32.0, DIP[0] - 4.0, DIP[0] + 4.0, DIP[1] - 0.8, DIP[1] + 0.8)
    for u in (DIP_LOW + 6.0, DIP_LOW + 16.0):                                    # high and low marks
        blade = blade - box(u - 0.5, u + 0.5, DIP[0] - 5, DIP[0] + 5, DIP[1] - 1.2, DIP[1] - 0.5)
    plug = ucyl(5.5, top - 12.0, top, DIP[0], DIP[1]) + ucyl(9.0, top, top + 3.0, DIP[0], DIP[1])
    ring = Location((top + 12.0, DIP[0], DIP[1])) * Rot(90, 0, 0) * Torus(8.0, 1.8)
    d = stem + blade + plug + ring + ucyl(2.0, top + 2.0, top + 5.0, DIP[0], DIP[1])
    return _l(d, spec)


def bracket(spec) -> Part:
    """Support bracket (39) under the turret feet; its legs bolt down to the overdrive casing."""
    t = spec.nom("thickness")
    (d, la), (_, lb) = FEET
    top = G.REMOTE_BOTTOM_UP
    low = G.REMOTE_BRACKET_UP
    w = 22.0
    b = box(top - t, top, la - 12.0, lb + 12.0, d - w / 2, d + w / 2)
    for l, s in ((la - 12.0, -1), (lb + 12.0, 1)):
        b = b + box(low, top, l - (t if s > 0 else 0), l + (t if s < 0 else 0), d - w / 2, d + w / 2)
        b = b + box(low, low + t, l - (0 if s > 0 else 14.0), l + (14.0 if s > 0 else 0), d - w / 2, d + w / 2)
    for l in (la, lb):
        b = b - ucyl(4.2, top - t - 1, top + 1, l, d)
    for l in G.REMOTE_BRACKET_HOLES:
        b = b - ucyl(3.6, low - 1, low + t + 1, l, d)
    return _l(b, spec)


def bolt(size):
    def b(spec):
        return _l(F.hex_bolt(size, spec.nom("length") / IN), spec)
    return b


WASHER = {"outside_diameter": lambda p: probes.bbox_size(p, "y"), "thickness": lambda p: probes.bbox_size(p, "z")}   # y: clear of the split

PARTS = {
    "gearbox.remote.housing": {"build": housing},
    "gearbox.remote.gasket": {"build": gasket},
    "gearbox.remote.dowel": {"build": dowel},
    "gearbox.remote.welch-plug": {"build": welch_plug},
    "gearbox.remote.housing-bolt": {"build": bolt("5/16"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.remote.housing-washer": {"build": screw_washer, "probes": WASHER},
    "gearbox.remote.shaft": {"build": shaft},
    "gearbox.remote.key": {"build": woodruff_key},
    "gearbox.remote.rear-lever": {"build": rear_lever},
    "gearbox.remote.rear-screw": {"build": rear_screw},
    "gearbox.remote.gear-lever": {"build": gear_lever},
    "gearbox.remote.knob": {"build": knob},
    "gearbox.remote.knob-print": {"build": knob_print},
    "gearbox.remote.knob-locknut": {"build": knob_locknut},
    "gearbox.remote.ball-spring": {"build": ball_spring},
    "gearbox.remote.cover": {"build": cover},
    "gearbox.remote.circlip": {"build": circlip},
    "gearbox.remote.locating-pin": {"build": locating_pin},
    "gearbox.remote.pin-washer": {"build": pin_washer},
    "gearbox.remote.reverse-plunger": {"build": reverse_plunger},
    "gearbox.remote.reverse-spring": {"build": plunger_spring()},
    "gearbox.remote.reverse-peg": {"build": reverse_peg},
    "gearbox.remote.detent-ball": {"build": detent_ball, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.remote.detent-spring": {"build": detent_spring},
    "gearbox.remote.retainer-plug": {"build": retainer_plug},
    "gearbox.remote.plug-washer": {"build": plug_washer},
    "gearbox.remote.plunger": {"build": spring_plunger},
    "gearbox.remote.plunger-spring": {"build": plunger_spring()},
    "gearbox.remote.cap": {"build": cap},
    "gearbox.remote.cap-washer": {"build": cap_washer},
    "gearbox.remote.isolation-switch": {"build": isolation_switch},
    "gearbox.remote.switch-gasket": {"build": switch_gasket},
    "gearbox.remote.switch-plunger": {"build": switch_plunger},
    "gearbox.remote.switch-spring": {"build": switch_plunger_spring},
    "gearbox.remote.switch-pin": {"build": switch_pin},
    "gearbox.remote.detent-plunger": {"build": detent_plunger},
    "gearbox.remote.detent-plug": {"build": detent_plug},
    "gearbox.remote.dipstick": {"build": dipstick},
    "gearbox.remote.bracket": {"build": bracket},
    "gearbox.remote.bracket-bolt": {"build": bolt("5/16"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.remote.bracket-washer": {"build": screw_washer, "probes": WASHER},
    "gearbox.remote.bracket-screw": {"build": bolt("1/4"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
}
