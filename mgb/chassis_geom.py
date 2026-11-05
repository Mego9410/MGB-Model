"""Geometry helpers shared by the suspension, steering and wheel parts (P9).

All solids are built in standalone (algebra) mode in the car frame unless stated.
"""
from __future__ import annotations

import math

from build123d import (Align, Box, Compound, Cylinder, Edge, Face, Location, Part, Plane, Rot, Solid, Vector, Wire,
                       extrude, revolve, sweep, Axis)

from mgb import shapes as Sh
from mgb.poly2d import ccw

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def lab(p, spec):
    p.label = spec.id
    return p


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def xprism(pts_yz, x0, x1):
    face = Face(Wire.make_polygon([(0.0, y, z) for y, z in ccw(pts_yz)], close=True))
    return extrude(face, x1 - x0, dir=(1, 0, 0)).moved(Location((x0, 0, 0)))


def yprism(pts_xz, y0, y1):
    face = Face(Wire.make_polygon([(x, 0.0, z) for x, z in ccw(pts_xz)], close=True))
    return extrude(face, y1 - y0, dir=(0, 1, 0)).moved(Location((0, y0, 0)))


def zprism(pts_xy, z0, z1):
    face = Face(Wire.make_polygon([(x, y, 0.0) for x, y in ccw(pts_xy)], close=True))
    return extrude(face, z1 - z0).moved(Location((0, 0, z0)))


def xcyl(r, x0, x1, y=0.0, z=0.0):
    return Location((x0, y, z)) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=BASE)


def ycyl(r, y0, y1, x=0.0, z=0.0):
    return Location((x, y0, z)) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=BASE)


def zcyl(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def zrev(profile):
    """Revolve an (r, z) profile about z."""
    return Sh.revolved(profile)


def xrev(profile):
    """Revolve an (r, x) profile about the x axis."""
    return Rot(0, 90, 0) * Sh.revolved([(r, x) for r, x in profile])


def yrev(profile):
    """Revolve an (r, y) profile about the y axis."""
    return Rot(-90, 0, 0) * Sh.revolved(profile)


def frame_to(p0, d, xhint=(1.0, 0.0, 0.0)):
    """Location with origin p0 and local z along d (local x as near xhint as possible)."""
    zd = Vector(*d).normalized()
    xd = Vector(*xhint)
    xd = xd - zd * xd.dot(zd)
    if xd.length < 1e-6:
        xd = Vector(0, 1, 0) - zd * zd.Y
    return Location(Plane(origin=p0, x_dir=xd.normalized(), z_dir=zd))


def rod(p0, p1, r):
    """Cylinder of radius r from point p0 to point p1."""
    v = Vector(*p1) - Vector(*p0)
    return frame_to(p0, v) * Cylinder(r, v.length, align=BASE)


def tube_between(p0, p1, ro, ri):
    v = Vector(*p1) - Vector(*p0)
    return frame_to(p0, v) * Sh.tube(2 * ro, 2 * ri, v.length)


def mirror_side(p, side):
    """A solid drawn for the left (+y) side, mirrored for the right (side -1)."""
    return p if side > 0 else p.mirror(Plane.XZ)


def compound(solids, label=None):
    c = Compound(children=list(solids))
    if label:
        c.label = label
    return c


def swept_rod(points, r):
    """A round rod swept along a polyline with rounded corners (solid sweep)."""
    from build123d import FilletPolyline
    pts = [Vector(*p) for p in points]
    keep = [pts[0]]                       # drop interior points in line with their neighbours (a zero fillet breaks the sweep)
    for a, b in zip(pts[1:-1], pts[2:]):
        u, v = a - keep[-1], b - a
        if u.length > 1e-6 and v.length > 1e-6 and u.normalized().cross(v.normalized()).length > 2e-3:
            keep.append(a)
    pts = keep + pts[-1:] if len(pts) > 1 else pts
    try:
        path = Wire(FilletPolyline(*pts, radius=r * 2.5).edges()) if len(pts) > 2 else Wire([Edge.make_line(*pts)])
    except Exception:
        path = Wire.make_polygon(pts, close=False)
    t = path.tangent_at(0)
    prof = Face(Wire.make_circle(r, Plane(pts[0], z_dir=t)))
    return sweep(prof, path=path, transition=__import__("build123d").Transition.ROUND)


def hexagon(af, h, z0=0.0):
    from build123d import RegularPolygon
    return extrude(RegularPolygon(af / math.sqrt(3), 6, major_radius=True), h).moved(Location((0, 0, z0)))


def castellated_nut(af, t, bore, slots=6, slot_w=None, slot_d=None, z0=0.0):
    """Hex castellated nut along +z: hex lower part, round crown with slots."""
    slot_w = slot_w or bore * 0.28
    slot_d = slot_d or t * 0.35
    n = hexagon(af, t - slot_d, z0)
    n = n + zcyl(af / 2 * 0.97, z0 + t - slot_d - 0.01, z0 + t)
    n = n - zcyl(bore / 2, z0 - 1, z0 + t + 1)
    for k in range(slots // 2):
        n = n - Rot(0, 0, 30 + 60 * k) * box(-af, af, -slot_w / 2, slot_w / 2, z0 + t - slot_d, z0 + t + 1)
    return n


def split_pin(d, length, z_axis=False):
    """Split pin along +x: eye at x=0, two legs to x=length (d = wire pair width)."""
    r = d / 4
    eye = Location((0, 0, 0)) * Rot(90, 0, 0) * __import__("build123d").Torus(d / 2, r)
    legs = xcyl(r, 0, length, 0, r) + xcyl(r, 0, length, 0, -r)
    return eye + legs


def spring_washer(size, z0=0.0):
    """Split spring washer (square section), axis z, from z0."""
    from mgb import fasteners as F
    d = F.THREADS[size][0] * IN
    t = max(1.2, d * 0.16)
    w = Sh.tube(d * 1.75, d + 0.6, t, z0)
    return w - box(-0.6, 0.6, 0, d, z0 - 1, z0 + t + 1)
