"""Lucas 18ACR alternator, its pulley, fan and nut, the pivot and adjusting link fixings, the rear
mounting bracket and the fan belt's alternator end (the belt itself is cooling.fan-belt).
Haynes Ch 10 Sec 11, 20-22 (18ACR), Fig 10.3 (16AC, the same construction); Ch 2 Fig 2.1 and
Fig 2.6 (pivot bolts, bracket, link stud and link); specs printed p162.

The alternator parts are built in the alternator frame (mgb.electrical_layout.alt_local):
local z forward along the shaft from the belt plane, local x = car down, local y = car left.
The assembly places them with one Location. The bracket, link and fixings are built in the
car frame.
"""
import math

from build123d import Axis, Box, Cylinder, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import electrical_layout as E, elec_shapes as X, fasteners as F, poly2d as P2, shapes as Sh, timing_layout as T
from mgb.elec_shapes import box, hull_xy, label, polar, rev, sector, tryfillet, xc, yc, zc

PIV_L = E.alt_lxly(*E.PIVOT)              # local (x, y) of the pivot line
LINK_L = E.alt_lxly(*E.LINK_LUG)          # local (x, y) of the adjusting lug hole
TB_ANGLES = (75.0, 195.0, 315.0)          # through-bolts (local polar angle from +x toward +y)
TB_R = E.BODY_R + 3.5


def _ang(p):
    return math.degrees(math.atan2(p[1], p[0]))


def _lug(centre, r_boss, z0, z1, root_r=40.0):
    """Tapered cast lug from the body out to a boss at `centre` (local x, y)."""
    return hull_xy([(0.0, 0.0, root_r), (centre[0], centre[1], r_boss)], z0, z1)


def _tb_ears(z0, z1):
    out = None
    for a in TB_ANGLES:
        x, y = polar(TB_R, a)
        e = hull_xy([(0.0, 0.0, 45.0), (x, y, 6.0)], z0, z1)
        out = e if out is None else out + e
    return out


def _tb_holes(z0, z1, r=2.9):
    out = None
    for a in TB_ANGLES:
        x, y = polar(TB_R, a)
        h = zc(r, z0, z1, x, y)
        out = h if out is None else out + h
    return out


# ---- the alternator (Fig 10.3 items 3-13) ----------------------------------------------------------
def drive_end_bracket(spec) -> Part:
    """Item 13: die-cast drive end bracket. Front wall with five spokes and the large
    cooling openings between them round the bearing boss, a skirt back to the stator, the
    pivot lug and the tapped adjusting lug, and ears for the three through-bolts."""
    z0, z1 = E.DE_Z
    R = E.BRACKET_R
    b = rev([(13.0, z0), (R, z0), (R, z1 - 4.0), (R - 4.0, z1), (24.0, z1), (24.0, z1 + 2.0),
             (13.0, z1 + 2.0)])
    b = b - rev([(26.0, z0 - 1), (R - 4.0, z0 - 1), (R - 4.0, z1 - 7.0), (26.0, z1 - 7.0)])
    for k in range(5):                                       # openings in the front wall
        a = 90.0 + 72.0 * k
        b = b - sector(27.0, R - 7.0, a + 10.0, a + 62.0, z1 - 8.0, z1 + 1.0)
    for k in range(10):                                      # slots round the skirt
        a = 18.0 + 36.0 * k
        if min(abs(((a - _ang(PIV_L)) + 180) % 360 - 180), abs(((a - _ang(LINK_L)) + 180) % 360 - 180)) < 22:
            continue
        b = b - (Rot(0, 0, a) * box(R - 6.0, R + 1.0, -4.0, 4.0, z0 + 6.0, z1 - 9.0))
    piv = _lug(PIV_L, 10.0, E.FRONT_LUG_Z[0], E.FRONT_LUG_Z[1], 46.0) - zc(4.2, -80, 10, *PIV_L)
    link = _lug(LINK_L, 9.0, E.FRONT_LUG_Z[0], E.FRONT_LUG_Z[1], 46.0) - zc(3.3, -80, 10, *LINK_L)
    b = b + (piv - zc(R - 4.0, z0, z1 - 7.0)) + (link - zc(R - 4.0, z0, z1 - 7.0))
    b = b + (_tb_ears(z0 + 1.5, z0 + 12.0) - zc(R - 4.0, z0 - 1, z1))   # clear of the front plate behind
    b = b - _tb_holes(z0, z0 + 13.0)
    b = b - zc(8.8, z1 - 9.0, z1 + 6.0)                      # shaft
    return label(b, spec)


def stator(spec) -> Part:
    """Item 5: laminated stator ring between the brackets, its stack showing in shallow
    grooves, notched for the through-bolts."""
    z0, z1 = E.STATOR_Z
    s = Sh.tube(2 * E.BODY_R, 2 * (E.BRACKET_R - 6.0), z1 - z0, z0)
    for k in range(1, 6):                                    # lamination stack lines
        zz = z0 + (z1 - z0) * k / 6
        s = s - Sh.tube(2 * E.BODY_R + 2, 2 * (E.BODY_R - 0.5), 0.7, zz - 0.35)
    for a in TB_ANGLES:
        x, y = polar(E.BODY_R + 1.0, a)
        s = s - zc(4.0, z0 - 1, z1 + 1, x, y)
    return label(s, spec)


def slip_ring_bracket(spec) -> Part:
    """Item 4: slip ring end bracket. Cup with radial cooling slots round its back, the rear
    bearing boss, the rear pivot lug and the through-bolt ears."""
    z0, z1 = E.SR_Z
    R = E.BRACKET_R
    b = rev([(10.0, z0 - 4.0), (20.0, z0 - 4.0), (20.0, z0), (R - 3.0, z0), (R, z0 + 4.0), (R, z1),
             (10.0, z1)])
    b = b - rev([(22.0, z0 + 6.0), (R - 4.0, z0 + 6.0), (R - 4.0, z1 + 1), (22.0, z1 + 1)])
    for k in range(12):                                      # slots in the back of the skirt
        a = 15.0 + 30.0 * k
        if abs(((a - _ang(PIV_L)) + 180) % 360 - 180) < 18:
            continue
        b = b - (Rot(0, 0, a) * box(R - 6.0, R + 1.0, -3.5, 3.5, z0 + 6.0, z0 + 34.0))
    for k in range(6):                                       # openings in the end wall round the boss
        b = b - sector(26.0, 44.0, 60.0 * k + 8.0, 60.0 * k + 48.0, z0 - 1, z0 + 7.0)
    piv = _lug(PIV_L, 10.0, E.REAR_LUG_Z[0], E.REAR_LUG_Z[1], 46.0) - zc(4.2, -200, 0, *PIV_L)
    b = b + (piv - zc(R - 4.0, z0 + 6.0, z1 + 1))
    b = b + (_tb_ears(z1 - 12.0, z1) - zc(R - 4.0, z0, z1 + 1))
    b = b - _tb_holes(z1 - 13.0, z1 + 1)
    b = b - zc(7.0, z0 - 5, z0 + 7)
    return label(b, spec)


def end_cover(spec) -> Part:
    """Item 1: moulded end cover over the rectifier and regulator, with its grille of slots,
    the opening for the terminal block and two fixing screws."""
    z0, z1 = E.COVER_Z
    r = E.BRACKET_R - 3.0
    c = rev([(0, z0), (r - 6.0, z0), (r, z0 + 6.0), (r, z1), (r - 2.5, z1), (r - 2.5, z0 + 3.0), (0, z0 + 3.0)])
    for k in range(-4, 5):                                   # grille slots across the end
        if k in (-1, 0):
            continue
        c = c - box(-4.0 + k * 10.0 - 2.0, -4.0 + k * 10.0 + 2.0, -32.0, 32.0, z0 - 1, z0 + 4.0)
    c = c - box(-14.0, 8.0, -44.0, -24.0, z0 - 1, z0 + 4.0)   # terminal block opening (outboard side)
    for sy in (-38.0, 38.0):                                 # cover screw bosses
        c = c + zc(4.5, z0 - 1.5, z0 + 3.0, 30.0, sy) - zc(1.8, z0 - 2, z0 + 4, 30.0, sy)
    return label(c, spec)


def rotor(spec) -> Part:
    """Items 6-9: shaft with its thread and key, the claw-pole rotor (seen through the
    openings) and the slip rings at the back."""
    s = zc(8.5, E.SR_Z[0] + 2.0, E.DE_FACE_Z + 6.0) + zc(7.5, E.DE_FACE_Z + 6.0, E.NUT_Z[1] + 2.0)
    poles = zc(44.0, E.STATOR_Z[0] + 2.0, E.STATOR_Z[1] - 2.0)
    for k in range(12):                                      # interleaved claw fingers
        a = 30.0 * k
        lo = E.STATOR_Z[0] + 2.0 if k % 2 else E.STATOR_Z[0] + 10.0
        hi = E.STATOR_Z[1] - 10.0 if k % 2 else E.STATOR_Z[1] - 2.0
        poles = poles + (Rot(0, 0, a) * box(38.0, 49.0, -7.0, 7.0, lo, hi))
    rings = zc(9.5, E.SR_Z[0] + 6.0, E.SR_Z[0] + 22.0)
    for zz in (E.SR_Z[0] + 10.0, E.SR_Z[0] + 17.0):
        rings = rings - Sh.tube(22, 18.2, 1.5, zz)
    fans = Sh.tube(84.0, 56.0, 4.0, E.DE_Z[0] + 2.0) + Sh.tube(84.0, 56.0, 4.0, E.SR_Z[1] - 6.0)   # internal fans
    return label(s + poles + rings + fans, spec)


def fan(spec) -> Part:
    """Item 13 (front): pressed steel cooling fan behind the pulley, its blades bent back
    off a backing disc."""
    z0, z1 = E.FAN_Z
    d = spec.nom("diameter")
    f = Sh.tube(d, 24.0, 1.6, z1 - 1.6) + Sh.tube(34.0, 17.6, z1 - z0, z0)
    n = int(spec.nom("blades"))
    for k in range(n):
        a = 360.0 * k / n
        blade = Rot(0, 0, a) * Location((d / 4 + 6.0, 0, (z0 + z1) / 2)) * Rot(18.0, 0, 0) * Box(d / 2 - 14.0, 1.6, z1 - z0 - 2.0)
        f = f + blade
    f = f & zc(d / 2, z0, z1)
    return label(f, spec)


def pulley(spec) -> Part:
    """Pressed V pulley, 2 3/4 in outside, for the 3/8 in fan belt (MGOC 12G1054)."""
    r = spec.nom("outside_diameter") / 2
    z0, z1 = E.PULLEY_Z
    w = z1 - z0
    g = 5.6                                                  # half the groove width at the rim (40 deg V)
    root = r - 10.0
    p = rev([(8.2, z0 - 3.0), (16.0, z0 - 3.0), (16.0, z0), (r, z0), (r, z0 + (w / 2 - g)), (root, -1.6),
             (root, 1.6), (r, z1 - (w / 2 - g)), (r, z1), (8.2, z1)])
    p = p - Location((0, 0, z1 - 1.5)) * Box(3.0, 18.0, 4.0)   # keyway mark
    return label(p, spec)


def shaft_nut(spec) -> Part:
    """Item 14: shaft nut on its spring washer, 25 lbf ft (p162)."""
    af = spec.nom("across_flats")
    z0, z1 = E.NUT_Z
    n = extrude(Plane.XY.offset(z0 + 2.0) * RegularPolygon(af / math.sqrt(3), 6), z1 - z0 - 2.0)
    n = n + Sh.tube(af * 1.05, 17.0, 2.0, z0)
    n = n - zc(7.6, z0 - 1, z1 + 1)
    return label(n, spec)


def through_bolt(spec) -> Part:
    """Item 3: through-bolt, head at the slip ring end, screwed into the drive end bracket."""
    x, y = polar(TB_R, 0.0)
    L0, L1 = E.SR_Z[1] - 12.0, E.DE_Z[0] + 11.0
    b = zc(2.6, L0, L1, x, y) + zc(4.6, L0 - 3.0, L0, x, y)
    b = b - (Location((x, y, L0 - 3.5)) * Box(1.2, 6.0, 2.0))
    return label(b, spec)


def terminal_plug(spec) -> Part:
    """Moulded three-way plug on the terminal blades at the back (the two + blades and IND); the
    harness leads (P10b, electrical.wiring-charging) enter its rear face, each through a moulded
    shroud."""
    z0 = E.COVER_Z[0]
    p = box(-12.0, 6.0, -42.0, -26.0, z0 - 14.0, z0 + 2.0)
    p = tryfillet(p, p.edges().filter_by(Axis.Z), 2.0)
    for k, dx in enumerate((-8.0, -3.0, 2.0)):
        r = 2.4 if k < 2 else 1.9
        p = p + zc(r + 0.9, z0 - 17.0, z0 - 13.9, dx, -34.0)              # lead shroud
    return label(p, spec)


# ---- mounting (Fig 2.6 items 14-19, 25-36) ---------------------------------------------------------
def rear_bracket(spec) -> Part:
    """Item 14: rear mounting bracket. A foot on the threaded boss on the right of the block
    (screw 16 and spring washer 15) and an ear out to the rear pivot bolt (31-33)."""
    bx, bz = E.REAR_BRACKET_BOSS
    fy = E.BOSS_FACE_Y
    t = spec.nom("thickness")
    py, pz = E.PIVOT
    ex0, ex1 = E.REAR_EAR_X
    foot = box(bx - 13.0, ex1, fy - t, fy, bz - 16.0, bz + 13.0)
    foot = tryfillet(foot, foot.edges().filter_by(Axis.Y), 6.0)
    ear = Location((ex0, 0, 0)) * Rot(0, 90, 0) * hull_xy([(-pz, py, 13.0), (-(bz - 8.0), fy - 6.0, 10.0),
                                                           (-(bz + 6.0), fy - 6.0, 6.0)], 0.0, ex1 - ex0)
    web = box(ex0, ex1, fy - 18.0, fy - 0.01, bz - 16.0, bz + 6.0)
    b = foot + ear + web
    b = b - yc(4.2, fy - 30.0, fy + 1.0, bx, bz)
    b = b - xc(4.2, ex0 - 1, ex1 + 1, py, pz)
    return label(b, spec)


def link(spec) -> Part:
    """Item 25: adjusting link, a flat strap with an eye on the stud and a curved slot
    struck about the pivot line for the link screw."""
    t = spec.nom("thickness")
    w = spec.nom("width")
    x0 = E.LINK_X[0]
    sy, sz = E.LINK_STUD
    ly, lz = E.LINK_LUG
    py, pz = E.PIVOT
    R = math.hypot(ly - py, lz - pz)
    a_l = math.atan2(lz - pz, ly - py)
    pts = []
    arc = [a_l - 0.16 + 0.32 * k / 10 for k in range(11)]
    outline = P2.hull(P2.circle_pts(sy, sz, w / 2, 20) +
                      [p for a in arc for p in P2.circle_pts(py + R * math.cos(a), pz + R * math.sin(a), w / 2, 12)])
    s = extrude(Plane.YZ.offset(x0) * Polygon(*outline, align=None), t, dir=(1, 0, 0))
    slot = None
    for a in [a_l - 0.13 + 0.26 * k / 12 for k in range(13)]:
        c = xc(4.3, x0 - 1, x0 + t + 1, py + R * math.cos(a), pz + R * math.sin(a))
        slot = c if slot is None else slot + c
    s = s - slot - xc(4.3, x0 - 1, x0 + t + 1, sy, sz)
    return label(s, spec)


def link_stud(spec) -> Part:
    """Item 17: adjusting link stud (pillar), screwed into the engine front through the front
    plate, with a hexagon collar that stands the link off to the drive end bracket's face."""
    sy, sz = E.LINK_STUD
    plate = T.PLATE_FACE + 1.65                       # on the pressed panel face
    col = Location((plate, sy, sz)) * Rot(0, 90, 0) * extrude(RegularPolygon(spec.nom("collar_af") / math.sqrt(3), 6),
                                                              E.LINK_X[0] - plate - 0.2)
    s = xc(3.97, plate - 14.0, plate, sy, sz) + col + xc(3.97, E.LINK_X[0] - 0.2, E.LINK_X[1] + 9.0, sy, sz)
    return label(s, spec)


def bolt(size, length_in):
    def build(spec) -> Part:
        return label(F.hex_bolt(size, length_in), spec)
    return build


def nut(size):
    def build(spec) -> Part:
        return label(F.hex_nut(size), spec)
    return build


def spring_washer(spec) -> Part:
    """Square-section spring washer, split and set."""
    i, o, t = spec.nom("inside_diameter"), spec.nom("outside_diameter"), spec.nom("thickness")
    w = Sh.washer(o, i, t) - Location((o / 2 - (o - i) / 4, 0, t / 2)) * Box((o - i) / 2 + 1, 0.8, t + 1)
    return label(w, spec)


def plain_washer(size):
    def build(spec) -> Part:
        return label(F.plain_washer(size), spec)
    return build


PARTS = {
    "electrical.charging.drive-end-bracket": {"build": drive_end_bracket},
    "electrical.charging.stator": {"build": stator,
                                   "probes": {"outside_diameter": lambda p: p.bounding_box().size.X}},
    "electrical.charging.slip-ring-bracket": {"build": slip_ring_bracket},
    "electrical.charging.end-cover": {"build": end_cover},
    "electrical.charging.rotor": {"build": rotor},
    "electrical.charging.fan": {"build": fan, "probes": {"diameter": lambda p: p.bounding_box().size.X}},
    "electrical.charging.pulley": {"build": pulley,
                                   "probes": {"outside_diameter": lambda p: p.bounding_box().size.X}},
    "electrical.charging.shaft-nut": {"build": shaft_nut},
    "electrical.charging.through-bolt": {"build": through_bolt},
    "electrical.charging.terminal-plug": {"build": terminal_plug},
    "electrical.charging.rear-bracket": {"build": rear_bracket},
    "electrical.charging.link": {"build": link},
    "electrical.charging.link-stud": {"build": link_stud},
    "electrical.charging.pivot-bolt": {"build": bolt("5/16", 1.5)},
    "electrical.charging.link-screw": {"build": bolt("5/16", 0.75)},
    "electrical.charging.bracket-screw": {"build": bolt("5/16", 0.75)},
    "electrical.charging.nut": {"build": nut("5/16")},
    "electrical.charging.spring-washer": {"build": spring_washer},
    "electrical.charging.plain-washer": {"build": plain_washer("5/16")},
}
