"""Pistons, rings, gudgeon pins and connecting rods (18G, clamp-bolt small end).

Piston frame: gudgeon pin centre at the origin, pin axis along X, crown up +Z.
Ring frame: axis Z, ring bottom at z = 0.
Rod frame: big-end centre at the origin, crank axis along X, small end at +Z.
"""
import math

from build123d import Align, Box, Cylinder, Location, Part, Plane, Rot, Solid, Vector, extrude, Polygon

from mgb import engine_layout as E, fasteners as F, probes, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
GROOVES = [(5.5, 1.6), (9.7, 1.6), (13.9, 1.6), (18.1, 4.0)]   # (depth below crown to groove top, height)


def _l(p, spec):
    p.label = spec.id
    return p


def xcyl(r, L, x=0.0, y=0.0, z=0.0):
    return Cylinder(r, L, rotation=(0, 90, 0)).moved(Location((x, y, z)))


def piston(spec) -> Part:
    D = spec.nom("diameter")
    ch = spec.nom("compression_height")
    H = spec.nom("overall_height")
    pin = spec.nom("gudgeon_bore")
    top, bot = ch, ch - H
    body = Sh.revolved([(0, top), (D / 2 - 0.6, top), (D / 2, top - 0.6), (D / 2, bot), (0, bot)])
    body = body - Sh.cyl(D - 9, top - 7 - bot, z0=bot - 1)       # hollow skirt, 7 mm crown
    for depth, h in GROOVES:                                     # ring grooves
        z1 = top - depth
        body = body - Sh.tube(D + 2, D - 7.4, h, z0=z1 - h)
    for depth, h in GROOVES[-1:]:                                # scraper groove drain slots
        z1 = top - depth - h
        for k in range(6):
            a = math.radians(30 + 60 * k)
            body = body - Cylinder(1.4, 12, rotation=(0, 90, 0)).moved(
                Location(((D / 2 - 4) * math.cos(a), (D / 2 - 4) * math.sin(a), z1 + h / 2)) * Rot(0, 0, math.degrees(a)))
    boss = xcyl(pin / 2 + 6, D - 14)                             # gudgeon bosses
    body = body + (boss & Sh.cyl(D - 2, 30, z0=-15))
    body = body - xcyl(pin / 2, D + 2)
    return _l(body, spec)


def ring(spec) -> Part:
    D = 80.26
    w, h = spec.nom("radial_width"), spec.nom("height")
    r = Sh.tube(D, D - 2 * w, h)
    r = r - Box(1.2, w * 3, h * 3).moved(Location((0, D / 2 - w / 2, h / 2)))   # the gap
    if "scraper" in spec.id:
        for k in range(12):
            a = math.radians(15 + 30 * k)
            r = r - Box(6, w * 3, 1.2).moved(Location((D / 2 * math.cos(a), D / 2 * math.sin(a), h / 2)) * Rot(0, 0, math.degrees(a) + 90))
    return _l(r, spec)


def gudgeon_pin(spec) -> Part:
    d, L, g = spec.nom("outside_diameter"), spec.nom("length"), spec.nom("clamp_groove_width")
    p = Rot(0, 90, 0) * Sh.revolved([(0, -L / 2), (d / 2 - 0.5, -L / 2), (d / 2, -L / 2 + 0.5),
                                     (d / 2, L / 2 - 0.5), (d / 2 - 0.5, L / 2), (0, L / 2)])
    # flat notch facing the clamp bolt, which locates the semi-floating pin
    p = p - Box(g, 4, d + 2, align=(Align.CENTER, Align.MIN, Align.CENTER)).moved(Location((0, d / 2 - 1.2, 0)))
    return _l(p - Rot(0, 90, 0) * Sh.cyl(9.0, L + 2, z0=-L / 2 - 1), spec)


def _split(angle):
    """Unit normal of the angular big-end split plane (contains the crank axis)."""
    a = math.radians(angle)
    return Vector(0, math.sin(a), math.cos(a))


def _half_space(n: Vector, keep_positive: bool, size=400):
    """A big box on one side of the plane through the origin with normal n."""
    b = Box(size, size, size, align=(Align.CENTER, Align.CENTER, Align.MIN if keep_positive else Align.MAX))
    pl = Plane(origin=(0, 0, 0), z_dir=n, x_dir=(1, 0, 0))
    return pl.location * b


def _big_end_ring(w):
    bore = 47.655 + 2 * 1.6
    ring = xcyl(bore / 2 + 7, w) - xcyl(bore / 2, w + 2)
    return ring, bore


def rod(spec) -> Part:
    c, w, ws = spec.nom("centres"), spec.nom("big_end_width"), spec.nom("small_end_width")
    n = _split(spec.nom("split_angle"))
    ring, bore = _big_end_ring(w)
    t = Vector(0, n.Z, -n.Y)                        # in-plane direction across the bore
    bosses = None
    for s in (-1, 1):
        cen = t * (s * (bore / 2 + 7))
        b = Solid.make_cylinder(8, 34, Plane(origin=cen - n * 17, z_dir=n, x_dir=(1, 0, 0)))
        bosses = b if bosses is None else bosses + b
    upper = (ring + bosses) & _half_space(n, True)
    beam = extrude(Plane.YZ.offset(-w * 0.3) * Polygon((-15, 22), (15, 22), (8, c - 14), (-8, c - 14), align=None), w * 0.6)
    web = Box(4, 26, c - 40, align=BASE).moved(Location((0, 0, 22)))
    eye = xcyl(16, ws, z=c)
    lug = Box(ws, 14, 20, align=BASE).moved(Location((0, 13, c - 10)))
    r = upper + beam + eye + lug
    r = r - xcyl(bore / 2, w + 4)
    r = r - xcyl(9.525, ws + 2, z=c)                                            # gudgeon pin bore
    r = r - Box(ws + 2, 16, 1.2, align=(Align.CENTER, Align.MIN, Align.CENTER)).moved(Location((0, 6, c)))  # clamp slit
    r = r - Cylinder(4.1, 40, rotation=(90, 0, 0)).moved(Location((0, 14, c + 6)))  # clamp bolt hole (tangent to the pin)
    for s in (-1, 1):                                                           # big-end bolt holes
        cen = t * (s * (bore / 2 + 7))
        r = r - Solid.make_cylinder(4.9, 80, Plane(origin=cen - n * 40, z_dir=n, x_dir=(1, 0, 0)))
    return _l(r, spec)


def rod_cap(spec) -> Part:
    w = spec.nom("big_end_width")
    n = _split(45)
    ring, bore = _big_end_ring(w)
    t = Vector(0, n.Z, -n.Y)
    bosses = None
    for s in (-1, 1):
        cen = t * (s * (bore / 2 + 7))
        b = Solid.make_cylinder(8, 34, Plane(origin=cen - n * 17, z_dir=n, x_dir=(1, 0, 0)))
        bosses = b if bosses is None else bosses + b
    cap = (ring + bosses) & _half_space(n, False)
    cap = cap - xcyl(bore / 2, w + 4)
    for s in (-1, 1):
        cen = t * (s * (bore / 2 + 7))
        cap = cap - Solid.make_cylinder(4.9, 80, Plane(origin=cen - n * 40, z_dir=n, x_dir=(1, 0, 0)))
    return _l(cap, spec)


def big_end_bolt(spec) -> Part:
    return _l(F.hex_bolt("3/8", spec.nom("length") / 25.4), spec)


BOLT_PITCH = (47.655 + 2 * 1.6) / 2 + 7      # big-end bolt offset either side of the bore


def lockwasher(spec) -> Part:
    t = spec.nom("thickness")
    p = Sh.slot_plate(2 * BOLT_PITCH + 15, 15, t)
    for x in (-BOLT_PITCH, BOLT_PITCH):
        p = p - Sh.cyl(9.8, t * 3, z0=-t).moved(Location((x, 0, 0)))
        p = p + Box(10, t, 6, align=(Align.CENTER, Align.MIN, Align.MIN)).moved(Location((x, 7.5 - t, 0)))
    return _l(p, spec)


def clamp_bolt(spec) -> Part:
    return _l(F.hex_bolt("5/16", spec.nom("length") / 25.4), spec)


PARTS = {
    "engine.block.piston": {"build": piston},
    "engine.block.piston-ring-top": {"build": ring},
    "engine.block.piston-ring-taper": {"build": ring},
    "engine.block.piston-ring-scraper": {"build": ring},
    "engine.block.gudgeon-pin": {"build": gudgeon_pin, "probes": {
        "outside_diameter": lambda p: probes.bbox_size(p, "y")}},
    "engine.block.connecting-rod": {"build": rod},
    "engine.block.connecting-rod-cap": {"build": rod_cap},
    "engine.block.big-end-shell": {"build": None, "probes": {"length": lambda p: probes.bbox_size(p, "x")}},
    "engine.block.big-end-bolt": {"build": big_end_bolt},
    "engine.block.big-end-lockwasher": {"build": lockwasher},
    "engine.block.gudgeon-clamp-bolt": {"build": clamp_bolt},
}


def big_end_shell(spec) -> Part:
    """Lower half-shell on the 47.655 mm crankpin, axis along X."""
    L, w, d = spec.nom("length"), spec.nom("wall_thickness"), 47.655
    ring = Rot(0, 90, 0) * Sh.tube(d + 2 * w, d, L, z0=-L / 2)
    half = ring & Box(L + 2, d + 2 * w + 2, (d + 2 * w) / 2 + 1, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return _l(half, spec)


PARTS["engine.block.big-end-shell"]["build"] = big_end_shell
