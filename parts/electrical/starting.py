"""Lucas M418G inertia-engaged starter, its mounting bolts, the remote starter solenoid, the
solenoid-to-starter cable and the engine earth strap. Haynes Ch 10 Sec 23-26 and Fig 10.4
(printed p168), specs printed p162; Ch 1 Sec 6 (removal order).

The starter parts are built in the starter frame (mgb.electrical_layout.starter_local): local z
forward along the axis from the rear plate's front face, local x = car down, local y = car
left; the assembly places them with one Location. The solenoid and the cables are built in the
car frame.
"""
import math

from build123d import Axis, Box, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import body_layout as BL, electrical_layout as E, elec_shapes as X, fasteners as F, shapes as Sh
from mgb.elec_shapes import box, hull_xy, label, polar, rev, tryfillet, xc, yc, zc

XF0 = E.REAR_PLATE_FRONT_X
R = E.YOKE_R
Z_FL = E.FLANGE_T                                  # flange front face
Z_YOKE = (E.YOKE_X[0] - XF0, E.YOKE_X[1] - XF0)    # 15 .. 118
Z_END = E.STARTER_FRONT_X - XF0                    # front of the shaft cap
BOLTS_L = [E.starter_local(y, z) for y, z in E.starter_bolt_points()]
TB_ANG = (45.0, 225.0)                             # the two through-bolts (local polar)
TB_R = R - 7.5
X_SPRING = (-288.0 - XF0, -266.0 - XF0)          # main spring and anchor plates, behind the ring gear (x -262.5)


def _plate_screws():
    import importlib.util
    from pathlib import Path
    sp = importlib.util.spec_from_file_location("_plates", Path(__file__).resolve().parents[2] / "parts" / "engine" / "block" / "plates.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.REAR_SCREWS_5_16 + m.REAR_SCREWS_3_8


def _term_dir():
    a = math.radians(E.TERMINAL_ANGLE)
    dy, dz = math.cos(a), math.sin(a)
    return (-dz, dy)                               # local (x, y) unit vector


def drive_end_bracket(spec) -> Part:
    """Item 19: drive end bracket. A two-eared flange on the engine rear plate with a spigot
    into the starter aperture, the shaft bush boss and the step the yoke sits on."""
    t = spec.nom("flange_thickness")
    fl = hull_xy([(0.0, 0.0, R + 2.0)] + [(x, y, 10.0) for x, y in BOLTS_L], 0.0, t)
    fl = tryfillet(fl, fl.edges().filter_by(Axis.Z), 3.0)
    b = fl + rev([(16.0, -10.0), (40.0, -10.0), (42.0, -6.0), (42.0, 0.1), (16.0, 0.1)])   # spigot into the aperture
    b = b + rev([(R - 7.2, t - 0.1), (R + 1.0, t - 0.1), (R + 1.0, t + 4.0), (R - 5.3, t + 4.0), (R - 5.3, Z_YOKE[0] + 1.5),
                 (R - 7.2, Z_YOKE[0] + 1.5)])
    b = b + rev([(9.0, -5.0), (15.0, -5.0), (15.0, t + 9.0), (9.0, t + 9.0)])          # bush boss (item 20)
    for k in range(4):                                                                # ribs on the front of the flange
        a = 90.0 * k
        b = b + (Rot(0, 0, a) * box(16.0, R - 9.0, -2.0, 2.0, t - 0.1, t + 8.0))
    for y, z in _plate_screws():                                                      # reliefs for the rear plate's screw heads
        x_, y_ = E.starter_local(y, z)
        if math.hypot(x_, y_) < R + 25.0:
            b = b - zc(10.0, -1.0, t + 1.0, x_, y_)
    b = b - rev([(17.0, -11.0), (38.0, -11.0), (38.0, -4.0), (R - 7.0, 0.5), (R - 7.0, t - 3.0), (17.0, t - 3.0)])
    b = b - zc(6.4, -20, t + 20)
    for x, y in BOLTS_L:
        b = b - zc(5.0, -1, t + 1, x, y) - zc(9.5, t - 0.01, t + 12.0, x, y)      # spot faces for the bolt heads
    for a in TB_ANG:
        x, y = polar(TB_R, a)
        b = b - zc(2.6, t - 1, t + 14, x, y)
    return label(b, spec)


def yoke(spec) -> Part:
    """Yoke with the four pole shoes inside: pole screws countersunk round the middle, the
    brush windows at the commutator end under the cover band, and the terminal post boss."""
    z0, z1 = Z_YOKE
    y = Sh.tube(2 * R, 2 * (R - 5.0), z1 - z0, z0)
    zm = z0 + 0.42 * (z1 - z0)
    for k in range(4):                                                                # pole screw heads
        a = 45.0 + 90.0 * k
        x, yy = polar(R, a)
        y = y - (Location((x, yy, zm)) * Rot(0, 0, a) * Rot(0, 90, 0) * Sh.revolved([(0, -2.0), (6.5, -0.01), (6.5, 1.0), (0, 1.0)]))
        y = y + (Location((x * 0.99, yy * 0.99, zm)) * Rot(0, 0, a) * Rot(0, 90, 0) * zc(4.0, -1.6, 0.0))
    for k in range(4):                                                                # brush windows
        a = 90.0 * k
        y = y - (Rot(0, 0, a) * box(R - 8.0, R + 2.0, -14.0, 14.0, z1 - 28.0, z1 - 4.0))
    ux, uy = _term_dir()
    tz = E.TERMINAL_Z
    boss = Location((ux * (R - 2.0), uy * (R - 2.0), tz)) * Plane(origin=(0, 0, 0), z_dir=(ux, uy, 0)).location * zc(9.0, 0.0, 5.0)
    y = y + boss
    y = y - (Plane(origin=(ux * (R - 8.0), uy * (R - 8.0), tz), z_dir=(ux, uy, 0)).location * zc(4.2, 0, 30))
    for zz in (z0 + 3.0, z1 - 1.5):                                                  # rolled edges
        y = y + Sh.tube(2 * R + 1.2, 2 * R - 1.0, 1.5, zz - 0.75)
    return label(y, spec)


def cover_band(spec) -> Part:
    """Item 31: cover band over the brush windows, clamped by a screw through its lugs."""
    w = spec.nom("width")
    z1 = Z_YOKE[1] - 3.0
    z0 = z1 - w
    b = Sh.tube(2 * R + 2.4, 2 * R + 0.2, w, z0)
    a = 200.0
    lug = Rot(0, 0, a) * (box(R, R + 10.0, -6.0, -1.0, z0 + 6.0, z1 - 6.0) + box(R, R + 10.0, 1.0, 6.0, z0 + 6.0, z1 - 6.0))
    b = b - (Rot(0, 0, a) * box(R - 1.0, R + 3.0, -1.0, 1.0, z0 - 1, z1 + 1)) + lug
    b = b + (Rot(0, 0, a) * Location((R + 6.0, 0, (z0 + z1) / 2)) * Rot(90, 0, 0) * (zc(2.0, -12.0, 12.0) + zc(3.4, 6.0, 9.0)))
    return label(b, spec)


def commutator_end_bracket(spec) -> Part:
    """Item 21: commutator end bracket, a shallow dished cap on the yoke with the bush boss
    (22) and the shaft cap (23); the two through-bolt bosses."""
    z0 = Z_YOKE[1]
    c = rev([(0, z0 - 4.0), (R - 5.3, z0 - 4.0), (R - 5.3, z0), (R + 0.5, z0), (R + 0.5, z0 + 5.0), (R - 8.0, z0 + 11.0),
             (16.0, z0 + 14.0), (0, z0 + 14.0)])
    c = c - rev([(0, z0 - 5.0), (R - 8.0, z0 - 5.0), (R - 8.0, z0 + 2.0), (16.0, z0 + 10.0), (0, z0 + 10.0)])
    c = c - zc(6.5, z0, z0 + 15.0)
    for a in TB_ANG:
        x, y = polar(TB_R, a)
        c = c + zc(6.0, z0 + 6.0, z0 + 11.5, x, y)
        c = c - zc(2.7, z0 - 5.0, z0 + 13.0, x, y)
    for k in range(6):                                                                 # stiffening ribs
        a = 30.0 + 60.0 * k
        if min(abs(a - TB_ANG[0]), abs(a - TB_ANG[1])) < 12:
            continue
        c = c + (Rot(0, 0, a) * Location((R * 0.55, 0, z0 + 11.0)) * Rot(0, -9.0, 0) * Box(R * 0.75, 3.0, 4.0))
    return label(c, spec)


def shaft_cap(spec) -> Part:
    """Item 23: the shaft cap over the square end of the armature shaft (Sec 24 para 2: turn it
    with a spanner on the square to free a jammed motor)."""
    z0 = Z_YOKE[1] + 14.05
    c = rev([(0, z0), (14.0, z0), (14.0, z0 + 3.0), (11.0, Z_END), (0, Z_END)])
    return label(c, spec)


def through_bolt(spec) -> Part:
    """Item 26: through-bolt from the commutator end into the drive end bracket."""
    x, y = polar(TB_R, 0.0)
    z1 = Z_YOKE[1] + 11.5
    b = zc(2.4, Z_FL, z1, x, y) + zc(4.2, z1, z1 + 3.5, x, y)
    b = b - (Location((x, y, z1 + 3.0)) * Box(1.2, 7.0, 2.0))
    return label(b, spec)


def armature(spec) -> Part:
    """Item 30: armature and shaft. The core and commutator inside the yoke, the shaft through
    the drive end bush, with the Woodruff key seat (18) and the screwed-sleeve spline."""
    s = zc(spec.nom("shaft_diameter") / 2, E.SHAFT_END_X - XF0, Z_YOKE[1] + 12.0)
    s = s + zc(R - 14.0, Z_YOKE[0] + 6.0, Z_YOKE[1] - 34.0)                             # core
    for k in range(16):                                                               # winding slots
        s = s - (Rot(0, 0, 22.5 * k) * box(R - 21.0, R - 13.0, -1.6, 1.6, Z_YOKE[0] + 5.0, Z_YOKE[1] - 33.0))
    s = s + zc(22.0, Z_YOKE[1] - 30.0, Z_YOKE[1] - 6.0)                               # commutator
    for k in range(24):
        s = s - (Rot(0, 0, 15.0 * k) * box(20.5, 23.0, -0.4, 0.4, Z_YOKE[1] - 29.0, Z_YOKE[1] - 7.0))
    return label(s, spec)


def _gear_profile(n, dp_mm_module, z0, z1):
    m = dp_mm_module
    rp = n * m / 2
    ra, rf = rp + m, rp - 1.25 * m
    pts = []
    for k in range(n):
        a0 = 360.0 * k / n
        for da, r in ((-0.5, rf), (-0.28, rf), (-0.14, ra), (0.14, ra), (0.28, rf), (0.5, rf)):
            pts.append(polar(r, a0 + da * 360.0 / n))
    return X.poly_xy(pts, z0, z1)


def pinion(spec) -> Part:
    """Item 17: pinion and barrel. Nine teeth (13.3 : 1 on the 120-tooth ring, p162), the
    barrel behind them carrying the anti-drift spring and the control nut."""
    z0, z1 = E.PINION_REST_X[0] - XF0, E.PINION_REST_X[1] - XF0
    n = int(spec.nom("teeth"))
    m = 25.4 / E.DP
    g = _gear_profile(n, m, z0, z1 - 4.0)
    g = tryfillet(g, g.edges().group_by(Axis.Z)[0], 0.8)
    g = g + zc(12.5, z1 - 4.0, z1)
    g = g - zc(7.6, z0 - 1, z1 + 1)
    return label(g, spec)


def drive_sleeve(spec) -> Part:
    """Items 5, 8, 9, 13, 14, 3, 2: the screwed sleeve inside the pinion, the drive head sleeve,
    the rear and front anchor plates either side of the main spring, and the circlip."""
    z_end = E.SHAFT_END_X - XF0
    zp = E.PINION_REST_X[0] - XF0
    s = zc(7.5, zp - 4.0, E.PINION_REST_X[1] - XF0 - 0.5)                            # screwed sleeve (multi-start thread)
    for k in range(6):
        zz = zp + 1.0 + 3.0 * k
        s = s - Sh.tube(17.0, 14.0, 1.2, zz)
    s = s + zc(9.0, z_end + 6.0, zp - 4.0)                                          # drive head sleeve
    s = s + zc(17.0, X_SPRING[1] - 2.5, X_SPRING[1])                                # rear anchor plate (behind the ring)
    s = s + zc(17.0, X_SPRING[0], X_SPRING[0] + 2.5)                                # front anchor plate
    s = s + Sh.tube(17.0, 12.0, 1.6, X_SPRING[0] - 2.0)                             # circlip
    s = s - zc(6.2, z_end - 1, 5.0)
    return label(s, spec)


def main_spring(spec) -> Part:
    """Item 4: the main (buffer) spring between the anchor plates."""
    z0, z1 = X_SPRING[0] + 2.5, X_SPRING[1] - 2.5
    s = Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), z1 - z0, 3.5)
    return label(s.moved(Location((0, 0, z0))), spec)


def terminal_post(spec) -> Part:
    """Items 24 and 25: the field terminal post through the yoke, insulating bushes and the
    nuts and washers that clamp the starter cable eye."""
    ux, uy = _term_dir()
    pl = Plane(origin=(ux * R, uy * R, E.TERMINAL_Z), z_dir=(ux, uy, 0)).location
    nut = F.NUT["5/16"][0] * 25.4 / math.sqrt(3)
    t = zc(3.97, -8.0, E.TERMINAL_STACK + 10.0) + zc(8.0, 3.05, 9.0)                 # stud and insulator on the boss
    t = t + extrude(Plane.XY.offset(9.0) * RegularPolygon(nut, 6), 6.0)
    t = t + Sh.washer(17.0, 8.2, 1.6).moved(Location((0, 0, 15.0)))
    t = t + extrude(Plane.XY.offset(E.TERMINAL_STACK + 1.6) * RegularPolygon(nut, 6), 6.0)
    return label(pl * t, spec)


def mounting_bolt(spec) -> Part:
    return label(F.hex_bolt("3/8", 1.0), spec)


def spring_washer(spec) -> Part:
    i, o, t = spec.nom("inside_diameter"), spec.nom("outside_diameter"), spec.nom("thickness")
    w = Sh.washer(o, i, t) - Location((o / 2 - (o - i) / 4, 0, t / 2)) * Box((o - i) / 2 + 1, 0.8, t + 1)
    return label(w, spec)


# ---- solenoid and cables (car frame) ---------------------------------------------------------------
SX, SY, SZ = BL.SOLENOID
SOL_R = E.SOL_R
SOL_C = E.SOL_C
sol_terminal = E.sol_terminal


def solenoid(spec) -> Part:
    """Remote starter solenoid (Lucas ST950 pattern, early cars): a steel can on a mounting
    plate bolted to the inner wing, the moulded cap with the two main studs and the small
    switch terminal, and the rubber-covered manual push at the bottom."""
    cx, cy, cz = SOL_C
    h = E.SOL_LEN
    plate = box(cx - 40.0, cx + 40.0, SY, SY + 2.5, cz - 22.0, cz + 22.0)
    plate = tryfillet(plate, plate.edges().filter_by(Axis.Y), 6.0)
    for sx in (-30.0, 30.0):
        plate = plate - yc(3.3, SY - 1, SY + 4, cx + sx, cz)
    can = Location((cx, cy, cz - h / 2)) * (zc(SOL_R, 0.0, h) + Sh.tube(2 * SOL_R + 3.0, 2 * SOL_R - 1, 3.0, h - 3.0))
    strap = box(cx - SOL_R * 0.7, cx + SOL_R * 0.7, SY + 2.0, cy, cz - 10.0, cz + 10.0)
    cap = Location((cx, cy, cz + h / 2)) * rev([(0, 0), (SOL_R + 1.0, 0), (SOL_R + 1.0, 4.0), (SOL_R - 3.0, 12.0), (0, 12.0)])
    s = plate + can + strap + cap
    for w in (1, -1):                                        # main studs, 5/16 in, with nuts
        tx, ty, tz = sol_terminal(w)
        s = s + zc(4.0, cz + h / 2 + 10.0, tz, tx, ty) + zc(7.0, cz + h / 2 + 10.0, cz + h / 2 + 15.0, tx, ty)
        s = s + Location((tx, ty, tz - 9.0)) * extrude(RegularPolygon(7.3, 6), 5.5)
    s = s + zc(2.0, cz + h / 2 + 10.0, cz + h / 2 + 20.0, cx, cy + 15.0)            # switch terminal
    s = s + Location((cx, cy, cz - h / 2)) * rev([(0, -16.0), (8.0, -16.0), (11.0, -10.0), (11.0, 0.1), (0, 0.1)])
    return label(s, spec)


def _starter_cable_path():
    tx, ty, tz = sol_terminal(-1)
    sx, sy, sz = E.starter_terminal()
    ux, uy = _term_dir()
    # leave the stud upward, turn inboard and down past the chassis leg, onto the post from above
    n = (0.0, math.cos(math.radians(E.TERMINAL_ANGLE)), math.sin(math.radians(E.TERMINAL_ANGLE)))
    return [(tx - 16.0, ty, tz - 9.75), (tx - 34.0, ty + 6.0, tz - 9.75), (tx - 50.0, ty + 45.0, tz + 10.0), (sx + 80.0, -320.0, sz + 120.0),
            (sx + 60.0, sy + n[1] * 30.0, sz + n[2] * 30.0), (sx + 30.0, sy + n[1] * 1.6, sz + n[2] * 1.6),
            (sx + 13.0, sy + n[1] * 1.6, sz + n[2] * 1.6)]


def starter_cable(spec) -> Part:
    """Solenoid to starter cable (MGOC AHA6280): heavy PVC-covered cable with an eye at each
    end, the solenoid end under the stud nut, the starter end on the terminal post."""
    d = spec.nom("diameter")
    c = X.cable(_starter_cable_path(), d, 45.0)
    tx, ty, tz = sol_terminal(-1)
    c = c + Location((tx, ty, tz - 10.5)) * (zc(7.5, 0.0, 1.5) + box(-17.0, 0.0, -4.5, 4.5, 0.0, 1.5) - zc(4.1, -1, 3))
    sx, sy, sz = E.starter_terminal()
    ux, uy = _term_dir()
    pl = Plane(origin=(sx, sy, sz), z_dir=(0, math.cos(math.radians(E.TERMINAL_ANGLE)), math.sin(math.radians(E.TERMINAL_ANGLE))))
    c = c + pl.location * (zc(8.0, 0.0, 1.6) + box(4.0, 14.0, -5.0, 5.0, 0.0, 1.6) - zc(4.1, -1, 3))
    return label(c, spec)


def earth_strap(spec) -> Part:
    """Engine to body earth strap (MGOC 2K6167): braided copper strap with an eye under the
    starter's top mounting bolt head and one on the body (chassis leg) by the bulkhead."""
    (y0, z0) = E.starter_bolt_points()[0]
    x0 = XF0 + E.FLANGE_T
    w, t = spec.nom("width"), spec.nom("thickness")
    pts = [(x0 + 3.5, y0 - 14.0, z0 + 2.0), (x0 + 26.0, y0 - 20.0, z0 + 6.0), (x0 + 20.0, -300.0, z0 + 40.0), (BL.BULKHEAD_X + 70.0, -330.0, -300.0)]
    s = None
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        d = tuple((bb - aa) / L for aa, bb in zip(a, b))
        seg = Plane(origin=a, z_dir=d).location * Box(w, t, L, align=(X.BASE[0], X.BASE[1], X.BASE[2]))
        s = seg if s is None else s + seg
    s = s + Location((x0 + 0.05, y0, z0)) * Rot(0, 90, 0) * (zc(9.0, 0.0, 1.5) - zc(5.0, -1, 3))
    s = s + X.cable([(x0 + 0.8, y0 - 7.5, z0 + 1.0), (x0 + 3.5, y0 - 14.0, z0 + 2.0)], 3.0, 1.0)   # tab from the eye
    return label(s, spec)


PARTS = {
    "electrical.starting.drive-end-bracket": {"build": drive_end_bracket},
    "electrical.starting.yoke": {"build": yoke},
    "electrical.starting.cover-band": {"build": cover_band},
    "electrical.starting.commutator-end-bracket": {"build": commutator_end_bracket},
    "electrical.starting.shaft-cap": {"build": shaft_cap},
    "electrical.starting.through-bolt": {"build": through_bolt},
    "electrical.starting.armature": {"build": armature},
    "electrical.starting.pinion": {"build": pinion},
    "electrical.starting.drive-sleeve": {"build": drive_sleeve},
    "electrical.starting.main-spring": {"build": main_spring},
    "electrical.starting.terminal-post": {"build": terminal_post},
    "electrical.starting.mounting-bolt": {"build": mounting_bolt},
    "electrical.starting.spring-washer": {"build": spring_washer},
    "electrical.starting.solenoid": {"build": solenoid},
    "electrical.starting.starter-cable": {"build": starter_cable},
    "electrical.starting.earth-strap": {"build": earth_strap},
}
