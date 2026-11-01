"""Twin SU HS4 carburettors, heat shield, distance pieces, linkage and air cleaners.
Haynes Ch 3, Figs 3.1, 3.10, 3.11, 3.12; photos 17.1(a)/(b), 17.7, 18.2-18.5.

Handed parts (bodies, float chambers, jet assemblies) are built in the engine frame at
their instrument; round parts on the piston axis are built about Z at the origin and
placed by the assembly.
"""
import math

from build123d import (Align, Axis, Box, Circle, Cylinder, FilletPolyline, Location, Part, Plane, Rot,
                       SlotCenterToCenter, extrude, fillet, sweep)

from mgb import carb_layout as K, fasteners as F, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def _l(p, spec):
    p.label = spec.id
    return p


def _tf(p, edges, r):
    try:
        return fillet(edges, r)
    except Exception:  # noqa: BLE001
        return p


def _ycyl(r, x, z, y0, y1):
    return Cylinder(r, y1 - y0, rotation=(-90, 0, 0)).moved(Location((x, (y0 + y1) / 2, z)))


def _xcyl(r, y, z, x0, x1):
    return Cylinder(r, abs(x1 - x0), rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _zcyl(r, x, y, z0, z1):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def _yslot(x, z, length, height, y0, t):
    pl = Plane(origin=(x, y0, z), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    return extrude(pl * SlotCenterToCenter(max(length - height, 0.01), height), t)


def _rod(points, r, radius=10.0):
    for rr in (radius, radius * 0.5, radius * 0.25):
        try:
            path = FilletPolyline(*points, radius=rr)
            break
        except ValueError:
            continue
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    try:
        return sweep(pl * Circle(r), path=path)
    except Exception:  # noqa: BLE001 - fall back to straight pieces with ball joints
        from build123d import Sphere, Vector
        out = None
        for a, b in zip(points, points[1:]):
            va, vb = Vector(*a), Vector(*b)
            seg = Plane(origin=a, z_dir=(vb - va).normalized()).location * Cylinder(r, (vb - va).length, align=BASE)
            seg = seg + Sphere(r).moved(Location(b))
            out = seg if out is None else out + seg
        return out


# ---- carburettor body (Fig 3.10 items 1 and 2; Fig 3.12) --------------------------------------
def body(x):
    def build(spec) -> Part:
        s = K.side(x)
        y0, z = K.BODY_Y, K.AXIS_Z
        bore = spec.nom("choke_diameter") / 2
        b = _yslot(x, z, 78, 52, y0, 9)                                      # engine flange
        b = b + _ycyl(bore + 7, x, z, y0, y0 + K.BODY_LEN)                    # barrel
        b = b + _yslot(x, z, 70, 58, y0 + K.BODY_LEN - 7, 7)                  # air intake flange
        tower = _zcyl(40, x, K.PISTON_Y, z + 4, K.CHAMBER_BASE_Z - 4)            # round body under the dashpot
        b = b + tower + _zcyl(42, x, K.PISTON_Y, K.CHAMBER_BASE_Z - 4, K.CHAMBER_BASE_Z)   # chamber seat
        b = b + _zcyl(15, x, K.PISTON_Y, z - 58, z)                             # jet housing
        b = b + Location((x + s * 30, K.PISTON_Y, z - 50)) * Box(34, 22, 22)     # float chamber lug
        b = b + _xcyl(9, K.PISTON_Y, z - 50, x + s * 40, x + s * 46)
        b = b + _xcyl(6, K.SPINDLE_Y, z, x - 44, x + 44)                        # spindle bosses
        b = b + _xcyl(6, K.PISTON_Y, z + 28, x + s * 38, x + s * 48)           # piston lifting pin boss
        # bores and holes
        b = b - _ycyl(bore, x, z, y0 - 1, y0 + K.BODY_LEN + 1)
        b = b - _zcyl(34, x, K.PISTON_Y, z + 8, K.CHAMBER_BASE_Z + 1)          # piston well
        b = b - _zcyl(5.0, x, K.PISTON_Y, z - 60, z)                           # jet bearing bore
        b = b - _xcyl(4.2, K.SPINDLE_Y, z, x - 45, x + 45)
        b = b - _xcyl(3.4, K.PISTON_Y, z - 50, x + s * 10, x + s * 50)
        for dx in (-K.STUD_DX, K.STUD_DX):
            b = b - _ycyl(4.4, x + dx, z, y0 - 1, y0 + 10)
        for dx in (-K.CLEANER_BOLT_DX, K.CLEANER_BOLT_DX):
            b = b - _ycyl(3.2, x + dx, z, y0 + K.BODY_LEN - 7.5, y0 + K.BODY_LEN + 1)
        for k in range(3):                                                     # chamber screws
            a = math.radians(90 + 120 * k)
            b = b - _zcyl(2.0, x + K.CHAMBER_SCREW_R * math.cos(a), K.PISTON_Y + K.CHAMBER_SCREW_R * math.sin(a), K.CHAMBER_BASE_Z - 10,
                          K.CHAMBER_BASE_Z + 1)
        return _l(b, spec)
    return build


def throttle_disc(x):
    def build(spec) -> Part:
        r = spec.nom("diameter") / 2
        d = Location((x, K.SPINDLE_Y, K.AXIS_Z)) * Rot(-spec.nom("closed_angle_deg"), 0, 0) * Cylinder(r, 1.2,
                                                                                                         rotation=(90, 0, 0))
        return _l(d - _xcyl(1.2, K.SPINDLE_Y + 3, K.AXIS_Z, x - 8, x + 8), spec)
    return build


def throttle_spindle(spec) -> Part:
    """Spindle along X, built centred on the origin."""
    L = spec.nom("length")
    s = _xcyl(4.0, 0, 0, -L / 2, L / 2)
    s = s - Box(10, 1.2, 9).moved(Location((0, 0, 0)))                         # slot for the disc
    return _l(s, spec)


def throttle_lever(spec) -> Part:
    """Lever on the inboard end of the spindle with the idle stop screw boss (Fig 3.12)."""
    L = spec.nom("length")
    arm = Location((0, 0, -L / 2)) * Box(2.4, 12, L)
    arm = _tf(arm, arm.edges().filter_by(Axis.X), 5.5)
    hub = _xcyl(7, 0, 0, -3, 3)
    stop = _xcyl(4.5, 0, -L + 6, -6, 6)
    return _l(arm + hub + stop - _xcyl(4.1, 0, 0, -4, 4), spec)


# ---- suction chamber, piston, damper (items 6, 8, 10; Fig 3.11) -------------------------------------
def suction_chamber(spec) -> Part:
    """Dashpot dome: flange with three screws, dome, neck for the damper. Base at z = 0."""
    h, d = spec.nom("height"), spec.nom("diameter")
    r = d / 2
    prof = [(0, 0), (r + 3, 0), (r + 3, 4), (r, 4), (r, h - 16), (r - 10, h - 8), (13, h - 6), (11, h), (0, h)]
    c = Sh.revolved(prof) - Sh.revolved([(0, -1), (r - 2, -1), (r - 2, h - 18), (r - 12, h - 10), (6, h - 9), (6, h + 1),
                                          (0, h + 1)])
    for k in range(3):
        a = math.radians(90 + 120 * k)
        c = c - _zcyl(2.2, K.CHAMBER_SCREW_R * math.cos(a), K.CHAMBER_SCREW_R * math.sin(a), -1, 6)
    return _l(c, spec)


def piston(spec) -> Part:
    """Suction piston with its rod and the tapered needle below. Base of the skirt at z = 0."""
    d = spec.nom("diameter")
    p = Sh.revolved([(0, 0), (d / 2 - 12, 0), (d / 2 - 12, 22), (d / 2, 26), (d / 2, 34), (6, 40), (6, 94), (0, 94)])
    p = p - _zcyl(d / 2 - 15, 2.5, 0, -1, 20) - _zcyl(3.0, 0, 0, 30, 95)       # skirt recess, damper bore
    needle = Sh.revolved([(0, -40), (0.6, -40), (1.3, -10), (1.3, 0), (0, 0)])
    return _l(p + needle, spec)


def piston_spring(spec) -> Part:
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("length"), 8, 1), spec)


def damper_cap(spec) -> Part:
    """Knurled cap with the damper rod and plunger (photo 17.7)."""
    d = spec.nom("diameter")
    cap = Sh.revolved([(0, 0), (d / 2, 0), (d / 2, 9), (d / 2 - 2, 12), (0, 12)])
    for k in range(12):
        a = math.radians(30 * k)
        cap = cap - _zcyl(1.0, (d / 2 + 0.4) * math.cos(a), (d / 2 + 0.4) * math.sin(a), 0, 10)
    rod = _zcyl(1.6, 0, 0, -spec.nom("rod_length"), 0)
    plunger = _zcyl(4.5, 0, 0, -spec.nom("rod_length"), -spec.nom("rod_length") + 6)
    return _l(cap + rod + plunger, spec)


# ---- jet, float chamber (items 12-34) ----------------------------------------------------------
def jet_assembly(x):
    def build(spec) -> Part:
        """Jet tube, jet head and the flexible feed tube to the float chamber (Fig 3.11 items 6, 7)."""
        s = K.side(x)
        z = K.AXIS_Z
        tube = _zcyl(2.4, x, K.PISTON_Y, z - 86, z - 4) - _zcyl(1.5, x, K.PISTON_Y, z - 60, z - 3)
        head = _zcyl(5.5, x, K.PISTON_Y, z - 92, z - 84)
        lug = Location((x - s * 9, K.PISTON_Y, z - 88)) * Box(18, 8, 6)
        feed = _rod([(x, K.PISTON_Y, z - 92), (x + s * K.FLOAT_DX / 2, K.PISTON_Y, z - 108),
                     (x + s * K.FLOAT_DX, K.PISTON_Y, z - 93)], 3.0, 20.0)
        return _l(tube + head + lug + feed, spec)
    return build


def jet_nut(kind):
    def build(spec) -> Part:
        af, t = spec.nom("across_flats"), spec.nom("thickness")
        from build123d import RegularPolygon
        n = extrude(RegularPolygon(af / math.sqrt(3), 6), t) - _zcyl(spec.nom("bore") / 2, 0, 0, -1, t + 1)
        if kind == "adjusting":
            n = n + _zcyl(af / 2 - 1, 0, 0, -6, 0) - _zcyl(spec.nom("bore") / 2, 0, 0, -7, 1)
        return _l(n, spec)
    return build


def float_chamber(x):
    def build(spec) -> Part:
        s = K.side(x)
        d, h = spec.nom("diameter"), spec.nom("height")
        cx, cy = x + s * K.FLOAT_DX, K.PISTON_Y
        top = K.AXIS_Z - 50 + h * 0.5
        c = _zcyl(d / 2, cx, cy, top - h, top)
        c = _tf(c, c.edges().group_by(Axis.Z)[0], 6.0)
        c = c - _zcyl(d / 2 - 2, cx, cy, top - h + 2, top + 1)
        c = c + _zcyl(6, cx, cy, top - h - 6, top - h + 1)                         # feed tube union
        c = c + Location((cx - s * (d / 2 + 4), cy, K.AXIS_Z - 50)) * Box(14, 20, 20)   # lug to the body
        c = c - _xcyl(3.4, cy, K.AXIS_Z - 50, cx - s * (d / 2 + 12), cx - s * (d / 2 - 4))
        return _l(c, spec)
    return build


def float_lid(x):
    def build(spec) -> Part:
        """Lid with the fuel inlet union and the overflow pipe (Haynes Sec 18 para 1)."""
        s = K.side(x)
        d = spec.nom("diameter")
        cx, cy = x + s * K.FLOAT_DX, K.PISTON_Y
        top = K.AXIS_Z - 50 + spec.nom("chamber_height") * 0.5
        lid = _zcyl(d / 2 + 1.5, cx, cy, top, top + 7)
        lid = lid + _zcyl(9, cx, cy, top + 7, top + 16)                              # inlet union boss
        lid = lid + _xcyl(4.5, cy, top + 12, cx, cx - s * 22)                         # fuel inlet spigot
        lid = lid + _rod([(cx + s * 12, cy, top + 7), (cx + s * 12, cy, top + 18), (cx + s * 12, cy + 30, top + 18)],
                         2.2, 6.0)                                                    # overflow pipe
        for k in range(3):
            a = math.radians(120 * k)
            lid = lid - _zcyl(1.8, cx + (d / 2 - 4) * math.cos(a), cy + (d / 2 - 4) * math.sin(a), top - 1, top + 8)
        return _l(lid, spec)
    return build


def float_(spec) -> Part:
    d, h = spec.nom("diameter"), spec.nom("height")
    f = Sh.tube(d, d - 18, h)
    return _l(f, spec)


# ---- heat shield, distance pieces, gaskets (photo 18.5) ------------------------------------------------
def heat_shield(spec) -> Part:
    """Steel shield between manifold and carburettors, its lower edge turned out under the
    float chambers to keep exhaust heat off them."""
    t = spec.nom("thickness")
    y0 = K.MANIFOLD_FACE_Y + K.GASKET
    zt, zb = K.AXIS_Z + 46, K.AXIS_Z - 92
    plate = Location((0, y0 + t / 2, (zt + zb) / 2)) * Box(320, t, zt - zb)
    plate = _tf(plate, plate.edges().filter_by(Axis.Y), 16.0)
    lip = Location((0, y0 + 32, zb + t / 2)) * Box(300, 64, t)
    sh = plate + lip
    for xc in K.CARB_X:
        sh = sh - _ycyl(21, xc, K.AXIS_Z, y0 - 1, y0 + t + 1)
        for dx in (-K.STUD_DX, K.STUD_DX):
            sh = sh - _ycyl(4.4, xc + dx, K.AXIS_Z, y0 - 1, y0 + t + 1)
    return _l(sh, spec)


def distance_piece(spec) -> Part:
    """Composition insulating block, built on the carburettor axis at the origin (y from 0)."""
    t = spec.nom("thickness")
    b = _yslot(0, 0, 78, 52, 0, t) - _ycyl(20.5, 0, 0, -1, t + 1)
    for dx in (-K.STUD_DX, K.STUD_DX):
        b = b - _ycyl(4.4, dx, 0, -1, t + 1)
    return _l(b, spec)


def flange_gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = _yslot(0, 0, 76, 50, 0, t) - _ycyl(20, 0, 0, -1, t + 1)
    for dx in (-K.STUD_DX, K.STUD_DX):
        g = g - _ycyl(4.4, dx, 0, -1, t + 1)
    return _l(g, spec)


# ---- linkage (items 46-72; photo 17.1) ----------------------------------------------------------------
def coupling_shaft(spec) -> Part:
    """Interconnecting throttle shaft between the spindles, with its two clamp couplings."""
    x0 = K.CARB_X[1] + 54                                  # clamps grip the spindle ends inboard of the levers
    x1 = K.CARB_X[0] - 54
    y, z = K.SPINDLE_Y, K.AXIS_Z
    s = _xcyl(spec.nom("diameter") / 2, y, z, x0, x1)
    for xc in (x0, x1):
        clamp = Location((xc, y, z)) * Box(14, 16, 16)
        clamp = clamp + Location((xc, y, z + 11)) * Box(14, 5, 8)
        s = s + _tf(clamp, clamp.edges().filter_by(Axis.X), 2.5)
        s = s - _ycyl(1.6, xc, z + 11, y - 9, y + 9)
    return _l(s, spec)


def jet_rod(spec) -> Part:
    """Rod linking the two jet levers to the choke cable lever below the instruments."""
    z = K.AXIS_Z - 88
    y = K.PISTON_Y + 14
    r = _xcyl(spec.nom("diameter") / 2, y, z, K.CARB_X[1] + 10, K.CARB_X[0] - 10)
    lever = Location((0, y, z - 14)) * Box(6, 4, 30)
    return _l(r + lever, spec)


def return_spring(spec) -> Part:
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("length"), 14, 1.5), spec)


# ---- air cleaners (Fig 3.1) -------------------------------------------------------------------------
def cleaner_adaptor(spec) -> Part:
    """Item 1: short stub on the carburettor intake flange. Built along +Y from y = 0."""
    a = _yslot(0, 0, 70, 58, 0, 4) + _ycyl(24, 0, 0, 0, 12)
    a = a - _ycyl(20, 0, 0, -1, 13)
    for dx in (-K.CLEANER_BOLT_DX, K.CLEANER_BOLT_DX):
        a = a - _ycyl(3.4, dx, 0, -1, 5)
    return _l(a, spec)


def cleaner_baseplate(spec) -> Part:
    """Item 3: pressed baseplate with a raised rim and the intake hole."""
    d = spec.nom("diameter")
    p = _ycyl(d / 2, 0, 0, 0, 1.6) + (_ycyl(d / 2, 0, 0, 0, 8) - _ycyl(d / 2 - 2, 0, 0, -1, 9))
    p = p + (_ycyl(32, 0, 0, 1.6, 6) - _ycyl(29, 0, 0, 1, 7))
    p = p - _ycyl(24, 0, 0, -1, 3)
    for dx in (-K.CLEANER_BOLT_DX, K.CLEANER_BOLT_DX):
        p = p - _ycyl(3.4, dx, 0, -1, 3)
    return _l(p, spec)


def cleaner_element(spec) -> Part:
    """Item 4: pleated paper element."""
    d, L = spec.nom("diameter"), spec.nom("length")
    pts = []
    n = 72
    for k in range(n * 2):
        a = math.pi * k / n
        r = d / 2 if k % 2 == 0 else d / 2 - 6
        pts.append((r * math.cos(a), r * math.sin(a)))
    from build123d import Polygon
    pl = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    e = extrude(pl * Polygon(*pts, align=None), L) - _ycyl(d / 2 - 22, 0, 0, -1, L + 1)
    e = e + (_ycyl(d / 2 + 1, 0, 0, 0, 3) - _ycyl(d / 2 - 22, 0, 0, -1, 4))
    e = e + (_ycyl(d / 2 + 1, 0, 0, L - 3, L) - _ycyl(d / 2 - 22, 0, 0, L - 4, L + 1))
    return _l(e, spec)


def cleaner_case(x):
    def build(spec) -> Part:
        """Item 5: drawn steel case with the intake tube turned down and forward."""
        d, depth = spec.nom("diameter"), spec.nom("depth")
        s = K.side(x)
        c = _ycyl(d / 2, 0, 0, 0, depth)
        c = _tf(c, c.edges().group_by(Axis.Y)[-1], 14.0)
        c = c - (_ycyl(d / 2 - 1.2, 0, 0, -1, depth - 1.2))
        tube = _rod([(s * (d / 2 - 14), depth * 0.45, -d / 2 + 12), (s * (d / 2 + 10), depth * 0.45, -d / 2 - 14),
                     (s * (d / 2 + 22), depth * 0.45, -d / 2 - 44)], 20.0, 18.0)
        tube = tube - _rod([(s * (d / 2 - 14), depth * 0.45, -d / 2 + 12), (s * (d / 2 + 10), depth * 0.45, -d / 2 - 14),
                            (s * (d / 2 + 22.5), depth * 0.45, -d / 2 - 45)], 18.5, 18.0)
        c = c + tube
        for dx in (-K.CLEANER_BOLT_DX, K.CLEANER_BOLT_DX):
            c = c + _ycyl(7, dx, 0, depth - 3, depth + 1) - _ycyl(3.4, dx, 0, depth - 4, depth + 2)
        return _l(c, spec)
    return build


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def nut(size):
    return lambda spec: _l(F.hex_nut(size), spec)


def stud(spec) -> Part:
    return _l(Sh.chamfered_cyl(spec.nom("thread_diameter"), spec.nom("length"), 0.6), spec)


def washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def float_bolt(spec) -> Part:
    return _l(F.hex_bolt("5/16", spec.nom("length") / 25.4), spec)


FRONT, REAR = K.CARB_X
PARTS = {
    "fuel.carbs.body-front": {"build": body(FRONT)},
    "fuel.carbs.body-rear": {"build": body(REAR)},
    "fuel.carbs.throttle-disc-front": {"build": throttle_disc(FRONT)},
    "fuel.carbs.throttle-disc-rear": {"build": throttle_disc(REAR)},
    "fuel.carbs.throttle-spindle": {"build": throttle_spindle},
    "fuel.carbs.throttle-lever": {"build": throttle_lever},
    "fuel.carbs.suction-chamber": {"build": suction_chamber},
    "fuel.carbs.piston": {"build": piston},
    "fuel.carbs.piston-spring": {"build": piston_spring},
    "fuel.carbs.damper": {"build": damper_cap},
    "fuel.carbs.jet-front": {"build": jet_assembly(FRONT)},
    "fuel.carbs.jet-rear": {"build": jet_assembly(REAR)},
    "fuel.carbs.jet-adjusting-nut": {"build": jet_nut("adjusting")},
    "fuel.carbs.jet-locking-nut": {"build": jet_nut("locking")},
    "fuel.carbs.float-chamber-front": {"build": float_chamber(FRONT)},
    "fuel.carbs.float-chamber-rear": {"build": float_chamber(REAR)},
    "fuel.carbs.float-lid-front": {"build": float_lid(FRONT)},
    "fuel.carbs.float-lid-rear": {"build": float_lid(REAR)},
    "fuel.carbs.float": {"build": float_},
    "fuel.carbs.float-bolt": {"build": float_bolt},
    "fuel.carbs.heat-shield": {"build": heat_shield},
    "fuel.carbs.distance-piece": {"build": distance_piece},
    "fuel.carbs.flange-gasket": {"build": flange_gasket},
    "fuel.carbs.stud": {"build": stud},
    "fuel.carbs.nut": {"build": nut("5/16")},
    "fuel.carbs.washer": {"build": washer},
    "fuel.carbs.coupling-shaft": {"build": coupling_shaft},
    "fuel.carbs.jet-rod": {"build": jet_rod},
    "fuel.carbs.return-spring": {"build": return_spring},
    "fuel.carbs.cleaner-adaptor": {"build": cleaner_adaptor},
    "fuel.carbs.cleaner-gasket": {"build": flange_gasket},
    "fuel.carbs.cleaner-baseplate": {"build": cleaner_baseplate},
    "fuel.carbs.cleaner-element": {"build": cleaner_element},
    "fuel.carbs.cleaner-case-front": {"build": cleaner_case(FRONT)},
    "fuel.carbs.cleaner-case-rear": {"build": cleaner_case(REAR)},
    "fuel.carbs.cleaner-bolt": {"build": bolt("1/4")},
}
