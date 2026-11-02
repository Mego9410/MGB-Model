"""Laycock type D overdrive hydraulics and controls: operating pistons, bridge pieces and their nuts,
the pump cam on the mainshaft, the pump (plunger, pin, spring, body), non-return valve, relief
valve, operating valve, filter, the solenoid, operating lever and its cover (Haynes Ch 6 Fig 6.13
items 1, 11-13, 20-36, 41-50, 61-63, 92-100; Figs 6.12, 6.14, 6.15, 6.17; Sec 12-14).

Built in the gearbox frame (GF) at the overdrive stations of mgb.overdrive_layout: drawn with
z = e and moved back by O.Z0. Parts used twice (pistons, bridge pieces, nuts, lockwashers) are drawn
on their own axis and placed by the assembly.

How it works (Figs 6.14, 6.15): the cam keyed on the mainshaft drives the pump plunger; oil goes
through the non-return valve to the operating cylinders and the relief valve. With the solenoid
off, the operating valve's ball is off its seat and the oil escapes; the springs hold the cone
clutch on the annulus (direct drive). The solenoid turns the cross-shaft, whose cam lets the ball
seat 1/32 in (Sec 14 para 5); pressure builds and the pistons pull the clutch onto the brake ring.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Rot, Sphere, Torus, extrude

from mgb import fasteners as F, gearbox_layout as G, overdrive_layout as O, probes, shapes as Sh
from mgb.poly2d import rounded
from parts.gearbox import casing as C
from parts.gearbox.od_casing import CH_E0, CH_E1, CH_U0, CH_U1, CHAMBER_SCREWS, SOL_SCREWS, xcyl, ycyl

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)
zc, box = C.zc, C.box


def _out(p, spec):
    p = p.moved(Location((0, 0, O.Z0)))
    p.label = spec.id
    return p


def _l(p, spec):
    p.label = spec.id
    return p


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def vrev(profile, y=0.0, e=0.0):
    """Revolve an (r, up) profile about a vertical axis at (left y, e)."""
    return Location((0, y, e)) * Rot(0, 90, 0) * Sh.revolved(profile)


# =================================================================================================
# operating pistons (1), O-rings (61), bridge pieces (62), lockwashers (63), nuts
# =================================================================================================
def piston(spec) -> Part:
    """Drawn on its own axis (the assembly puts it in the left or right cylinder): spigoted end
    forward against the bridge piece (Sec 12 para 22)."""
    r = O.PISTON_D / 2
    p0, p1 = O.PISTON_E
    p = Sh.revolved([(0, p0), (6.0, p0), (6.0, p0 + 4.0), (r - 0.6, p0 + 4.0), (r, p0 + 4.6), (r, p1 - 0.6),
                     (r - 0.6, p1), (0, p1)])
    p = p - ring(r - 2.6, r + 1, p0 + 9.0, p0 + 11.6)                                   # O-ring groove
    p = p - zc(r - 3.0, p1 - 10.0, p1 + 1)                                              # hollow back
    return _l(p.moved(Location((0, 0, O.Z0))), spec)


def piston_o_ring(spec) -> Part:
    r = O.PISTON_D / 2 - 1.4
    return _l(Location((0, 0, O.Z0 + O.PISTON_E[0] + 10.3)) * Torus(r, 1.2), spec)


def bridge_piece(spec) -> Part:
    t = spec.nom("thickness")
    b0, b1 = O.BRIDGE_E
    b = box(-25.0, 25.0, -6.0, 6.0, b0, b0 + t)
    for s in (1, -1):
        b = b - zc(4.3, b0 - 1, b1 + 1, s * O.BOLT_UP, 0.0)
    return _l(b.moved(Location((0, 0, O.Z0))), spec)


def lockwasher(spec) -> Part:
    """Tab washer under a bridge piece nut; the tab is bent up against the bridge piece's edge
    (Sec 12 paras 2, 22). Drawn at the origin, face on z = 0."""
    t = spec.nom("thickness")
    w = zc(8.5, 0, t) + box(-4.0, 4.0, 6.5, 6.5 + t, -6.0, t)                            # tab bent over the bridge edge
    w = w - zc(4.2, -1, t + 1)
    return _l(w, spec)


def bridge_nut(spec) -> Part:
    return _l(F.hex_nut(O.BOLT_SIZE), spec)


# =================================================================================================
# pump cam (93), Woodruff key (92), circlip (94)
# =================================================================================================
KEY_C = G.MS_TAIL_R + 4.6 - 2.0              # centre of the key's arc (up), P5a keyway cutter
KEY_R = 0.5 * IN / 2


def cam(spec) -> Part:
    """Eccentric on the mainshaft, its low point down on the pump plunger (Sec 11 para 5)."""
    e0, e1 = O.CAM_E
    c = zc(O.CAM_R, e0, e1, O.CAM_THROW, 0.0)
    c = c - zc(O.SHAFT_R + 0.03, e0 - 1, e1 + 1)
    c = c - box(O.SHAFT_R - 1.0, KEY_C + KEY_R * 0.2 + 1.5, -1.65, 1.65, e0 - 1, e1 + 1)    # keyway at the top
    for s in (1, -1):                                                                  # chamfers on the lobe edges
        z = e0 if s < 0 else e1
        c = c - Location((O.CAM_THROW, 0, z)) * Sh.revolved([(O.CAM_R - 1.0, -0.01 if s > 0 else 0.01),
                                                            (O.CAM_R + 1, -0.01 if s > 0 else 0.01),
                                                            (O.CAM_R + 1, -1.2 * s)])
    return _out(c, spec)


def woodruff_key(spec) -> Part:
    t = spec.nom("thickness")
    mid = sum(O.CAM_E) / 2
    k = Location((KEY_C, 0, mid)) * Rot(90, 0, 0) * Cylinder(KEY_R, t)
    k = k - box(KEY_C + KEY_R * 0.2, KEY_C + KEY_R + 1, -t, t, mid - 10, mid + 10)
    return _out(k, spec)


def cam_circlip(spec) -> Part:
    """Item 94 (MGOC 22H228): retains the cam, in the groove behind it."""
    r0 = G.MS_TAIL_R - 0.8
    z = O.e_of(G.MS_CAM_D[1]) + 1.05
    c = ring(r0, r0 + 3.4, z, z + 1.1)
    c = c - Location((0, -r0 - 1.7, z)) * Box(4.0, 6.0, 4.0)
    for s in (1, -1):
        c = c + Location((s * 3.4, -r0 - 2.6, z)) * Cylinder(1.8, 1.1, align=BASE)
        c = c - Location((s * 3.4, -r0 - 2.6, z - 1)) * Cylinder(0.7, 3.2, align=BASE)
    return _out(c, spec)


# =================================================================================================
# pump: plunger (41), pin (42), spring (44), body (43), grub screw (47); non-return valve 45-50
# =================================================================================================
PE = O.PUMP_E


def pump_plunger(spec) -> Part:
    h0, h1 = O.PUMP_HEAD                                     # top, bottom of the fork head (up)
    stem_r = 4.5
    p = vrev([(0, O.PUMP_BODY[1] - 14.0), (stem_r, O.PUMP_BODY[1] - 14.0), (stem_r, h1), (0, h1)], 0.0, PE)
    p = p + box(h1 - 4.0, h1, -5.0, 5.0, PE - 13.5, PE + 13.5)                            # yoke
    for s in (1, -1):                                                                    # cheeks either side of the cam
        z0 = PE + s * 11.3
        p = p + box(h1 - 0.01, h0 + 2.0, -5.0, 5.0, min(z0, z0 + s * 2.2), max(z0, z0 + s * 2.2))
    p = p - zc(O.PIN_D / 2 + 0.05, PE - 15, PE + 15, O.PUMP_TOP - O.PIN_D / 2, 0.0)       # pin hole
    p = p + vrev([(stem_r - 0.01, h1 - 6.0), (6.5, h1 - 6.0), (6.5, h1 - 4.0), (stem_r - 0.01, h1 - 4.0)], 0.0, PE)   # spring seat
    return _out(p, spec)


def pump_pin(spec) -> Part:
    p = Sh.chamfered_cyl(O.PIN_D, 26.6, 0.3, z0=PE - 13.3).moved(Location((O.PUMP_TOP - O.PIN_D / 2, 0, 0)))
    return _out(p, spec)


def pump_spring(spec) -> Part:
    top = O.PUMP_HEAD[1] - 6.0
    L = top - O.PUMP_BODY[1]
    s = Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), L, 9.0)
    s = Location((O.PUMP_BODY[1], 0, PE)) * Rot(0, 90, 0) * s
    return _out(s, spec)


def pump_body(spec) -> Part:
    """Item 43: small end up into the centre hole at the bottom of the casing, inlet facing the
    rear, a groove for the grub screw (Sec 12 para 23)."""
    b0, b1 = O.PUMP_BODY
    st = O.PUMP_BODY_STEP
    b = vrev([(4.6, b0), (10.15, b0), (10.15, st), (7.0, st + 2.0), (7.0, b1), (4.6, b1)], 0.0, PE)
    b = b - vrev([(6.0, b0 - 0.01), (7.6, b0 - 0.01), (7.6, b0 + 9.0), (6.0, b0 + 9.0)], 0.0, PE)   # thread for the NRV body
    b = b - xcyl(6.0, b0 - 1, b0 + 9.0, 0.0, PE)
    b = b - vrev([(9.0, O.GRUB_UP - 3.0), (10.5, O.GRUB_UP - 3.0), (10.5, O.GRUB_UP + 3.0), (9.0, O.GRUB_UP + 3.0)], 0.0, PE)
    b = b - zc(2.2, PE, PE + 12.0, st - 8.0, 0.0)                                           # inlet, facing the rear
    b = b - zc(1.5, PE - 12.0, PE, st - 14.0, 0.0)                                          # delivery to the gallery
    return _out(b, spec)


def grub_screw(spec) -> Part:
    L = spec.nom("length")
    s = Sh.chamfered_cyl(5.6, L, 0.4)
    s = s - Location((0, 0, -0.5)) * Box(1.0, 6.0, 3.0, align=BASE)
    return _out(s.moved(Location((O.GRUB_UP, 0, PE - 9.6 - L))), spec)


def nrv_body(spec) -> Part:
    n0, n1 = O.NRV
    b = vrev([(2.0, n0), (8.0, n0), (8.0, n0 + 3.0), (7.4, n0 + 3.5), (7.4, n1 + 8.0), (3.5, n1 + 8.0), (3.5, n1 + 6.0),
              (2.0, n1 + 4.0)], 0.0, PE)
    b = b - xcyl(4.2, n0 - 1, n1 + 2.5, 0.0, PE)                                             # ball chamber
    for k in range(3):
        b = b - vrev([(7.1, n1 + 0.5 + 2.4 * k), (7.6, n1 + 0.5 + 2.4 * k), (7.6, n1 + 1.3 + 2.4 * k), (7.1, n1 + 1.3 + 2.4 * k)], 0.0, PE)
    return _out(b, spec)


def ball(r_up, y, e, d):
    return Location((r_up, y, e)) * Sphere(d / 2)


NRV_BALL_D = 0.25 * IN


def nrv_ball(spec) -> Part:
    d = spec.nom("diameter")
    return _out(ball(O.NRV[1] + 2.5 - d / 2 - 0.2, 0.0, PE, d), spec)


def nrv_spring(spec) -> Part:
    d = NRV_BALL_D
    top = O.NRV[1] + 2.5 - d - 0.2
    bot = O.PLUG_FACE + 1.0
    s = Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), top - bot, 6.0)
    return _out(Location((bot, 0, PE)) * Rot(0, 90, 0) * s, spec)


PLUG_WASHER_T = 1.5


def hex_plug_down(face_up, thread_r, thread_l, af, head_h, y, e, lock_hole=True):
    """Plug screwed up into the underside: head below face_up, thread above."""
    from build123d import RegularPolygon
    h = extrude(RegularPolygon(af / math.sqrt(3), 6), head_h)
    p = h + zc(thread_r, head_h - 0.01, head_h + thread_l) + zc(af / 2 + 1.5, head_h - 1.5, head_h)
    if lock_hole:                                                                       # drilled for the locking wire
        p = p - Location((0, 0, head_h * 0.5)) * Rot(0, 90, 30) * Cylinder(0.9, af * 2)
    return Location((face_up, y, e)) * Rot(0, 90, 0) * p.moved(Location((0, 0, -head_h)))


def nrv_plug(spec) -> Part:
    """Item 49: the non-return valve plug, wired to the relief valve plug (Sec 12 para 24)."""
    p = hex_plug_down(O.PLUG_FACE - PLUG_WASHER_T, 12.5, 7.0, 22.2, 8.0, 0.0, PE)
    p = p - xcyl(5.0, O.PLUG_FACE - 0.5, O.PLUG_FACE + 7.5, 0.0, PE)                     # spring pocket
    return _out(p, spec)


def plug_washer(r_out, r_in, t, y, e):
    return xcyl(r_out, O.PLUG_FACE - t, O.PLUG_FACE, y, e) - xcyl(r_in, O.PLUG_FACE - t - 1, O.PLUG_FACE + 1, y, e)


def nrv_washer(spec) -> Part:
    t = spec.nom("thickness")
    return _out(plug_washer(spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2, t, 0.0, PE), spec)


# =================================================================================================
# relief valve: plug (95), washer (96), spring (97), plunger (98), body (99), O-ring (100)
# =================================================================================================
RL = O.RELIEF_LEFT


def relief_body(spec) -> Part:
    r0, r1 = O.RELIEF_BODY
    b = vrev([(3.0, r0), (7.55, r0), (7.55, r1), (3.0, r1)], RL, PE)
    b = b - xcyl(4.6, r0 - 1, r1 - 6.0, RL, PE)                                              # plunger bore
    b = b - vrev([(6.0, r1 - 14.0), (7.7, r1 - 14.0), (7.7, r1 - 11.4), (6.0, r1 - 11.4)], RL, PE)   # O-ring groove
    for s in (1, -1):                                                                    # holes for circlip pliers
        b = b - xcyl(1.0, r0 - 1, r0 + 3.0, RL + s * 5.5, PE)
    b = b - zc(1.5, PE - 9, PE + 9, r1 - 9.0, RL)                                           # cross drilling to the gallery
    return _out(b, spec)


def relief_o_ring(spec) -> Part:
    r1 = O.RELIEF_BODY[1]
    return _out(Location((r1 - 12.7, RL, PE)) * Rot(0, 90, 0) * Torus(6.4, 1.2), spec)


def relief_plunger(spec) -> Part:
    r0, r1 = O.RELIEF_BODY
    p = vrev([(0, r1 - 30.0), (4.5, r1 - 30.0), (4.5, r1 - 8.0), (2.5, r1 - 6.5), (0, r1 - 6.0)], RL, PE)
    p = p + vrev([(0, r1 - 34.0), (3.0, r1 - 34.0), (3.0, r1 - 29.99), (0, r1 - 29.99)], RL, PE)     # spring spigot
    return _out(p, spec)


def relief_spring(spec) -> Part:
    top = O.RELIEF_BODY[1] - 30.0
    bot = O.PLUG_FACE + 1.0
    s = Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), top - bot, 8.0)
    return _out(Location((bot, RL, PE)) * Rot(0, 90, 0) * s, spec)


def relief_plug(spec) -> Part:
    p = hex_plug_down(O.PLUG_FACE - PLUG_WASHER_T, 11.0, 7.0, 19.05, 8.0, RL, PE)
    p = p - xcyl(5.6, O.PLUG_FACE - 4.5, O.PLUG_FACE + 7.5, RL, PE)
    return _out(p, spec)


def relief_washer(spec) -> Part:
    t = spec.nom("thickness")
    return _out(plug_washer(spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2, t, RL, PE), spec)


# =================================================================================================
# operating valve: valve (25), ball (24), plunger (23), spring (22), washer (21), plug (20)
# =================================================================================================
VE, VL = O.OPVALVE
XE, XU = O.CROSS_SHAFT
V_BOT = XU + 6.5                                 # valve stem foot on the cross-shaft cam
V_SEAT = 50.0                                    # seat at the top of the valve tube
TOP = O.OPVALVE_TOP


def op_valve(spec) -> Part:
    """Item 25: a tube with a seat at its top for the ball, a small hole in its side (Sec 14 para 6)."""
    v = vrev([(0, V_BOT), (3.0, V_BOT), (3.0, V_BOT + 6.0), (5.5, V_BOT + 8.0), (5.5, V_SEAT), (0, V_SEAT)], VL, VE)
    v = v - xcyl(1.6, V_BOT + 2.0, V_SEAT + 1, VL, VE)
    v = v - Location((V_SEAT + 0.6, VL, VE)) * Rot(0, 90, 0) * Sh.revolved([(0, -2.0), (3.2, 0.6), (0, 0.6)])
    v = v - zc(0.8, VE - 8, VE, V_SEAT - 10.0, VL)                                           # the small side hole
    for k in range(3):
        z = V_BOT + 14.0 + 7.0 * k
        v = v - vrev([(5.0, z), (5.6, z), (5.6, z + 1.2), (5.0, z + 1.2)], VL, VE)
    return _out(v, spec)


def op_ball(spec) -> Part:
    d = spec.nom("diameter")
    return _out(ball(V_SEAT + d / 2 - 0.6, VL, VE, d), spec)


def op_plunger(spec) -> Part:
    d = 6.35
    z0 = V_SEAT + d - 0.6
    p = vrev([(0, z0), (2.0, z0), (2.0, z0 + 3.0), (4.5, z0 + 3.0), (4.5, z0 + 5.0), (2.4, z0 + 5.0), (2.4, z0 + 9.0), (0, z0 + 9.0)], VL, VE)
    return _out(p, spec)


def op_spring(spec) -> Part:
    z0 = V_SEAT + 6.35 - 0.6 + 5.0
    z1 = TOP - 1.0
    s = Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), z1 - z0, 6.0)
    return _out(Location((z0, VL, VE)) * Rot(0, 90, 0) * s, spec)


def op_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = xcyl(spec.nom("outside_diameter") / 2, TOP, TOP + t, VL, VE) - xcyl(spec.nom("inside_diameter") / 2, TOP - 1, TOP + t + 1, VL, VE)
    return _out(w, spec)


def op_plug(spec) -> Part:
    from build123d import RegularPolygon
    t = 1.2
    head = extrude(RegularPolygon(19.05 / math.sqrt(3), 6), 7.0)
    p = head + zc(10.0, -0.01, 1.5) + zc(7.9, -10.0, 0.01)
    p = p - zc(4.0, -10.5, -2.0)
    return _out(Location((TOP + t, VL, VE)) * Rot(0, 90, 0) * p, spec)


# =================================================================================================
# filter (11), sealing plate (12), magnetic rings (13)
# =================================================================================================
FE, FU = O.FILTER
F_IN, F_OUT = 18.0, O.FILTER_FACE - 2.4


def filter_(spec) -> Part:
    r = O.FILTER_R
    f = ycyl(r, F_IN, F_OUT, FU, FE) - ycyl(r - 1.0, F_IN + 2.0, F_OUT - 2.0, FU, FE)
    for k in range(10):                                                                # gauze windows
        a = math.radians(36.0 * k)
        for j in range(4):
            y = F_IN + 6.0 + j * 8.0
            f = f - Location((FU + r * math.cos(a), y, FE + r * math.sin(a))) * Rot(0, math.degrees(-a), 0) * Box(3.0, 5.0, 4.0)
    f = f + ycyl(r + 0.4, F_IN, F_IN + 2.0, FU, FE)
    return _out(f, spec)


def sealing_plate(spec) -> Part:
    """Item 12: the filter seal at the outer end, metal face inwards (Sec 2 para 6)."""
    t = spec.nom("thickness")
    p = ycyl(O.FILTER_R + 1.5, F_OUT, F_OUT + t, FU, FE) - ycyl(5.0, F_OUT - 1, F_OUT + t + 1, FU, FE)
    return _out(p, spec)


def magnetic_ring(spec) -> Part:
    """Item 13: rings round the filter's outer end; the assembly spaces the two."""
    w = spec.nom("width")
    r = O.FILTER_R
    m = ycyl(r + 1.3, F_OUT - w, F_OUT, FU, FE) - ycyl(r + 0.05, F_OUT - w - 1, F_OUT + 1, FU, FE)
    return _out(m, spec)


# =================================================================================================
# solenoid (34), gasket (36), self-locking nut (35), operating lever (26), Mills pins (27, 28),
# O-ring (29), cover (30) and gasket (31)
# =================================================================================================
SU, SL = O.SOL_AXIS
S0, S1 = O.SOL_E
GK = 0.8                                      # gasket
EAR = 27.0                                    # solenoid flange screws above and below the axis


def solenoid(spec) -> Part:
    """Item 34 (MGOC 10002): a can with a flange on the chamber's rear wall, its plunger forward
    through the wall to the lever (Fig 6.17), the lead from the back end."""
    r = O.SOL_R
    f0 = S0 + GK
    s = Sh.revolved([(0, f0 + 4.0), (r - 1.0, f0 + 4.0), (r, f0 + 5.0), (r, S1 - 18.0), (r + 1.2, S1 - 17.0), (r + 1.2, S1 - 13.0),
                     (r, S1 - 12.0), (r, S1 - 2.0), (r - 2.0, S1), (6.0, S1), (6.0, S1 + 3.0), (0, S1 + 3.0)])
    fl = zc(r + 2.0, f0, f0 + 4.0)
    for du in (EAR, -EAR):
        fl = fl + zc(6.5, f0, f0 + 4.0, du, 0.0)
    fl = fl + box(-EAR, EAR, -6.5, 6.5, f0, f0 + 4.0)
    for du in (EAR, -EAR):
        fl = fl - zc(2.6, f0 - 1, f0 + 5, du, 0.0)
    s = s + fl
    # plunger rod through the wall to the lever, two flats on its shank (Sec 13 para 4), thread
    pl = Sh.revolved([(0, O.CROSS_SHAFT[0] - 9.0), (2.6, O.CROSS_SHAFT[0] - 9.0), (2.6, O.CROSS_SHAFT[0] + 4.0), (4.0, O.CROSS_SHAFT[0] + 6.0),
                      (4.0, f0 + 0.01), (0, f0 + 0.01)])
    pl = pl - box(3.2, 5.0, -5.0, 5.0, CH_E1 - 14.0, CH_E1 - 6.0) - box(-5.0, -3.2, -5.0, 5.0, CH_E1 - 14.0, CH_E1 - 6.0)
    s = s + pl
    # lead and grommet off the back
    s = s + zc(3.0, S1 + 2.9, S1 + 9.0, -r * 0.4, 0.0)                               # grommet
    s = s + zc(1.6, S1 + 8.9, S1 + 14.0, -r * 0.4, 0.0)                                # lead (cut short; the loom is P10)
    return _out(Location((SU, SL, 0)) * s, spec)


def solenoid_gasket(spec) -> Part:
    g = zc(O.SOL_R + 2.0, S0, S0 + GK) + box(-EAR, EAR, -6.5, 6.5, S0, S0 + GK)
    for du in (EAR, -EAR):
        g = g + zc(6.5, S0, S0 + GK, du, 0.0)
    g = g - zc(7.0, S0 - 1, S0 + GK + 1)
    for du in (EAR, -EAR):
        g = g - zc(2.6, S0 - 1, S0 + GK + 1, du, 0.0)
    return _out(Location((SU, SL, 0)) * g, spec)


def solenoid_nut(spec) -> Part:
    """Item 35: self-locking nut on the plunger end, in front of the lever (nut B, Fig 6.17)."""
    from build123d import RegularPolygon
    n = extrude(RegularPolygon(7.94 / math.sqrt(3), 6), 4.5) + zc(3.6, 4.49, 6.5)
    n = n - zc(2.4, -1, 8)
    return _out(Location((SU, SL, XE - 8.0)) * n, spec)


LEVER_T = 4.0


def op_lever(spec) -> Part:
    """Item 26, the operating valve lever assembly: the cross-shaft (O-ring and Mills pins), the cam
    under the operating valve, and the outer arm with test hole A, its lower end forked on the
    solenoid plunger (Figs 6.13, 6.14, 6.17)."""
    xr = 4.75
    L0 = O.LEVER_LEFT
    ya = L0 + 4.0                                                                       # plane of the arm
    sh = ycyl(xr, VL - 6.0, ya - 1.0, XU, XE)
    # valve cam: a flat-sided lobe under the valve foot
    cam_ = ycyl(7.5, VL - 6.0, VL + 6.0, XU, XE) - box(XU + 5.0, XU + 9.0, VL - 7.0, VL + 7.0, XE - 9.0, XE + 9.0)
    # outer arm: boss on the shaft, arm down, a tab at its foot across the solenoid plunger
    arm = ycyl(7.0, ya - LEVER_T / 2, ya + LEVER_T / 2, XU, XE)
    arm = arm + box(SU + 4.0, XU, ya - LEVER_T / 2, ya + LEVER_T / 2, XE - 5.0, XE + 5.0)
    arm = arm + box(SU - 7.0, SU + 7.0, L0 - 7.0, ya + LEVER_T / 2, XE - 1.5, XE + 1.5)
    arm = arm - ycyl(2.45, ya - 5, ya + 5, XU - 14.0, XE)                                  # hole A (Fig 6.17)
    lv = sh + cam_ + arm
    lv = lv - zc(2.9, XE - 9.0, XE + 9.0, SU, L0)                                            # the plunger passes through the tab
    for y in (VL, ya):                                                                  # Mills pin holes
        lv = lv - xcyl(1.6, XU - 10, XU + 10, y, XE)
    return _out(lv, spec)


def mills_pin(spec) -> Part:
    """Items 27, 28: grooved (Mills) pins through the cam and the arm boss; drawn at the arm."""
    p = Sh.chamfered_cyl(3.2, 12.0, 0.3, z0=-6.0)
    for k in range(3):
        a = 120.0 * k
        p = p - Rot(0, 0, a) * box(1.3, 2.0, -0.3, 0.3, -5.0, 5.0)
    return _out(Location((XU, O.LEVER_LEFT + 4.0, XE)) * Rot(0, 90, 0) * p, spec)


def lever_o_ring(spec) -> Part:
    return _out(Location((XU, -88.0, XE)) * Rot(90, 0, 0) * Torus(5.8, 1.1), spec)


CO = (CH_E0, CH_E1, CH_U0, CH_U1)


def chamber_cover(spec) -> Part:
    """Item 30: cover over the lever chamber on three bolts (Sec 13 para 2), with a raised panel."""
    t = spec.nom("thickness")
    poly = rounded([(CH_U0, CH_E0), (CH_U1, CH_E0), (CH_U1, CH_E1), (CH_U0, CH_E1)], 6.0)
    from build123d import Plane, Polygon
    face = O.CHAMBER_FACE - GK
    p = Location((0, face, 0)) * extrude(Plane.XZ * Polygon(*poly, align=None), t)
    inner = rounded([(CH_U0 + 13, CH_E0 + 12), (CH_U1 - 13, CH_E0 + 12), (CH_U1 - 13, CH_E1 - 12), (CH_U0 + 13, CH_E1 - 12)], 5.0)
    p = p + Location((0, face - t + 0.01, 0)) * extrude(Plane.XZ * Polygon(*inner, align=None), 3.0)
    for u, e in CHAMBER_SCREWS:
        p = p - ycyl(3.6, face + 1, face - t - 4, u, e)
    return _out(p, spec)


def chamber_gasket(spec) -> Part:
    from build123d import Plane, Polygon
    poly = rounded([(CH_U0, CH_E0), (CH_U1, CH_E0), (CH_U1, CH_E1), (CH_U0, CH_E1)], 6.0)
    g = Location((0, O.CHAMBER_FACE, 0)) * extrude(Plane.XZ * Polygon(*poly, align=None), GK)
    g = g - box(CH_U0 + 8.0, CH_U1 - 6.0, O.CHAMBER_FACE - 2, O.CHAMBER_FACE + 1, CH_E0 + 8.0, CH_E1 - 8.0)
    for u, e in CHAMBER_SCREWS:
        g = g - ycyl(3.6, O.CHAMBER_FACE + 1, O.CHAMBER_FACE - 2, u, e)
    return _out(g, spec)


def solenoid_screw(spec) -> Part:
    """10-32 UNF x 1/2 in screw (MGOC 53K126), drawn head at the origin, shank along +z."""
    L = spec.nom("length")
    s = Sh.revolved([(0, -2.8), (3.7, -2.8), (3.9, -1.2), (3.7, 0), (2.4, 0), (2.4, L), (0, L)])
    s = s - Location((0, 0, -2.8)) * Box(1.2, 9.0, 2.4)
    return _l(s, spec)


def star_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t)
    for k in range(10):
        w = w - Rot(0, 0, 36.0 * k) * box(-0.4, 0.4, id_ / 2 - 0.1, id_ / 2 + 1.4, -1, t + 1)
    return _l(w, spec)


WASHER = C.WASHER

PARTS = {
    "gearbox.overdrive-hydraulics.piston": {"build": piston, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.overdrive-hydraulics.piston-o-ring": {"build": piston_o_ring},
    "gearbox.overdrive-hydraulics.bridge-piece": {"build": bridge_piece},
    "gearbox.overdrive-hydraulics.lockwasher": {"build": lockwasher},
    "gearbox.overdrive-hydraulics.bridge-nut": {"build": bridge_nut},
    "gearbox.overdrive-hydraulics.cam": {"build": cam},
    "gearbox.overdrive-hydraulics.key": {"build": woodruff_key},
    "gearbox.overdrive-hydraulics.cam-circlip": {"build": cam_circlip},
    "gearbox.overdrive-hydraulics.pump-plunger": {"build": pump_plunger},
    "gearbox.overdrive-hydraulics.pump-pin": {"build": pump_pin},
    "gearbox.overdrive-hydraulics.pump-spring": {"build": pump_spring},
    "gearbox.overdrive-hydraulics.pump-body": {"build": pump_body},
    "gearbox.overdrive-hydraulics.grub-screw": {"build": grub_screw},
    "gearbox.overdrive-hydraulics.nrv-body": {"build": nrv_body},
    "gearbox.overdrive-hydraulics.nrv-ball": {"build": nrv_ball, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.overdrive-hydraulics.nrv-spring": {"build": nrv_spring},
    "gearbox.overdrive-hydraulics.nrv-plug": {"build": nrv_plug},
    "gearbox.overdrive-hydraulics.nrv-washer": {"build": nrv_washer},
    "gearbox.overdrive-hydraulics.relief-body": {"build": relief_body},
    "gearbox.overdrive-hydraulics.relief-o-ring": {"build": relief_o_ring},
    "gearbox.overdrive-hydraulics.relief-plunger": {"build": relief_plunger},
    "gearbox.overdrive-hydraulics.relief-spring": {"build": relief_spring},
    "gearbox.overdrive-hydraulics.relief-plug": {"build": relief_plug},
    "gearbox.overdrive-hydraulics.relief-washer": {"build": relief_washer},
    "gearbox.overdrive-hydraulics.op-valve": {"build": op_valve},
    "gearbox.overdrive-hydraulics.op-ball": {"build": op_ball, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.overdrive-hydraulics.op-plunger": {"build": op_plunger},
    "gearbox.overdrive-hydraulics.op-spring": {"build": op_spring},
    "gearbox.overdrive-hydraulics.op-washer": {"build": op_washer},
    "gearbox.overdrive-hydraulics.op-plug": {"build": op_plug},
    "gearbox.overdrive-hydraulics.filter": {"build": filter_},
    "gearbox.overdrive-hydraulics.sealing-plate": {"build": sealing_plate},
    "gearbox.overdrive-hydraulics.magnetic-ring": {"build": magnetic_ring},
    "gearbox.overdrive-hydraulics.solenoid": {"build": solenoid},
    "gearbox.overdrive-hydraulics.solenoid-gasket": {"build": solenoid_gasket},
    "gearbox.overdrive-hydraulics.solenoid-nut": {"build": solenoid_nut},
    "gearbox.overdrive-hydraulics.solenoid-screw": {"build": solenoid_screw, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.overdrive-hydraulics.solenoid-washer": {"build": star_washer},
    "gearbox.overdrive-hydraulics.op-lever": {"build": op_lever},
    "gearbox.overdrive-hydraulics.mills-pin": {"build": mills_pin},
    "gearbox.overdrive-hydraulics.lever-o-ring": {"build": lever_o_ring},
    "gearbox.overdrive-hydraulics.cover": {"build": chamber_cover},
    "gearbox.overdrive-hydraulics.cover-gasket": {"build": chamber_gasket},
    "gearbox.overdrive-hydraulics.cover-screw": {"build": C.bolt("1/4"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.overdrive-hydraulics.cover-washer": {"build": C.spring_washer, "probes": WASHER},
}
