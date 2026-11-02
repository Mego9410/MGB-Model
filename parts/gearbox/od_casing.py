"""Laycock type D overdrive casings and their fixings, the filter cover, plugs and the speedometer
drive in the rear casing (Haynes Ch 6 Fig 6.13 items 2, 7, 8, 11-15, 18-19, 39-40, 84-90; Fig 6.12;
Fig 6.17; Fig 6.18; Sec 2 para 5, Sec 11, Sec 12, Sec 14).

Built in the gearbox frame of mgb.gearbox_layout (GF: local z = d rearward, x up, y left) at the
overdrive stations of mgb.overdrive_layout: each solid is drawn with z = e (millimetres behind
the main casing front face) and moved back by O.Z0.

Forms (Fig 6.13 items 2, 7, 8; Fig 6.12 section; Figs 6.17 and 6.18):
- main casing: round front flange on the adaptor with the spigot into its register, eight stud
  holes with nut scallops behind; a barrel body with ribs over the top; the sump below with the
  pump, relief valve and drain bosses on its flat underside (DRAIN cast beside the plug), the
  filter cover face on the left, a plug boss on the right; the operating cylinders, bolt holes and
  the cam chamber in the front wall; the operating valve boss on the top right; the solenoid and
  lever chamber on the right with its cover face and the solenoid seat on its rear wall; the rear
  mounting pads low on both sides; the rear flange the brake ring clamps to on eight studs.
- brake ring: a thick ring with the internal cone (small end forward, Sec 12 para 20) and the
  eight stud holes, and a lug.
- rear casing: front flange, a body that steps down from the brake ring to the bearing housings
  with a flat-topped hump over the front, the two remote bracket bosses, the speedometer drive
  boss on the right below the output shaft with its locking screw lug, and the oil seal bore.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Plane, Polygon, Rot, Text, Torus, extrude

from mgb import fasteners as F, gearbox_layout as G, gears as GR, overdrive_layout as O, probes, shapes as Sh
from mgb.poly2d import circle_pts, hull, rounded
from parts.gearbox import casing as C

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)
zc, box, zprism = C.zc, C.box, C.zprism


def _out(p, spec):
    p = p.moved(Location((0, 0, O.Z0)))
    p.label = spec.id
    return p


def ycyl(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along local y (across the car) from y0 to y1 at (up x, e z)."""
    lo, hi = min(y0, y1), max(y0, y1)
    return Location((x, lo, z)) * Rot(-90, 0, 0) * Cylinder(r, hi - lo, align=BASE)


def xcyl(r, x0, x1, y=0.0, z=0.0):
    """Cylinder along local x (up) from x0 to x1 at (left y, e z)."""
    lo, hi = min(x0, x1), max(x0, x1)
    return Location((lo, y, z)) * Rot(0, 90, 0) * Cylinder(r, hi - lo, align=BASE)


TAP = {"1/4": 3.2, "5/16": 3.98, "10-32": 2.4}            # tapped holes drawn at the major radius
CLR = {"1/4": 3.6, "5/16": 4.2}


# =================================================================================================
# main casing (item 2)
# =================================================================================================
BODY = circle_pts(0, 0, O.MC_BODY_R, 72)                                         # the barrel
SUMP = rounded([(O.SUMP_BOTTOM, O.SUMP_LEFT[0]), (O.SUMP_BOTTOM, O.SUMP_LEFT[1]), (-40.0, O.SUMP_LEFT[1]),
                (-40.0, O.SUMP_LEFT[0])], 8.0)                                     # the sump box under it
COVER_SCREWS = [(O.COVER[2] + 4.5, O.COVER[0] + 4.5), (O.COVER[2] + 4.5, O.COVER[1] - 4.5),
                (O.COVER[3] - 4.5, O.COVER[0] + 4.5), (O.COVER[3] - 4.5, O.COVER[1] - 4.5)]   # (up, e)
COVER_OPEN = (O.COVER[2] + 7.0, O.COVER[3] - 6.0, O.COVER[0] + 9.0, O.COVER[1] - 9.0)       # up0, up1, e0, e1
CH_E0, CH_E1, CH_U0, CH_U1 = O.CHAMBER
CH_CAV = (CH_E0 + 4.0, CH_E1 - 8.0, CH_U0 + 8.0, CH_U1 - 8.5)
CHAMBER_SCREWS = [(CH_U1 - 4.0, (CH_E0 + CH_E1) / 2 + 8.0), (CH_U0 + 3.5, CH_E0 + 5.0), (CH_U0 + 3.5, CH_E1 - 12.0)]  # (up, e)
SOL_SCREWS = [(O.SOL_AXIS[0] + 27.0, O.SOL_AXIS[1]), (O.SOL_AXIS[0] - 27.0, O.SOL_AXIS[1])]                 # (up, left)


def _lettering(word, size, depth):
    t = extrude(Text(word, font_size=size), depth)
    return t


def main_casing(spec) -> Part:
    c = zprism(BODY, 8.0, 74.0) + zprism(SUMP, O.SUMP_E[0], O.SUMP_E[1])
    # front flange and spigot
    c = c + zc(O.MC_FLANGE_R, O.MC_FLANGE[0], O.MC_FLANGE[1])
    c = c + Sh.revolved([(O.SPIGOT_R[1], O.SPIGOT[0]), (O.SPIGOT_R[0] - 0.6, O.SPIGOT[0]), (O.SPIGOT_R[0], O.SPIGOT[0] + 0.6),
                         (O.SPIGOT_R[0], 0.2), (O.SPIGOT_R[1], 0.2)])
    # rear flange for the brake ring
    c = c + zc(O.CASE_R, O.MC_REAR_FL[0], O.MC_REAR_FL[1])
    # three ribs over the top, flange to flange, and a web each side down to the sump
    for a in (-38.0, 0.0, 38.0):
        c = c + Rot(0, 0, a) * box(O.MC_BODY_R - 6.0, O.MC_BODY_R + 5.0, -3.5, 3.5, O.MC_FLANGE[1] - 1, O.MC_REAR_FL[0] + 1)
    for s in (1, -1):
        c = c + Rot(0, 0, s * 118.0) * box(O.MC_BODY_R - 6.0, O.MC_BODY_R + 4.0, -3.0, 3.0, O.MC_FLANGE[1] - 1, 46.0)
    # operating valve boss on the top right (plug 20 is reached from inside the car, Sec 14 para 5)
    ve, vl = O.OPVALVE
    c = c + xcyl(11.0, 30.0, O.OPVALVE_TOP, vl, ve)
    c = c + box(30.0, O.OPVALVE_TOP - 8.0, vl - 3.0, vl + 3.0, ve - 18.0, ve)          # gusset forward
    c = c + box(30.0, O.OPVALVE_TOP - 8.0, vl - 3.0, vl + 3.0, ve, ve + 11.0)           # and back to the rear flange
    # lever chamber on the right (Fig 6.17)
    ch = zprism(rounded([(CH_U0, O.CHAMBER_FACE), (CH_U1, O.CHAMBER_FACE), (CH_U1, -60.0), (CH_U0, -60.0)], 6.0), CH_E0, CH_E1)
    ch = ch + zprism([(CH_U0 + 2.0, -56.0), (CH_U0 + 2.0, -96.0), (CH_U0 - 18.0, -46.0)], CH_E0 + 2.0, CH_E0 + 7.0)   # web under it
    c = c + ch
    # rear mounting pads, both sides (the rubber mountings bolt on, Fig 1.29 item 33)
    for s in (1, -1):
        u0, u1 = O.MOUNT_UP
        pad = rounded([(u0, s * 40.0), (u1, s * 40.0), (u1, s * O.MOUNT_FACE), (u0, s * O.MOUNT_FACE)], 4.0)
        c = c + zprism(pad, O.MOUNT_E[0], O.MOUNT_E[1])
        for e in (O.MOUNT_E[1] - 9.0,):                                              # gusset down to the sump, behind the filter cover
            c = c + zprism([(u0 + 0.5, s * (O.SUMP_LEFT[1] - 4.0)), (u0 + 0.5, s * (O.MOUNT_FACE - 6.0)),
                            (u0 - 22.0, s * (O.SUMP_LEFT[1] - 4.0))], e, e + 6.0)
    # filter cover face on the left of the sump
    e0, e1, u0, u1 = O.COVER
    c = c + box(u0 + 2.0, u1, 40.0, O.FILTER_FACE, e0, e1)
    # plug 39 boss on the right of the sump
    pe, pu = O.PLUG39
    c = c + ycyl(11.0, O.SUMP_LEFT[0] + 6.0, O.SUMP_LEFT[0] - 6.0, pu, pe)
    # ---- cavities ----
    c = c - zc(70.0, 28.0, O.MC_REAR_FL[0])                                 # springs, bearing housing
    c = c - zc(76.0, O.MC_REAR_FL[0] - 0.01, O.MC_LEN + 1.0)                # the cone clutch disc
    c = c - zc(22.0, O.SPIGOT[0] - 1.0, 30.0)                               # cam chamber, through the front wall
    c = c - zc(O.SPIGOT_R[1], O.SPIGOT[0] - 1.0, 0.0)
    c = c - box(-115.0, -64.0, -44.0, 54.0, 12.0, 68.0)                     # sump
    # put back: the valve block inside the top right, the pump and relief valve bosses in the sump
    c = c + box(0.0, 58.0, -80.0, -46.0, O.OPVALVE[0] - 12.0, O.OPVALVE[0] + 12.0)
    c = c + xcyl(15.0, O.PLUG_FACE, -24.0, 0.0, O.PUMP_E)
    c = c + xcyl(12.5, O.PLUG_FACE, -56.0, O.RELIEF_LEFT, O.PUMP_E)
    de, dl = O.DRAIN
    c = c + xcyl(14.0, O.PLUG_FACE, O.SUMP_BOTTOM + 8.0, dl, de)
    # cylinder pads seat the clutch springs (front wall is solid to e 28 outside the cam chamber)
    # ---- bores and holes ----
    for u, l in O.BOLTS:
        c = c - zc(4.3, O.SPIGOT[0] - 1.0, 30.0, u, l)
    for l in (O.CYL_LEFT, -O.CYL_LEFT):                                       # operating cylinders
        c = c - zc(O.PISTON_D / 2 + 0.05, -1.0, O.CYL_E[1], 0.0, l)
    for u, l in O.OD_STUDS:                                                  # flange: stud holes and nut scallops
        c = c - zc(3.6, -1.0, O.MC_FLANGE[1] + 1.0, u, l)
        c = c - zc(9.5, O.MC_FLANGE[1], 24.0, u, l)
    lu, ll = O.OD_STUDS[G.OD_STUD_LONG]
    c = c - zc(5.0, O.MC_FLANGE[1], 46.0, lu, ll)                            # groove past the long stud
    for u, l in O.CASE_STUDS:                                                # rear face: tapped for the casing studs
        c = c - zc(TAP["1/4"], O.MC_REAR_FL[0] - 4.0, O.MC_LEN + 1.0, u, l)
    # pump bore (body, small end up) with the plug counterbore; relief valve bore; drain
    c = c - xcyl(10.2, O.SUMP_BOTTOM - 5.0, -12.0, 0.0, O.PUMP_E)
    c = c - xcyl(13.0, O.SUMP_BOTTOM - 5.0, O.SUMP_BOTTOM + 8.0, 0.0, O.PUMP_E)
    c = c - xcyl(7.6, O.SUMP_BOTTOM - 5.0, -58.0, O.RELIEF_LEFT, O.PUMP_E)
    c = c - xcyl(11.5, O.SUMP_BOTTOM - 5.0, O.SUMP_BOTTOM + 8.0, O.RELIEF_LEFT, O.PUMP_E)
    c = c - xcyl(9.0, O.SUMP_BOTTOM - 5.0, O.SUMP_BOTTOM + 14.0, dl, de)
    c = c - zc(2.8, -1.0, O.PUMP_E - 9.0, O.GRUB_UP, 0.0)                    # grub screw (47) into the pump body groove
    c = c - box(O.PUMP_HEAD[1] - 6.5, -12.0, -6.5, 6.5, O.CAM_E[0] - 4.0, O.CAM_E[1] + 4.0)   # slot for the plunger fork
    ou, ol, od = G.to_local(G.OD_OIL_PORT)
    c = c - zc(6.0, -1.0, 14.0, ou, ol)                                      # oil from the gearbox to the sump
    # filter opening and cover screws
    c = c - box(COVER_OPEN[0], COVER_OPEN[1], 30.0, O.FILTER_FACE + 1.0, COVER_OPEN[2], COVER_OPEN[3])
    for u, e in COVER_SCREWS:
        c = c - ycyl(TAP["1/4"], O.FILTER_FACE - 16.0, O.FILTER_FACE + 1.0, u, e)
    c = c - ycyl(7.0, O.SUMP_LEFT[0] - 7.0, -30.0, pu, pe)                   # plug 39
    # operating valve bore, plug counterbore; cross-shaft bore; test hole A (Sec 13)
    c = c - xcyl(5.6, O.CROSS_SHAFT[1] - 2.0, O.OPVALVE_TOP + 1.0, vl, ve)
    c = c - xcyl(8.0, O.OPVALVE_TOP - 10.0, O.OPVALVE_TOP + 1.0, vl, ve)
    xe, xu = O.CROSS_SHAFT
    c = c - ycyl(4.85, O.CHAMBER_FACE - 1.0, vl + 6.0, xu, xe)
    c = c - ycyl(9.5, vl - 8.0, vl + 8.0, xu, xe)                                # pocket for the valve cam
    c = c - ycyl(7.0, -89.3, -86.7, xu, xe)                                      # O-ring groove (item 29)
    # lever chamber: cavity open at the cover face, the solenoid seat in its rear wall
    c = c - box(CH_CAV[2], CH_CAV[3], O.CHAMBER_FACE - 1.0, -84.0, CH_CAV[0], CH_CAV[1])
    c = c - ycyl(2.45, -84.5, -70.0, xu - 14.0, xe)
    for u, e in CHAMBER_SCREWS:
        c = c - ycyl(TAP["1/4"], O.CHAMBER_FACE - 1.0, O.CHAMBER_FACE + 22.0, u, e)
    su, sl = O.SOL_AXIS
    c = c - zc(7.0, CH_CAV[1] - 1.0, CH_E1 + 1.0, su, sl)
    for u, l in SOL_SCREWS:
        c = c - zc(TAP["10-32"], CH_E1 - 10.0, CH_E1 + 1.0, u, l)
    # mounting pad screws (5/16 UNF)
    for s in (1, -1):
        for e, u in O.MOUNT_SCREWS:
            c = c - ycyl(TAP["5/16"], s * (O.MOUNT_FACE + 1.0), s * (O.MOUNT_FACE - 18.0), u, e)
    # DRAIN cast on the sump side beside the plug (Fig 6.18)
    word = _lettering("DRAIN", 7.0, 0.8)
    c = c + Location((O.SUMP_BOTTOM + 0.2, dl - 18.0, de)) * Rot(0, -90, 0) * word
    return _out(c, spec)


# =================================================================================================
# brake ring (item 7)
# =================================================================================================
def brake_ring(spec) -> Part:
    e0, e1 = O.BR
    c0, c1 = O.CONE_E
    r0, r1 = O.BR_CONE_R
    k = (r1 - r0) / (c1 - c0)
    prof = [(r0 - k * (c0 - e0) + 0.0, e0), (O.CASE_R, e0), (O.CASE_R, e0 + 3.0), (O.CASE_R + 1.5, e0 + 5.0),
            (O.CASE_R + 1.5, e1 - 5.0), (O.CASE_R, e1 - 3.0), (O.CASE_R, e1), (r1 + k * (e1 - c1), e1)]
    b = Sh.revolved(prof)
    for u, l in O.CASE_STUDS:
        b = b - zc(3.6, e0 - 1, e1 + 1, u, l)
    # lug with a slot on the upper right (Fig 6.13 item 7)
    a = -52.0
    lug = Rot(0, 0, a) * box(O.CASE_R - 2.0, O.CASE_R + 8.0, -9.0, 9.0, e0 + 3.0, e1 - 3.0)
    lug = lug - Rot(0, 0, a) * box(O.CASE_R + 3.0, O.CASE_R + 9.0, -3.0, 3.0, e0 + 2.0, e1 - 2.0)
    b = b + lug
    return _out(b, spec)


# =================================================================================================
# rear casing (item 8)
# =================================================================================================
RB_BOSSES = [(G.REMOTE_BRACKET_UP, l, O.e_of(G.REMOTE_BRACKET_D)) for l in G.REMOTE_BRACKET_HOLES]    # (up, left, e)
SP_E, SP_U = O.SPEEDO_AXIS_E, O.SPEEDO_UP
SP_LOCK = (SP_E + 23.0, SP_U)                                                # locking screw (86): (e, up)


def rear_casing(spec) -> Part:
    f0, f1 = O.RC_FLANGE
    fb0, fb1 = O.FRONT_BRG_E
    outer = [(0.0, f0), (O.CASE_R, f0), (O.CASE_R, f1), (O.RC_BODY_R, f1), (O.RC_BODY_R - 1.0, 130.0),
             (78.0, 146.0), (64.0, 160.0), (46.0, fb0 + 0.0), (46.0, fb1 + 2.0), (40.0, fb1 + 8.0),
             (38.0, O.REAR_BRG_E[0] - 6.0), (40.0, O.REAR_BRG_E[0] - 2.0), (40.0, O.RC_END - 6.0),
             (38.0, O.RC_END), (0.0, O.RC_END)]
    c = Sh.revolved(outer)
    # flat-topped hump over the front (Fig 6.13 item 8) and a keel underneath
    c = c + zprism(rounded([(20.0, -40.0), (62.0, -40.0), (62.0, 40.0), (20.0, 40.0)], 8.0), f1 - 1.0, 176.0)
    c = c + box(-58.0, -20.0, -8.0, 8.0, f1 - 1.0, fb1)
    # remote bracket bosses (P5a datums REMOTE_BRACKET_*): the left one on a web from the hump
    for u, l, e in RB_BOSSES:
        c = c + xcyl(9.0, 34.0, u, l, e)
        lo, hi = sorted((l, 0.6 * l))
        c = c + box(34.0, u - 4.0, lo, hi, e - 3.0, e + 3.0)
    # speedometer drive boss on the right below the output shaft, and its locking screw lug
    c = c + ycyl(16.0, -20.0, O.SPEEDO_BOSS_LEFT, SP_U, SP_E)
    c = c + ycyl(7.5, -30.0, O.SPEEDO_BOSS_LEFT - 4.0, SP_LOCK[1], SP_LOCK[0])
    c = c + box(SP_U - 7.5, SP_U + 7.5, O.SPEEDO_BOSS_LEFT, -30.0, SP_E, SP_LOCK[0])
    # ---- inside ----
    inner = [(0.0, f0 - 1.0), (76.0, f0 - 1.0), (76.0, 138.0), (66.0, 150.0), (48.0, 160.0), (37.5, 164.0),
             (O.OUT_BRG_FRONT[1] / 2, 164.0), (O.OUT_BRG_FRONT[1] / 2, fb1), (25.0, fb1 + 1.0),
             (25.0, O.REAR_BRG_E[0] - 2.0), (28.0, O.REAR_BRG_E[0] - 2.0), (28.0, O.REAR_BRG_E[0]),
             (O.OUT_BRG_REAR[1] / 2, O.REAR_BRG_E[0]), (O.OUT_BRG_REAR[1] / 2, O.SEAL_E[0]),
             (31.75, O.SEAL_E[0]), (31.75, O.RC_END + 1.0), (0.0, O.RC_END + 1.0)]
    c = c - Sh.revolved(inner)
    for u, l in O.CASE_STUDS:
        c = c - zc(3.6, f0 - 1, f1 + 1, u, l)
        c = c - zc(8.5, f1, f1 + 14.0, u, l)                                 # spot faces for the nuts
    for u, l, e in RB_BOSSES:
        c = c - xcyl(TAP["1/4"], u - 20.0, u + 1.0, l, e)
    c = c - ycyl(SP_HOUSING_R + 0.05, O.SPEEDO_BOSS_LEFT - 1.0, -12.0, SP_U, SP_E)
    c = c - ycyl(9.5, -12.5, 14.0, SP_U, SP_E)                                 # pinion pocket under the worm
    c = c - ycyl(TAP["1/4"], O.SPEEDO_BOSS_LEFT - 5.0, -46.0, SP_LOCK[1], SP_LOCK[0])
    return _out(c, spec)


SP_HOUSING_R = O.SPEEDO_HOUSING_D / 2


# =================================================================================================
# fixings
# =================================================================================================
def od_nut(spec):
    """1/4 in UNF nut on an overdrive stud, on the main casing flange (z: from the flange, rearward)."""
    return C._l(F.hex_nut("1/4"), spec)


def case_stud(spec):
    return C._l(C.stud("1/4", spec.nom("length") / IN), spec)


# ---- filter cover (14), gasket (15) --------------------------------------------------------------
def filter_cover(spec) -> Part:
    """Flat plate on the left face of the sump, built lying on it (y outward)."""
    t = spec.nom("thickness")
    e0, e1, u0, u1 = O.COVER
    poly = rounded([(u0, e0), (u1, e0), (u1, e1), (u0, e1)], 6.0)
    p = Location((0, O.FILTER_FACE + 0.8, 0)) * extrude(Plane.XZ * Polygon(*poly, align=None), -t)
    # pressed dish in the middle over the filter
    dish = rounded([(u0 + 12, e0 + 12), (u1 - 12, e0 + 12), (u1 - 12, e1 - 12), (u0 + 12, e1 - 12)], 8.0)
    p = p + Location((0, O.FILTER_FACE + 0.8 + t - 0.01, 0)) * extrude(Plane.XZ * Polygon(*dish, align=None), -2.0)
    for u, e in COVER_SCREWS:
        p = p - ycyl(3.6, O.FILTER_FACE, O.FILTER_FACE + t + 4.0, u, e)
    return _out(p, spec)


def filter_cover_gasket(spec) -> Part:
    t = spec.nom("thickness")
    e0, e1, u0, u1 = O.COVER
    poly = rounded([(u0, e0), (u1, e0), (u1, e1), (u0, e1)], 6.0)
    g = Location((0, O.FILTER_FACE, 0)) * extrude(Plane.XZ * Polygon(*poly, align=None), -t)
    g = g - box(COVER_OPEN[0], COVER_OPEN[1], O.FILTER_FACE - 1, O.FILTER_FACE + 2, COVER_OPEN[2], COVER_OPEN[3])
    for u, e in COVER_SCREWS:
        g = g - ycyl(3.6, O.FILTER_FACE - 1, O.FILTER_FACE + 2, u, e)
    return _out(g, spec)


# ---- plugs ---------------------------------------------------------------------------------------
def hex_plug(thread_d, thread_l, af, head_h, collar=0.0):
    """Hexagon-headed plug: head underside at z = 0, thread along +z."""
    from build123d import RegularPolygon
    h = extrude(RegularPolygon(af / math.sqrt(3), 6), head_h).moved(Location((0, 0, -head_h)))
    p = h + zc(thread_d / 2, 0.0, thread_l)
    if collar:
        p = p + zc(af / 2 + collar, -1.2, 0.0)
    p = p - zc(thread_d / 2 + 1, thread_l - 0.6, thread_l + 1) + zc(thread_d / 2 - 0.6, thread_l - 0.61, thread_l)
    return p


def drain_plug(spec) -> Part:
    """Item 18: hexagon plug with a flange, into the sump underside, sealing on washer 19."""
    p = hex_plug(spec.nom("thread_diameter"), 12.0, 22.0, 9.0, collar=2.0)
    p = p - Location((0, 0, -9.0)) * Box(14, 2.0, 2.0)                       # lockwire-free, a cast DRAIN beside it
    return C._l(p, spec)


def sealing_washer(spec) -> Part:
    return C._l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def plug39(spec) -> Part:
    return C._l(hex_plug(spec.nom("thread_diameter"), 10.0, 14.3, 6.5, collar=1.0), spec)


# ---- speedometer drive (items 84-90) and the cable end -------------------------------------------
def _speedo_loc():
    """Frame at the boss face: local z points inward (+y toward the centre), as built."""
    return Location((SP_U, O.SPEEDO_BOSS_LEFT, SP_E)) * Rot(-90, 0, 0)


def speedo_housing2(spec) -> Part:
    r = SP_HOUSING_R
    b = Sh.revolved([(3.2, -18.0), (8.2, -18.0), (9.5, -16.5), (9.5, -4.0), (15.0, -4.0), (15.0, 0.0),
                     (r, 0.0), (r, 40.0), (r - 1.5, 41.5), (5.0, 41.5), (5.0, 44.0), (3.2, 44.0)])
    b = b - Sh.revolved([(r - 2.4, 6.0), (r + 1, 6.0), (r + 1, 8.6), (r - 2.4, 8.6)])
    b = b - zc(7.0, -19.0, -6.0)
    b = b - Location((0, -(15.0 + 2.0), -2.0)) * Box(8.0, 10.0, 5.0)                    # notch toward the locking screw
    for k in range(3):
        z = -15.5 + 3.6 * k
        b = b - Sh.revolved([(9.0, z), (9.7, z), (9.7, z + 1.0), (9.0, z + 1.0)])
    b = b - Location((0, 5.0, 30.0)) * Rot(0, 90, 0) * Cylinder(1.6, 30.0)
    return _out(_speedo_loc() * b, spec)


def speedo_o_ring(spec) -> Part:
    r = SP_HOUSING_R - 1.2
    o = Location((0, 0, 7.3)) * Torus(r, 1.2)
    return _out(_speedo_loc() * o, spec)


def speedo_pin(spec) -> Part:
    p = Location((0, 5.0, 30.0)) * Rot(0, 90, 0) * Sh.chamfered_cyl(3.2, 2 * SP_HOUSING_R - 4.0, 0.3, z0=-(SP_HOUSING_R - 2.0))
    return _out(_speedo_loc() * p, spec)


def speedo_seal(spec) -> Part:
    s = Sh.revolved([(3.4, -17.6), (6.95, -17.6), (6.95, -10.0), (4.5, -10.0), (4.5, -15.0), (3.4, -14.0)])
    return _out(_speedo_loc() * s, spec)


def speedo_gear(spec) -> Part:
    """Driven gear 89 (17H8021): a small helical pinion on a spindle; the spindle end has the
    square socket the cable drives through (Fig 6.13 item 89)."""
    n = int(spec.nom("teeth"))
    rp = O.SPEEDO_PINION_R
    beta = 25.0
    mn = 2 * rp * math.cos(math.radians(beta)) / n
    w = 9.0
    z_in = -O.SPEEDO_BOSS_LEFT                                   # boss face to the shaft plane (y = 0)
    g = GR.helical(n, mn, beta, w, hand="left").moved(Location((0, 0, z_in - w / 2)))
    g = g + zc(3.1, -20.0, z_in + w / 2 + 3.0)
    g = g + zc(rp - 2.5, z_in + w / 2 - 0.1, z_in + w / 2 + 2.0)
    g = g - Location((0, 0, -20.0)) * Box(2.6, 2.6, 8.0)
    return _out(_speedo_loc() * g, spec)


def lock_screw(spec) -> Part:
    """Locking screw 86: hexagon head with a dog that drops into the housing flange notch."""
    L = spec.nom("length")
    s = C._l(F.hex_bolt("1/4", L / IN), spec)
    loc = Location((SP_LOCK[1], O.SPEEDO_BOSS_LEFT - 4.0 - 1.6, SP_LOCK[0])) * Rot(-90, 0, 0)
    return _out(loc * s, spec)


def lock_washer(spec) -> Part:
    """Washer 87 under the locking screw head; its rim overlaps the housing flange."""
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t)
    loc = Location((SP_LOCK[1], O.SPEEDO_BOSS_LEFT - 4.0 - t, SP_LOCK[0])) * Rot(-90, 0, 0)
    return _out(loc * w, spec)


ANGLE_OUT = 46.0                       # angle drive: boss face to the output axis
ANGLE_ROT = -45.0                      # output turned forward and down, under the solenoid


def angle_drive(spec) -> Part:
    """Speedometer cable angle drive (MGOC 120694, listed for the three-synchro MGB): a knurled nut
    on the housing thread, a body with the bevel gears, and the output turned forward along the
    car, threaded for the cable nut."""
    a = Sh.revolved([(9.8, -32.0), (14.5, -32.0), (15.0, -31.0), (15.0, -19.0), (14.5, -18.0), (9.8, -18.0)])
    for k in range(18):                                          # knurl on the nut
        ang = 360.0 * k / 18
        a = a - Location((15.0 * math.cos(math.radians(ang)), 15.0 * math.sin(math.radians(ang)), -25.0)) * \
            Rot(0, 0, ang) * Box(1.6, 1.0, 14.0)
    body = zc(11.0, -ANGLE_OUT - 11.0, -31.5)
    body = body + Location((0, 0, -ANGLE_OUT)) * Rot(0, 90, 0) * Cylinder(11.0, 22.0)
    out_boss = Location((-11.0, 0, -ANGLE_OUT)) * Rot(0, -90, 0) * Cylinder(8.5, 20.0, align=BASE)
    out_thr = Location((-31.0, 0, -ANGLE_OUT)) * Rot(0, -90, 0) * Cylinder(7.5, 12.0, align=BASE)
    a = a + body + out_boss + out_thr
    for k in range(3):
        x = -33.0 - 3.6 * k
        a = a - Location((x, 0, -ANGLE_OUT)) * Rot(0, 90, 0) * Sh.tube(17.0, 14.0, 1.0)
    a = a - Location((-44.0, 0, -ANGLE_OUT)) * Rot(0, 90, 0) * Box(2.6, 2.6, 8.0)               # square drive out
    # local frame: z = 0 at the boss face, -z outward (right); output along local -x, which the
    # placement turns to point forward
    loc = _speedo_loc() * Rot(0, 0, ANGLE_ROT)
    return _out(loc * a, spec)


def cable_end(spec) -> Part:
    """Speedometer cable end on the angle drive output: the knurled ferrule nut, the outer casing
    stub and the inner cable's square end (the rest of the cable is P10/P11)."""
    L = spec.nom("length")
    n = Sh.revolved([(7.6, 0.0), (11.0, 0.0), (11.0, 14.0), (9.0, 16.0), (5.0, 16.0), (5.0, 22.0), (4.6, 22.0), (4.6, L),
                     (2.0, L), (2.0, 16.0), (7.6, 16.0)])
    for k in range(16):
        ang = 360.0 * k / 16
        n = n - Location((11.0 * math.cos(math.radians(ang)), 11.0 * math.sin(math.radians(ang)), 7.0)) * \
            Rot(0, 0, ang) * Box(1.4, 1.0, 12.0)
    n = n + zc(2.2, -1.0, L) + Location((0, 0, -4.0)) * Box(2.5, 2.5, 8.0, align=BASE)   # inner cable and its square
    loc = _speedo_loc() * Rot(0, 0, ANGLE_ROT) * Location((-43.0, 0, -ANGLE_OUT)) * Rot(0, -90, 0)
    return _out(loc * n, spec)


WASHER = C.WASHER

PARTS = {
    "gearbox.overdrive-casing.main-casing": {"build": main_casing},
    "gearbox.overdrive-casing.brake-ring": {"build": brake_ring},
    "gearbox.overdrive-casing.rear-casing": {"build": rear_casing},
    "gearbox.overdrive-casing.od-nut": {"build": od_nut},
    "gearbox.overdrive-casing.od-washer": {"build": C.spring_washer, "probes": WASHER},
    "gearbox.overdrive-casing.case-stud": {"build": case_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.overdrive-casing.case-nut": {"build": od_nut},
    "gearbox.overdrive-casing.case-washer": {"build": C.spring_washer, "probes": WASHER},
    "gearbox.overdrive-casing.filter-cover": {"build": filter_cover},
    "gearbox.overdrive-casing.filter-cover-gasket": {"build": filter_cover_gasket},
    "gearbox.overdrive-casing.cover-screw": {"build": C.bolt("1/4"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.overdrive-casing.cover-washer": {"build": C.spring_washer, "probes": WASHER},
    "gearbox.overdrive-casing.drain-plug": {"build": drain_plug},
    "gearbox.overdrive-casing.drain-washer": {"build": sealing_washer, "probes": WASHER},
    "gearbox.overdrive-casing.plug": {"build": plug39},
    "gearbox.overdrive-casing.plug-washer": {"build": sealing_washer, "probes": WASHER},
    "gearbox.overdrive-casing.speedo-housing": {"build": speedo_housing2},
    "gearbox.overdrive-casing.speedo-o-ring": {"build": speedo_o_ring},
    "gearbox.overdrive-casing.speedo-pin": {"build": speedo_pin},
    "gearbox.overdrive-casing.speedo-seal": {"build": speedo_seal},
    "gearbox.overdrive-casing.speedo-gear": {"build": speedo_gear},
    "gearbox.overdrive-casing.lock-screw": {"build": lock_screw},
    "gearbox.overdrive-casing.lock-washer": {"build": lock_washer},
    "gearbox.overdrive-casing.angle-drive": {"build": angle_drive},
    "gearbox.overdrive-casing.cable-end": {"build": cable_end},
}
