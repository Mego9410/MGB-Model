"""Clutch hydraulics: master cylinder and reservoir with its internals and fixings, the RHD
metal pipe with its banjo and clips, the flexible hose at its bracket, and the slave
cylinder with its internals, pushrod, clevis pin, bleed screw and fixings.
Haynes Ch 5 Sec 3 (bleeding), Sec 5 (master cylinder), Sec 6 (slave cylinder) and Fig 5.3
(clutch control gear, printed p109), items 8-19, 24, 26-44, 47 and 49.

Cylinders are built in their own frames (z forward along the car from the mounting face,
x up, y to the car's right) and placed by the assembly from mgb.clutch_layout (master
cylinder on the pedal box) and mgb.gearbox_layout (slave cylinder on the bellhousing pad).
Pipe, clips and hose are built in the engine frame between those two frames.

Forms from Fig 5.3:
- master cylinder (item 8): cast body with a two-bolt flange, the cylinder running forward
  to a boss for the banjo bolt, and the round reservoir standing on it next to the flange
  with its fluted cap (9) and seal (10); the rubber boot (11) over the rear end.
- slave cylinder (item 36): cast body with a domed closed end, the hose union boss and the
  bleed screw boss near that end, a two-ear flange at the open end, and the rubber boot (42)
  with its two clips (41, 43) on the pushrod (44).
"""
import math

from build123d import Align, Box, Cylinder, FilletPolyline, Location, Part, Plane, Polygon, Rot, Sphere, Torus, \
    extrude, sweep, Circle

from mgb import clutch_layout as K, fasteners as F, gearbox_layout as G, probes, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)

# ---- master cylinder frame (local z forward from the pedal box face, x up, y right) --------------
MC_LEN = 128.0               # flange face to the front of the cylinder casting
MC_FLANGE_T = 7.0
MC_BOLT_X = 27.0             # flange bolts above and below the axis
MC_RES_Z, MC_RES_R, MC_RES_TOP = 34.0, 21.0, 60.0     # reservoir centre, radius, top of the casting
MC_NECK_TOP = MC_RES_TOP + 7.0
MC_SPIGOT = 12.0             # rear spigot behind the flange, into the pedal box
BANJO_X0 = MC_LEN + 8.0      # banjo seat on the front boss
BANJO_T = 10.0
WASHER_T = 1.6
STUB_DIR = (-math.sqrt(0.5), math.sqrt(0.5), 0.0)    # banjo pipe stub: down and to the right (local)
CLEVIS_Z = K.PEDAL_CLEVIS[0] - K.PEDAL_BOX_FACE_X   # pedal clevis pin, local z (negative: behind)

# ---- slave cylinder frame (local z forward from the pad face, x up, y right) ----------------------
SL_FLANGE_T = 7.0
SL_LEN = 66.0                # pad face to the start of the domed end
SL_UNION_Z, SL_BLEED_Z = 50.0, 58.0
SL_UNION_DIR = (0.75, math.sqrt(1 - 0.75 ** 2))                # up and outboard (local x, y)
SL_EYE_Z = G.LEVER_END[0] - G.SLAVE_PAD_X           # pushrod eye at the lever end (negative)


def _l(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def radial(dx, dy, r0, r1, z, rad):
    """Cylinder of radius rad along the local direction (dx, dy, 0) from r0 to r1, at depth z."""
    a = math.degrees(math.atan2(dy, dx))
    return Location((0, 0, z)) * Rot(0, 0, a) * Location(((r0 + r1) / 2, 0, 0)) * Cylinder(rad, r1 - r0, rotation=(0, 90, 0))


def _rod(points, r, radius):
    path = None
    for rr in (radius, radius * 0.5, radius * 0.25, radius * 0.1):
        try:
            path = FilletPolyline(*points, radius=rr)
            break
        except ValueError:
            continue
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    return sweep(pl * Circle(r), path=path)


def _hex(af, h):
    return extrude(Polygon(*[(af / math.sqrt(3) * math.cos(math.radians(30 + 60 * k)),
                              af / math.sqrt(3) * math.sin(math.radians(30 + 60 * k))) for k in range(6)], align=None),
                   h, dir=(0, 0, 1))


def mc_frame():
    return Plane(origin=(K.PEDAL_BOX_FACE_X, K.MC_Y, K.MC_Z), x_dir=(0, 0, 1), z_dir=(1, 0, 0)).location


def slave_frame():
    return Plane(origin=(G.SLAVE_PAD_X, G.SLAVE_Y, G.SLAVE_Z), x_dir=(0, 0, 1), z_dir=(1, 0, 0)).location


def mc_point(x, y, z):
    return tuple((mc_frame() * Location((x, y, z))).position)


def slave_point(x, y, z):
    return tuple((slave_frame() * Location((x, y, z))).position)


# ---- master cylinder (Fig 5.3 items 8-19) -------------------------------------------------------
def mc_body(spec) -> Part:
    bore = spec.nom("bore") / 2
    r = 15.5
    b = zc(r, -MC_SPIGOT, MC_LEN) + zc(10.5, MC_LEN - 1, BANJO_X0)
    b = b + Sh.revolved([(0, MC_LEN - 2), (r, MC_LEN - 2), (r - 3.0, MC_LEN + 1.0), (0, MC_LEN + 1.0)])
    # two-bolt flange, a lozenge with bosses round the holes
    fl = extrude(Polygon((-MC_BOLT_X - 9, -9), (-MC_BOLT_X - 9, 9), (-12, 19), (12, 19), (MC_BOLT_X + 9, 9),
                         (MC_BOLT_X + 9, -9), (12, -19), (-12, -19), align=None), MC_FLANGE_T, dir=(0, 0, 1))
    for s in (-1, 1):
        fl = fl + zc(9.0, 0, MC_FLANGE_T, s * MC_BOLT_X)
    b = b + fl
    # reservoir standing on the cylinder by the flange, with the filler neck
    res = Location((0, 0, MC_RES_Z)) * Rot(0, 90, 0) * Cylinder(MC_RES_R, MC_RES_TOP, align=BASE)
    b = b + res
    b = b + Location((MC_RES_TOP, 0, MC_RES_Z)) * Rot(0, 90, 0) * Cylinder(15.5, MC_NECK_TOP - MC_RES_TOP, align=BASE)
    for k in range(4):                                               # thread on the neck
        b = b + Location((MC_RES_TOP + 1.2 + 1.5 * k, 0, MC_RES_Z)) * Rot(0, 90, 0) * \
            Sh.revolved([(15.4, 0), (16.1, 0.35), (15.4, 0.7)])
    b = b + Location((0, 0, MC_RES_Z - MC_RES_R)) * Box(14, 8, MC_RES_R)                      # web to the flange
    b = b + Location((-r + 1.0, 0, (MC_FLANGE_T + MC_LEN) / 2)) * Box(6.0, 6.0, MC_LEN - MC_FLANGE_T - 4)   # keel rib
    # hollows: bore, reservoir well, feed and by-pass ports, outlet
    b = b - zc(bore, -MC_SPIGOT - 1, MC_LEN - 6)
    b = b - zc(12.8, -MC_SPIGOT - 1, -MC_SPIGOT + 4)                  # circlip recess at the mouth
    b = b - Location((14.0, 0, MC_RES_Z)) * Rot(0, 90, 0) * Cylinder(MC_RES_R - 2.5, MC_RES_TOP - 3.0 - 14.0, align=BASE)
    b = b - Location((50.0, 0, MC_RES_Z)) * Rot(0, 90, 0) * Cylinder(12.5, MC_NECK_TOP - 50.0 + 1.0, align=BASE)
    b = b - Location((bore, 0, MC_RES_Z - 4)) * Rot(0, 90, 0) * Cylinder(1.6, 16, align=BASE)
    b = b - Location((bore, 0, MC_RES_Z + 6)) * Rot(0, 90, 0) * Cylinder(0.6, 16, align=BASE)
    b = b - zc(4.9, MC_LEN - 7, BANJO_X0 + 1)
    for s in (-1, 1):
        b = b - zc(4.2, -1, MC_FLANGE_T + 1, s * MC_BOLT_X)
    return _l(b, spec)


def mc_cap(spec) -> Part:
    """Item 9: fluted filler cap with its breather hole."""
    z0 = MC_NECK_TOP + 1.5
    c = Sh.revolved([(0, 0), (19.0, 0), (19.0, 4.0), (17.5, 5.5), (5.0, 6.5), (0, 6.5)]) + ring(16.4, 19.0, -7.8, 0.1)
    for k in range(18):
        a = 20.0 * k
        c = c - (Location((0, 0, -4.0)) * Rot(0, 0, a) * Location((19.6, 0, 0)) * Box(2.0, 2.2, 15.0))
    c = c - zc(0.8, -1, 8, 6.0, 0)
    return _l(Location((z0, 0, MC_RES_Z)) * Rot(0, 90, 0) * c, spec)


def mc_seal(spec) -> Part:
    """Item 10: rubber seal under the cap."""
    t = spec.nom("thickness")
    return _l(Location((MC_NECK_TOP, 0, MC_RES_Z)) * Rot(0, 90, 0) * Sh.washer(32.6, 18.0, t), spec)


def mc_boot(spec) -> Part:
    """Item 11: rubber boot over the mouth, gripping the pushrod."""
    z0 = -MC_SPIGOT
    o = Sh.revolved([(15.6, z0 + 5), (17.4, z0 + 5), (17.4, z0 - 2), (14.0, z0 - 5), (15.0, z0 - 8), (6.4, z0 - 11.5),
                     (6.0, z0 - 13.5), (4.1, z0 - 13.5), (4.1, z0 - 11.5), (12.6, z0 - 7.5), (12.0, z0 - 5), (15.6, z0 - 1.5)])
    return _l(o, spec)


def mc_circlip(spec) -> Part:
    z = -MC_SPIGOT + 1.5
    c = ring(9.0, 12.8, z, z + 1.2) - Location((0, -11.0, z)) * Box(4.0, 5.0, 4.0)
    for s in (-1, 1):
        c = c + zc(1.9, z, z + 1.2, s * 3.4, -9.6) - zc(0.6, z - 1, z + 2, s * 3.4, -9.6)
    return _l(c, spec)


def mc_pushrod(spec) -> Part:
    """Item 13: pushrod with its stop washer, threaded into a clevis fork with a locknut."""
    zc_ = CLEVIS_Z
    p = zc(4.0, zc_ + 14, -2.0) + Sh.revolved([(0, -2.0), (4.0, -2.0), (4.2, -1.0), (3.0, 0.3), (0, 0.8)])
    p = p + zc(8.6, -MC_SPIGOT + 2.8, -MC_SPIGOT + 4.2)              # stop washer under the circlip
    fork = Location((0, 0, zc_ + 6)) * Box(16.0, 18.0, 20.0)
    fork = fork - Location((0, 0, zc_ + 2)) * Box(20.0, 8.6, 20.0)     # slot for the pedal
    fork = fork - Location((0, 0, zc_)) * Rot(90, 0, 0) * Cylinder(4.1, 30)
    p = p + fork + Location((0, 0, zc_ + 15)) * _hex(12.7, 6.0).moved(Location((0, 0, -3)))   # locknut
    return _l(p, spec)


def mc_piston(spec) -> Part:
    """Item 15: piston with the groove for the secondary cup and the bleed holes in its head."""
    b = spec.nom("diameter") / 2
    p = Sh.revolved([(0, -4.0), (b - 0.2, -4.0), (b - 0.2, 2.0), (b - 2.5, 3.0), (b - 2.5, 9.0), (b - 0.2, 10.0),
                     (b - 0.2, 20.0), (b - 1.6, 21.0), (b - 1.6, 26.0), (0, 26.0)])
    p = p - Sh.revolved([(0, -5), (5.5, -5), (4.0, 0.5), (0, 1.0)])     # dish for the pushrod
    for k in range(6):
        a = math.radians(60 * k)
        p = p - zc(0.8, 18, 27, 6.5 * math.cos(a), 6.5 * math.sin(a))
    return _l(p, spec)


def mc_secondary_cup(spec) -> Part:
    b = 9.5
    return _l(Sh.revolved([(b - 2.45, 3.0), (b, 3.0), (b, 3.6), (b - 0.6, 5.0), (b, 8.4), (b, 9.0),
                           (b - 2.45, 9.0)]), spec)


def mc_piston_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = ring(3.0, 9.2, 26.0, 26.0 + t)
    for k in range(6):
        a = math.radians(60 * k + 30)
        w = w + zc(1.4, 26.0 + t - 0.01, 26.0 + t + 0.4, 6.8 * math.cos(a), 6.8 * math.sin(a))
    return _l(w, spec)


def mc_main_cup(spec) -> Part:
    """Item 17: main cup, lip toward the outlet."""
    b, z0 = 9.4, 27.0
    c = Sh.revolved([(0, z0), (b - 1.0, z0), (b, z0 + 1.0), (b, z0 + 7.0), (b - 1.6, z0 + 7.0), (b - 1.8, z0 + 3.5),
                     (4.0, z0 + 3.5), (4.0, z0 + 5.0), (0, z0 + 5.0)])
    return _l(c, spec)


def mc_spring_retainer(spec) -> Part:
    z0 = 34.2
    r = ring(6.0, 8.6, z0, z0 + 0.8) + ring(5.0, 6.0, z0, z0 + 5.0) + Sh.revolved([(0, z0 + 0.0), (2.0, z0), (2.0, z0 + 1.5), (0, z0 + 1.5)])
    for k in range(3):
        r = r - (Location((0, 0, z0 + 3.0)) * Rot(0, 0, 120 * k) * Location((5.5, 0, 0)) * Box(3.0, 1.2, 5.0))
    return _l(r, spec)


def mc_spring(spec) -> Part:
    """Item 19: tapered return spring, large end first into the bore (Sec 5 para 9)."""
    z0, z1 = 35.0, MC_LEN - 9.0
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), z1 - z0, 9).moved(Location((0, 0, z0))), spec)


def mc_bolt(length_key):
    def build(spec):
        b = F.hex_bolt("5/16", spec.nom("length") / 25.4)
        return _l(b, spec)
    return build


def mc_nut(spec):
    return _l(F.hex_nut("5/16"), spec)


def plain_washer(spec):
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def spring_washer(spec):
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) - Location(((od + id_) / 4, 0, t / 2)) * Rot(0, 0, 20) * Box(od, 1.2, t + 1)
    return _l(w, spec)


def stiffener(spec) -> Part:
    """Stiffener plate under the top bolt (Sec 5 para 11), built on its hole, face at z = 0."""
    t = spec.nom("thickness")
    p = extrude(Polygon((-8, -14), (-8, 14), (16, 18), (34, 12), (34, -12), (16, -18), align=None), t, dir=(0, 0, 1))
    p = p + Location((26, 0, -0.6)) * Box(14, 22, 1.2)               # pressed rib, on the face away from the box wall
    return _l(p - zc(4.2, -1, t + 3), spec)


# ---- banjo outlet and pipe (items 24, 30-35) ------------------------------------------------------
def banjo(spec) -> Part:
    """Item 32: banjo eye on the front boss with the pipe stub brazed in."""
    z0 = BANJO_X0 + WASHER_T
    e = zc(9.5, z0, z0 + BANJO_T) - zc(5.0, z0 - 1, z0 + BANJO_T + 1)
    e = e - ring(5.0, 6.3, z0 + 3.0, z0 + BANJO_T - 3.0)               # internal gallery
    e = e + radial(STUB_DIR[0], STUB_DIR[1], 8.0, 9.0 + 14.0, z0 + BANJO_T / 2, 3.2)
    return _l(e, spec)


def banjo_bolt(spec) -> Part:
    """Item 33: hollow banjo bolt with its cross-drilling."""
    L = spec.nom("length")
    z_head = BANJO_X0 + 2 * WASHER_T + BANJO_T
    b = F.hex_bolt("3/8", L / 25.4)
    b = Location((0, 0, z_head)) * Rot(180, 0, 0) * b
    b = b - zc(1.8, z_head - L - 1, z_head - 3)
    b = b - Location((0, 0, BANJO_X0 + WASHER_T + BANJO_T / 2)) * Cylinder(1.6, 14, rotation=(90, 0, 0))
    return _l(b, spec)


def sealing_washer(which):
    def build(spec):
        z0 = BANJO_X0 if which == "inner" else BANJO_X0 + WASHER_T + BANJO_T
        return _l(ring(5.0, 8.5, z0, z0 + WASHER_T), spec)
    return build


def _stub_end():
    z = BANJO_X0 + WASHER_T + BANJO_T / 2
    return mc_point(STUB_DIR[0] * 23.0, STUB_DIR[1] * 23.0, z)


BR_X, BR_Y, BR_Z = K.HOSE_BRACKET
BRACKET_T = 3.0
PIPE_NUT_TOP = BR_Z + BRACKET_T + 23.0          # top of the pipe's union nut in the hose end


def pipe_points():
    s = _stub_end()
    # QA fix round 1, steering: through the mounting wall into the box's rear section and down its open bottom
    # inboard of the steering column (y -250; the column passes under the box at y -287), then out to the bracket
    # below the column (D: clear of the column's outer tube by 15 mm).
    yc = K.MC_Y + 19.0                                   # inboard of the clutch arm (QA fix round 1, cockpit: box moved out)
    return [s, (s[0], s[1] - 6.0, s[2] - 6.0), (s[0] - 4.0, s[1] - 14.0, s[2] - 16.0), (BR_X + 40.0, yc, s[2] - 16.0),
            (K.PEDAL_BOX_FACE_X - 25.0, yc, s[2] - 24.0), (K.PEDAL_BOX_FACE_X - 25.0, yc, -80.0),
            (BR_X, BR_Y, PIPE_NUT_TOP + 16.0), (BR_X, BR_Y, PIPE_NUT_TOP - 2.0)]


def metal_pipe(spec) -> Part:
    """Item 24 (RHD): 3/16 in pipe from the banjo down the bulkhead to the hose bracket, ending
    in a union nut screwed into the hose end."""
    pts = pipe_points()
    p = _rod(pts, spec.nom("outside_diameter") / 2, 12.0)
    nut = Location((BR_X, BR_Y, PIPE_NUT_TOP - 10.0)) * _hex(11.1, 10.0)
    return _l(p + nut, spec)


def pipe_clip(spec) -> Part:
    """Items 30/31: P-clip round the pipe with a screw tab, built at the origin on the local
    z axis (the assembly lays it on the pipe)."""
    r = 2.4 + 0.3
    c = ring(r, r + 0.9, -4.0, 4.0) + Location((r + 6.0, 0, 0)) * Box(12.0, 1.8, 8.0)
    c = c - Location((r + 8.5, 0, 0)) * Rot(90, 0, 0) * Cylinder(2.0, 6)
    return _l(c, spec)


# ---- hose (items 26-29) -----------------------------------------------------------------------------
def _slave_union_axis():
    ux, uy = SL_UNION_DIR
    return ux, uy


def hose_points():
    ux, uy = _slave_union_axis()
    p_end = slave_point(ux * 31.0, uy * 31.0, SL_UNION_Z)            # top of the hose's hex at the union
    p_out = slave_point(ux * 64.0, uy * 64.0, SL_UNION_Z)
    top = (BR_X, BR_Y, BR_Z - 16.0)
    return [top, (BR_X, BR_Y, BR_Z - 32.0), (BR_X + 12.0, BR_Y + 4.0, BR_Z - 48.0), p_out, p_end]


def hose(spec) -> Part:
    """Item 26: flexible hose with its crimped end fittings: the top one through the bracket
    (hex below, thread up through it), the bottom one screwed into the slave cylinder."""
    pts = hose_points()
    h = _rod(pts[1:-1], spec.nom("outside_diameter") / 2, 18.0)
    # top end: ferrule, hex under the bracket, threaded neck up through it
    top = Location((BR_X, BR_Y, 0)) * (zc(6.0, BR_Z - 42.0, BR_Z - 17.0) + _hex(15.9, 15.0).moved(Location((0, 0, BR_Z - 17.0)))
                                         + zc(5.6, BR_Z - 2.0, PIPE_NUT_TOP - 10.0))
    top = top - Location((BR_X, BR_Y, 0)) * zc(2.5, PIPE_NUT_TOP - 30.0, PIPE_NUT_TOP)
    # bottom end: ferrule, hex and male thread into the union boss
    ux, uy = _slave_union_axis()
    a = math.degrees(math.atan2(uy, ux))
    bot = (zc(6.0, 31.0 + 2.0 + 13.0, 31.0 + 2.0 + 13.0 + 22.0) + _hex(14.3, 13.0).moved(Location((0, 0, 31.0 + 2.0)))
           + zc(4.8, 20.0, 31.0 + 2.0))
    bot = slave_frame() * Location((0, 0, SL_UNION_Z)) * Rot(0, 0, a) * Rot(0, 90, 0) * bot
    return _l(h + top + bot, spec)


def hose_locknut(spec) -> Part:
    """Item 27: locknut on the hose's top end, above the bracket."""
    z0 = BR_Z + BRACKET_T + 1.5
    return _l(Location((BR_X, BR_Y, z0)) * (_hex(15.9, 6.4) - zc(5.6, -1, 8)), spec)


def hose_lockwasher(spec) -> Part:
    """Item 28: shakeproof washer between the bracket and the locknut."""
    z0 = BR_Z + BRACKET_T
    w = ring(5.7, 9.5, z0, z0 + 1.5)
    for k in range(10):
        w = w - (Location((0, 0, z0 + 1.2)) * Rot(0, 0, 36 * k) * Location((8.5, 0, 0)) * Box(2.5, 1.0, 1.0))
    return _l(w.moved(Location((BR_X, BR_Y, 0))), spec)


def copper_washer(spec) -> Part:
    """Item 29: copper washer between the hose end and the slave cylinder union."""
    ux, uy = _slave_union_axis()
    a = math.degrees(math.atan2(uy, ux))
    w = Location((0, 0, 31.0)) * Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness"))
    return _l(slave_frame() * Location((0, 0, SL_UNION_Z)) * Rot(0, 0, a) * Rot(0, 90, 0) * w, spec)


# ---- slave cylinder (items 36-44, 47, 49) -----------------------------------------------------------
def slave_body(spec) -> Part:
    bore = spec.nom("bore") / 2
    r = 16.5
    z_rear = -SL_FLANGE_T
    b = zc(r, z_rear, SL_LEN) + Sh.revolved([(0, SL_LEN - 0.1), (r, SL_LEN - 0.1), (r - 3.0, SL_LEN + 5.0),
                                              (8.0, SL_LEN + 8.5), (0, SL_LEN + 9.0)])
    b = b + ring(r - 0.1, 18.5, z_rear - 4.0, z_rear)                  # lip the boot grips
    # two-ear flange on the open end
    dz = G.SLAVE_BOLT_DZ
    fl = extrude(Polygon((-dz - 8, -8), (-dz - 8, 8), (-10, 18), (10, 18), (dz + 8, 8), (dz + 8, -8), (10, -18),
                         (-10, -18), align=None), SL_FLANGE_T, dir=(0, 0, 1)).moved(Location((0, 0, z_rear)))
    for s in (-1, 1):
        fl = fl + zc(8.0, z_rear, 0.0, s * dz)
    b = b + fl
    # union boss (up and outboard) and bleed screw boss (on top), near the closed end
    ux, uy = SL_UNION_DIR
    b = b + radial(ux, uy, r - 4.0, 31.0, SL_UNION_Z, 7.5)
    b = b + radial(1.0, 0.0, r - 4.0, 25.0, SL_BLEED_Z, 6.5)
    b = b + Location((r + 1.0, 0, (SL_UNION_Z + SL_BLEED_Z) / 2)) * Box(6.0, 5.0, 20.0)   # web between the bosses
    # bore, ports, bolt holes
    b = b - zc(bore, z_rear - 5, SL_LEN - 2)
    b = b - radial(ux, uy, bore - 1, 32.0, SL_UNION_Z, 2.0) - radial(ux, uy, 19.0, 32.0, SL_UNION_Z, 4.9)
    b = b - radial(1.0, 0.0, bore - 1, 26.0, SL_BLEED_Z, 1.5) - radial(1.0, 0.0, 17.0, 26.0, SL_BLEED_Z, 3.5)
    for s in (-1, 1):
        b = b - zc(4.2, z_rear - 1, 1, s * dz)
    return _l(b, spec)


def slave_spring(spec) -> Part:
    """Item 37: piston return spring against the closed end."""
    z0, z1 = 16.0, SL_LEN - 2.0
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), z1 - z0, 7).moved(Location((0, 0, z0))), spec)


def slave_cup_filler(spec) -> Part:
    """Item 38: cup filler, the spring seat inside the cup."""
    z0 = 11.5
    f = Sh.revolved([(0, z0), (10.5, z0), (10.5, z0 + 1.0), (4.0, z0 + 1.0), (4.0, z0 + 5.0), (0, z0 + 5.0)])
    return _l(f, spec)


def slave_cup(spec) -> Part:
    """Item 39: piston cup, fitted lip first (Sec 6 para 4)."""
    b, z0 = 12.6, 4.5
    c = Sh.revolved([(0, z0), (b - 0.8, z0), (b, z0 + 0.8), (b, z0 + 7.0), (b - 1.5, z0 + 7.0), (b - 1.8, z0 + 3.0),
                     (0, z0 + 3.0)])
    return _l(c, spec)


def slave_piston(spec) -> Part:
    """Item 40: piston, its rear recessed for the pushrod."""
    b = spec.nom("diameter") / 2
    p = Sh.revolved([(0, -9.0), (b - 1.0, -9.0), (b - 0.2, -8.0), (b - 0.2, 3.5), (b - 1.0, 4.5), (0, 4.5)])
    p = p - Sh.revolved([(0, -10.0), (5.0, -10.0), (3.0, -2.0), (0, -1.5)])
    p = p - ring(b - 1.2, b, -5.0, -3.5)
    return _l(p, spec)


def slave_boot(spec) -> Part:
    """Item 42: rubber boot from the cylinder's lip to the pushrod."""
    z0 = -SL_FLANGE_T
    o = Sh.revolved([(18.6, z0 - 0.2), (19.6, z0 - 0.2), (19.6, z0 - 5.0), (17.0, z0 - 8.0), (18.5, z0 - 11.0),
                     (9.0, z0 - 19.0), (6.0, z0 - 22.0), (6.0, z0 - 27.0), (4.1, z0 - 27.0), (4.1, z0 - 22.0),
                     (15.5, z0 - 10.0), (15.0, z0 - 4.3), (18.6, z0 - 4.3)])
    return _l(o, spec)


def boot_clip(which):
    def build(spec):
        if which == "large":
            z0 = -SL_FLANGE_T - 4.5
            c = ring(19.6, 20.6, z0, z0 + 3.5) + Location((0, 20.6 + 2.0, z0 + 1.75)) * Box(4.0, 4.0, 3.5)
        else:
            z0 = -SL_FLANGE_T - 26.0
            c = ring(6.0, 7.0, z0, z0 + 3.0) + Location((0, 7.0 + 1.5, z0 + 1.5)) * Box(3.0, 3.0, 3.0)
        return _l(c, spec)
    return build


def slave_pushrod(spec) -> Part:
    """Item 44: pushrod from the piston to the lever, its flat eye between the lever's fork."""
    ze = SL_EYE_Z
    p = Sh.revolved([(0, -3.2), (2.4, -3.6), (3.4, -5.2), (3.6, -8.0), (4.0, -8.5), (4.0, ze + 9.0), (0, ze + 9.0)])
    eye = Location((0, 0, ze)) * (Cylinder(9.0, 8.4, rotation=(0, 90, 0)) + Location((0, 0, 5.0)) * Box(8.4, 8.0, 10.0))
    eye = eye - Location((0, 0, ze)) * Cylinder(4.1, 20, rotation=(0, 90, 0))
    return _l(p + eye, spec)


def slave_clevis_pin(spec) -> Part:
    """Item 47: clevis pin through the lever fork and pushrod eye, with its split pin hole."""
    L = spec.nom("length")
    p = Sh.revolved([(0, -L / 2), (3.95, -L / 2), (3.95, L / 2), (6.5, L / 2), (6.5, L / 2 + 2.5), (0, L / 2 + 2.5)])
    p = p - Location((0, 0, -L / 2 + 2.5)) * Cylinder(0.9, 12, rotation=(90, 0, 0))
    return _l(Location((0, 0, SL_EYE_Z)) * Rot(0, 90, 0) * p, spec)


def bleed_screw(spec) -> Part:
    """Item 49: bleed screw: thread, hex and the nipple the bleed tube fits over (Sec 3)."""
    s = zc(3.4, 17.0, 26.0) + _hex(7.9, 5.5).moved(Location((0, 0, 26.0))) + zc(2.6, 31.5, 39.0)
    s = s + Sh.revolved([(1.0, 33.0), (3.1, 33.0), (2.6, 35.0), (1.0, 35.0)])
    s = s - zc(0.9, 16, 40)
    return _l(Location((0, 0, SL_BLEED_Z)) * Rot(0, 90, 0) * s, spec)


def bleed_cap(spec) -> Part:
    """Rubber dust cap on the bleed nipple (Sec 3 para 3)."""
    c = zc(4.6, 33.5, 42.0) - zc(3.25, 33.0, 40.5)
    c = c + Sh.revolved([(0, 42.0), (4.4, 42.0), (3.0, 43.5), (0, 43.8)])
    return _l(Location((0, 0, SL_BLEED_Z)) * Rot(0, 90, 0) * c, spec)


def slave_bolt(spec):
    return _l(F.hex_bolt("5/16", spec.nom("length") / 25.4), spec)


PARTS = {
    "clutch.hydraulics.mc-body": {"build": mc_body, "probes": {"bore": lambda p: min(d for d, _ in probes.cylinder_diameters(p) if 18 < d < 20)}},
    "clutch.hydraulics.mc-cap": {"build": mc_cap},
    "clutch.hydraulics.mc-seal": {"build": mc_seal},
    "clutch.hydraulics.mc-boot": {"build": mc_boot},
    "clutch.hydraulics.mc-circlip": {"build": mc_circlip},
    "clutch.hydraulics.mc-pushrod": {"build": mc_pushrod},
    "clutch.hydraulics.mc-secondary-cup": {"build": mc_secondary_cup},
    "clutch.hydraulics.mc-piston": {"build": mc_piston},
    "clutch.hydraulics.mc-piston-washer": {"build": mc_piston_washer},
    "clutch.hydraulics.mc-main-cup": {"build": mc_main_cup},
    "clutch.hydraulics.mc-spring-retainer": {"build": mc_spring_retainer},
    "clutch.hydraulics.mc-spring": {"build": mc_spring},
    "clutch.hydraulics.mc-bolt-long": {"build": mc_bolt("long")},
    "clutch.hydraulics.mc-bolt": {"build": mc_bolt("short")},
    "clutch.hydraulics.mc-nut": {"build": mc_nut},
    "clutch.hydraulics.mc-washer": {"build": plain_washer},
    "clutch.hydraulics.mc-stiffener": {"build": stiffener},
    "clutch.hydraulics.banjo": {"build": banjo},
    "clutch.hydraulics.banjo-bolt": {"build": banjo_bolt},
    "clutch.hydraulics.sealing-washer-inner": {"build": sealing_washer("inner")},
    "clutch.hydraulics.sealing-washer-outer": {"build": sealing_washer("outer")},
    "clutch.hydraulics.metal-pipe": {"build": metal_pipe},
    "clutch.hydraulics.pipe-clip": {"build": pipe_clip},
    "clutch.hydraulics.hose": {"build": hose},
    "clutch.hydraulics.hose-locknut": {"build": hose_locknut},
    "clutch.hydraulics.hose-lockwasher": {"build": hose_lockwasher},
    "clutch.hydraulics.copper-washer": {"build": copper_washer},
    "clutch.hydraulics.slave-body": {"build": slave_body, "probes": {"bore": lambda p: min(d for d, _ in probes.cylinder_diameters(p) if 24 < d < 27)}},
    "clutch.hydraulics.slave-spring": {"build": slave_spring},
    "clutch.hydraulics.slave-cup-filler": {"build": slave_cup_filler},
    "clutch.hydraulics.slave-cup": {"build": slave_cup},
    "clutch.hydraulics.slave-piston": {"build": slave_piston},
    "clutch.hydraulics.slave-boot": {"build": slave_boot},
    "clutch.hydraulics.boot-clip-small": {"build": boot_clip("small")},
    "clutch.hydraulics.boot-clip-large": {"build": boot_clip("large")},
    "clutch.hydraulics.slave-pushrod": {"build": slave_pushrod},
    "clutch.hydraulics.slave-clevis-pin": {"build": slave_clevis_pin},
    "clutch.hydraulics.bleed-screw": {"build": bleed_screw},
    "clutch.hydraulics.bleed-cap": {"build": bleed_cap},
    "clutch.hydraulics.slave-bolt": {"build": slave_bolt, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "clutch.hydraulics.slave-spring-washer": {"build": spring_washer},
}
