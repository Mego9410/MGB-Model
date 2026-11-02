"""Shape helpers shared by the electrical parts (P10): round bodies about an axis, hulls of
circles extruded into lugs and brackets, cables swept along routed polylines, lens and bezel
profiles. Standalone (algebra) mode, like mgb.shapes."""
from __future__ import annotations

import math

from build123d import (Align, Axis, Box, Circle, Cylinder, Edge, Face, FilletPolyline, Location, Part, Plane,
                       Polygon, Polyline, Rot, Wire, extrude, fillet, sweep)

from mgb import poly2d as P2, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def label(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    """Cylinder about Z from z0 to z1 at (x, y)."""
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def xc(r, x0, x1, y=0.0, z=0.0):
    return Cylinder(r, x1 - x0, rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def yc(r, y0, y1, x=0.0, z=0.0):
    return Cylinder(r, y1 - y0, rotation=(90, 0, 0)).moved(Location((x, (y0 + y1) / 2, z)))


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=BASE).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, z0)))


def rev(profile):
    """Revolve a closed (r, z) profile about Z (points in order round the outline)."""
    return Sh.revolved(profile)


def tryfillet(p, edges, r):
    try:
        out = fillet(edges, r)
        return out if out.is_valid else p
    except Exception:  # noqa: BLE001 - keep the sharp shape if the kernel refuses
        return p


def hull_xy(circles, z0, z1, n=28):
    """Prism (along Z, z0..z1) on the convex hull of circles [(x, y, r)] in the XY plane."""
    pts = [p for cx, cy, r in circles for p in P2.circle_pts(cx, cy, r, n)]
    poly = P2.hull(pts)
    return extrude(Plane.XY.offset(z0) * Polygon(*poly, align=None), z1 - z0)


def poly_xy(pts, z0, z1):
    """Prism along Z (z0..z1) on a polygon in the XY plane (either winding)."""
    return extrude(Plane.XY.offset(z0) * Polygon(*P2.ccw(pts), align=None), z1 - z0)


def sector(r0, r1, a0, a1, z0, z1, n=10):
    """Annular sector between radii r0 and r1, angles a0..a1 (deg), as a prism along Z."""
    pts = [(r1 * math.cos(math.radians(a0 + (a1 - a0) * k / n)), r1 * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
           for k in range(n + 1)]
    pts += [(r0 * math.cos(math.radians(a1 - (a1 - a0) * k / n)), r0 * math.sin(math.radians(a1 - (a1 - a0) * k / n)))
            for k in range(n + 1)]
    return poly_xy(pts, z0, z1)


def polar(r, deg):
    return r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg))


def _path(points, radius):
    pts = [tuple(float(c) for c in p) for p in points]
    clean = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean[-1]) > 1e-3:
            clean.append(p)
    if len(clean) == 2:
        return Polyline(*clean)
    for r in (radius, radius * 0.6, radius * 0.35, radius * 0.18, radius * 0.08):
        try:
            return FilletPolyline(*clean, radius=r)
        except Exception:  # noqa: BLE001
            continue
    return Polyline(*clean)


def cable(points, d, radius=30.0, hollow=0.0):
    """Round cable, hose or tube swept along a routed polyline with filleted bends."""
    path = _path(points, radius)
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    prof = Circle(d / 2)
    if hollow:
        try:
            out = sweep(pl * (Circle(d / 2) - Circle(d / 2 - hollow)), path=path)
            if out.is_valid:
                return out
        except Exception:  # noqa: BLE001
            pass
    try:
        out = sweep(pl * prof, path=path, transition=__import__("build123d").Transition.ROUND)
        if out.is_valid:
            return out
    except Exception:  # noqa: BLE001
        pass
    # last resort: straight segments joined by spheres
    from build123d import Sphere
    out = None
    for a, b in zip(points, points[1:]):
        L = math.dist(a, b)
        if L < 1e-3:
            continue
        seg = Plane(origin=a, z_dir=tuple((bb - aa) / L for aa, bb in zip(a, b))).location * Cylinder(
            d / 2, L, align=BASE)
        out = seg if out is None else out + seg
    for p in points[1:-1]:
        out = out + Sphere(d / 2).moved(Location(p))
    return out


def sleeve_bands(points, d, every=120.0, width=10.0, grow=1.2):
    """Tape or clip bands round a routed bundle at intervals (marks a sleeved loom)."""
    path = _path(points, 40.0)
    L = path.length
    out = None
    n = max(1, int(L // every))
    for k in range(1, n + 1):
        t = min(0.98, k * every / L)
        p, tng = path.position_at(t), path.tangent_at(t)
        band = Plane(origin=p, z_dir=tng).location * Cylinder(d / 2 + grow, width)
        out = band if out is None else out + band
    return out


def eye_terminal(d_hole, t=1.2, w=12.0, L=22.0):
    """Ring terminal: flat eye with a crimp barrel, eye centre at the origin in XY, barrel along +X."""
    eye = zc(w / 2, 0, t) + box(0, L * 0.6, -w * 0.35, w * 0.35, 0, t)
    eye = eye - zc(d_hole / 2, -1, t + 1)
    barrel = xc(w * 0.28, L * 0.5, L, 0, w * 0.28)
    return eye + barrel


def lens_dome(r, h, z0=0.0, n=8):
    """Shallow domed lens about Z: a spherical cap approximated by a revolved arc."""
    R = (r * r + h * h) / (2 * h)
    prof = [(0, z0)]
    for k in range(n + 1):
        a = math.asin(min(1.0, r / R)) * (1 - k / n)
        prof.append((R * math.sin(a), z0 + h - (R - R * math.cos(a))))
    prof.append((0, z0 + h))
    # profile: centre bottom, rim, round to the top
    pts = [(0, z0), (r, z0)] + [(R * math.sin(math.asin(min(1.0, r / R)) * (1 - k / n)),
                                 z0 + (R * math.cos(math.asin(min(1.0, r / R)) * (1 - k / n)) - (R - h)))
                                for k in range(1, n)] + [(0, z0 + h)]
    return rev(pts)


def placed(loc, part):
    return loc * part
