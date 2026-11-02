"""Geometry helpers shared by the brake part scripts (parts/brakes/*). Standalone (algebra) mode."""
from __future__ import annotations

import math

from build123d import (Align, Box, Circle, Cylinder, Face, FilletPolyline, Location, Part, Plane, Polygon, Rot, Wire,
                       extrude, sweep, Solid)

from mgb import fasteners as F, shapes as Sh
from mgb.poly2d import circle_pts, hull

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def lab(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def ycyl(r, y0, y1, x=0.0, z=0.0):
    return Location((x, y0, z)) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=BASE)


def xcyl(r, x0, x1, y=0.0, z=0.0):
    return Location((x0, y, z)) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=BASE)


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def yrev(profile):
    """Revolve an (r, y) profile about the y axis."""
    return Rot(-90, 0, 0) * Sh.revolved(profile)


def xrev(profile):
    """Revolve an (r, x) profile about the x axis."""
    return Rot(0, 90, 0) * Sh.revolved(profile)


def yprism(pts_xz, y0, y1):
    face = Face(Wire.make_polygon([(x, 0.0, z) for x, z in pts_xz], close=True))
    return extrude(face, y1 - y0, dir=(0, 1, 0)).moved(Location((0, y0, 0)))


def xprism(pts_yz, x0, x1):
    face = Face(Wire.make_polygon([(0.0, y, z) for y, z in pts_yz], close=True))
    return extrude(face, x1 - x0, dir=(1, 0, 0)).moved(Location((x0, 0, 0)))


def zprism(pts_xy, z0, z1):
    face = Face(Wire.make_polygon([(x, y, 0.0) for x, y in pts_xy], close=True))
    return extrude(face, z1 - z0, dir=(0, 0, 1)).moved(Location((0, 0, z0)))


def hexp(af, h, z0=0.0):
    """Hex prism along z, flats on +/-y."""
    r = af / math.sqrt(3)
    return zprism([(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k))) for k in range(6)], z0, z0 + h)


def chamfered_hex(af, h, z0=0.0):
    r = af / math.sqrt(3)
    return hexp(af, h, z0) & Sh.revolved([(0, z0 - 0.1), (af / 2 + 0.2, z0 - 0.1), (r + 0.4, z0 + h * 0.25),
                                          (r + 0.4, z0 + h * 0.75), (af / 2 + 0.2, z0 + h + 0.1), (0, z0 + h + 0.1)])


def lobes(r_body, pts_r, n=48):
    """Hull of a circle and small circles: (x, y, r) list."""
    pts = circle_pts(0, 0, r_body, n) if r_body else []
    for x, y, r in pts_r:
        pts += circle_pts(x, y, r, 20)
    return hull(pts)


def path_wire(points, radius):
    for rr in (radius, radius * 0.5, radius * 0.25, radius * 0.1):
        try:
            return FilletPolyline(*points, radius=rr)
        except Exception:
            continue
    from build123d import Polyline
    return Polyline(*points)


def rod(points, r, radius=10.0):
    """Round bar or pipe swept along a filleted polyline."""
    path = path_wire(points, radius)
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    return sweep(pl * Circle(r), path=path)


def tube_rod(points, ro, ri, radius=10.0):
    """Hollow pipe; falls back to a solid one if the hollow sweep fails."""
    path = path_wire(points, radius)
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    try:
        t = sweep(pl * Circle(ro) - pl * Circle(ri), path=path)
        if t.is_valid:
            return t
    except Exception:
        pass
    return sweep(pl * Circle(ro), path=path)


def flat_bar(points, w, t, radius=8.0, up=(0, 0, 1)):
    """Flat bar w wide (across, in the path's plane) and t thick (along `up`) swept on a polyline."""
    path = path_wire(points, radius)
    tan = path.tangent_at(0)
    pl = Plane(origin=path.position_at(0), z_dir=tan, x_dir=up)
    from build123d import Rectangle
    return sweep(pl * Rectangle(t, w), path=path, transition=__import__("build123d").Transition.RIGHT)


def along(p, a, b):
    """Place a part drawn along +z from the origin so it runs from point a toward b (a at z = 0)."""
    d = [b[i] - a[i] for i in range(3)]
    return Plane(origin=a, z_dir=d).location * p


def frame(origin, z_dir, x_dir=None):
    if x_dir is None:
        return Plane(origin=origin, z_dir=z_dir).location
    return Plane(origin=origin, z_dir=z_dir, x_dir=x_dir).location


def bolt(size, length_in, series="UNF"):
    return F.hex_bolt(size, length_in, series)


def nut(size, series="UNF"):
    return F.hex_nut(size, series)


def nyloc(size):
    """Self-locking nut: hex with the nylon insert collar on top (seat at z = 0)."""
    d = F.THREADS[size][0] * IN
    af, t = (v * IN for v in F.NUT[size])
    n = chamfered_hex(af, t) + zc(af / 2 - 0.4, t - 0.01, t + 0.3 * d) - zc(d / 2 * 0.92, -1, t + d)
    return n


def spring_washer(size):
    d = F.THREADS[size][0] * IN
    t = 0.06 * d + 0.6
    od, id_ = 1.7 * d + 0.5, d + 0.4
    w = Sh.washer(od, id_, t) - Location(((od + id_) / 4, 0, t / 2)) * Rot(0, 0, 20) * Box(od, 1.0, t + 1)
    return w, t


def plain_washer(size):
    i, o, t = (v * IN for v in F.WASHER[size])
    return Sh.washer(o, i, t), t


def coil(wire, od, length, coils):
    return Sh.coil_spring(wire, od, length, coils, end_turns=0.5)


def tension_spring(p0, p1, wire, od, hook_axis=(0, 1, 0)):
    """Close-coiled tension spring with a hook at each end, from p0 to p1 (hook centres)."""
    from build123d import Torus
    L = math.dist(p0, p1)
    body = L - 2 * od
    c = Sh.coil_spring(wire, od, body, body / wire * 0.98, end_turns=0.25).moved(Location((0, 0, od)))
    r = od / 2 - wire / 2
    hk = Location((0, 0, od / 2)) * Rot(90, 0, 0) * Torus(od / 2 - wire / 2, wire / 2)
    hk2 = Location((0, 0, L - od / 2)) * Rot(90, 0, 0) * Torus(od / 2 - wire / 2, wire / 2)
    s = c + hk + hk2
    return Plane(origin=p0, z_dir=[p1[i] - p0[i] for i in range(3)], x_dir=hook_axis).location * s


def mirror_y(p):
    """Mirror a part in the car's centre plane (y -> -y): a handed part for the other side."""
    return p.mirror(Plane.XZ)


def split_pin(d, L):
    """Split pin of nominal size d (the hole it fits): two half-round legs side by side along x and an eye, along
    +z from the eye's underside."""
    from build123d import Torus
    r = d / 4
    legs = zc(r * 0.98, 0, L, r, 0) + zc(r * 0.98, 0, L - 2.0, -r, 0)
    eye = Location((0, 0, -r * 1.6)) * Rot(90, 0, 0) * Torus(r * 1.6, r)
    return legs + eye


def cyl_radius(face):
    """Radius of a cylindrical face (None if not cylindrical)."""
    if face.geom_type.name != "CYLINDER":
        return None
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    return BRepAdaptor_Surface(face.wrapped).Cylinder().Radius()


def bore(p, r):
    """Diameter of the cylindrical face nearest radius r (0 if none within 0.5 mm): the bore probe."""
    rs = [v for v in (cyl_radius(f) for f in p.faces()) if v and abs(v - r) < 0.5]
    return 2 * min(rs, key=lambda v: abs(v - r)) if rs else 0.0
