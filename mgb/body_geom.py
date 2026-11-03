"""Sheet-metal helpers for the body (P11b): pressings drawn as thin bands along a profile and extruded, flanged
plates, beads and holes. Standalone (algebra) mode in the car frame."""
from __future__ import annotations

import math

from build123d import Compound, Face, Location, Plane, Polygon, Rot, Wire, extrude

from mgb.chassis_geom import box, xcyl, xprism, ycyl, yprism, zcyl, zprism
from mgb.poly2d import ccw


def offset_open(pts, d):
    """Open polyline offset by d to its left (mitred, limited)."""
    out = []
    n = len(pts)
    for k in range(n):
        if k == 0:
            a, b = pts[0], pts[1]
            nx, ny = -(b[1] - a[1]), b[0] - a[0]
            L = math.hypot(nx, ny)
            out.append((pts[0][0] + nx / L * d, pts[0][1] + ny / L * d))
            continue
        if k == n - 1:
            a, b = pts[-2], pts[-1]
            nx, ny = -(b[1] - a[1]), b[0] - a[0]
            L = math.hypot(nx, ny)
            out.append((pts[-1][0] + nx / L * d, pts[-1][1] + ny / L * d))
            continue
        a, b, c = pts[k - 1], pts[k], pts[k + 1]
        n1 = (-(b[1] - a[1]), b[0] - a[0])
        n2 = (-(c[1] - b[1]), c[0] - b[0])
        l1, l2 = math.hypot(*n1), math.hypot(*n2)
        n1 = (n1[0] / l1, n1[1] / l1)
        n2 = (n2[0] / l2, n2[1] / l2)
        m = (n1[0] + n2[0], n1[1] + n2[1])
        lm = math.hypot(*m) or 1.0
        m = (m[0] / lm, m[1] / lm)
        cosh = max(m[0] * n1[0] + m[1] * n1[1], 0.35)
        out.append((b[0] + m[0] * d / cosh, b[1] + m[1] * d / cosh))
    return out


def band(pts, t):
    """Closed thin polygon along an open polyline, thickness t to its left."""
    return list(pts) + list(reversed(offset_open(pts, t)))


def round_path(pts, r, n=4):
    """Open polyline with its inner corners rounded (radius r). Every corner gives n + 1 points, so paths with the
    same vertex count stay loftable."""
    if len(pts) < 3 or r <= 0:
        return list(pts)
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        a, b, c = pts[k - 1], pts[k], pts[k + 1]
        u1 = (a[0] - b[0], a[1] - b[1])
        u2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*u1), math.hypot(*u2)
        u1, u2 = (u1[0] / max(l1, 1e-9), u1[1] / max(l1, 1e-9)), (u2[0] / max(l2, 1e-9), u2[1] / max(l2, 1e-9))
        cosang = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
        half = math.acos(cosang) / 2
        if half < 1e-3 or abs(half - math.pi / 2) < 1e-2 or l1 < 1e-6 or l2 < 1e-6:
            d = min(0.5, 0.2 * l1, 0.2 * l2)
            for j in range(n + 1):           # straight through: points along the line either side of b
                tt = -d + 2 * d * j / n
                out.append((b[0] - u1[0] * tt if tt < 0 else b[0] + u2[0] * tt,
                            b[1] - u1[1] * tt if tt < 0 else b[1] + u2[1] * tt))
            continue
        d = min(r / math.tan(half), 0.45 * l1, 0.45 * l2)
        rr = d * math.tan(half)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        lb = math.hypot(*bis)
        cen = (b[0] + bis[0] / lb * rr / math.sin(half), b[1] + bis[1] / lb * rr / math.sin(half))
        t1 = (b[0] + u1[0] * d, b[1] + u1[1] * d)
        t2 = (b[0] + u2[0] * d, b[1] + u2[1] * d)
        a1 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        a2 = math.atan2(t2[1] - cen[1], t2[0] - cen[0])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for j in range(n + 1):
            tt = a1 + da * j / n
            out.append((cen[0] + rr * math.cos(tt), cen[1] + rr * math.sin(tt)))
    out.append(pts[-1])
    return out


def sheet_x(pts_yz, t, x0, x1, r=6.0):
    """Pressing whose section (y, z) runs along x from x0 to x1."""
    return xprism(band(round_path(pts_yz, r), t), min(x0, x1), max(x0, x1))


def sheet_y(pts_xz, t, y0, y1, r=6.0):
    return yprism(band(round_path(pts_xz, r), t), min(y0, y1), max(y0, y1))


def sheet_z(pts_xy, t, z0, z1, r=6.0):
    return zprism(band(round_path(pts_xy, r), t), min(z0, z1), max(z0, z1))


def plate_x(outline_yz, x0, t):
    """Flat plate in a y-z plane from x0 to x0 + t (t may be negative)."""
    return xprism(outline_yz, min(x0, x0 + t), max(x0, x0 + t))


def plate_y(outline_xz, y0, t):
    return yprism(outline_xz, min(y0, y0 + t), max(y0, y0 + t))


def plate_z(outline_xy, z0, t):
    return zprism(outline_xy, min(z0, z0 + t), max(z0, z0 + t))


def rect(a0, a1, b0, b1):
    return [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]


def rounded_rect(a0, a1, b0, b1, r, n=4):
    from mgb.body_shell import fillet_poly
    return fillet_poly(rect(a0, a1, b0, b1), r, n)


def obround(ca, cb, length, width, n=8):
    """Slot outline centred (ca, cb), long along the first axis."""
    r = width / 2
    h = length / 2 - r
    pts = []
    for k in range(n + 1):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((ca + h + r * math.cos(a), cb + r * math.sin(a)))
    for k in range(n + 1):
        a = math.pi / 2 + math.pi * k / n
        pts.append((ca - h + r * math.cos(a), cb + r * math.sin(a)))
    return pts


def solids(parts):
    out = []
    for p in parts:
        if p is None:
            continue
        out.extend(p.solids())
    return out


def compound(parts, label=None):
    c = Compound(solids(parts))
    if label:
        c.label = label
    return c


def fuse(parts):
    """Union a list of solids (small parts only)."""
    out = None
    for p in parts:
        out = p if out is None else out + p
    return out
