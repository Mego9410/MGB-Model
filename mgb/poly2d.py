"""Small 2D polygon helpers (no external geometry library): convex hull, offsets of convex
polygons, points along a perimeter, and radial resampling for lofts."""
from __future__ import annotations

import math


def area(poly):
    return 0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))


def ccw(poly):
    return list(poly) if area(poly) > 0 else list(reversed(poly))


def circle_pts(cx, cy, r, n=24, a0=0.0, a1=360.0):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n)]


def hull(points):
    """Convex hull (monotone chain), counter-clockwise."""
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def inset(poly, d):
    """Convex polygon moved inward by d (mitred corners); negative d grows it (mitred)."""
    p = ccw(poly)
    n = len(p)
    lines = []
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey)
        if L < 1e-9:
            continue
        nx, ny = -ey / L, ex / L                      # inward normal for a ccw polygon
        lines.append(((a[0] + nx * d, a[1] + ny * d), (ex / L, ey / L)))
    out = []
    for i in range(len(lines)):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(p2)
            continue
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + t * d1[0], p1[1] + t * d1[1]))
    return dedupe(out)


def grow(poly, d, arc_pts=4):
    """Convex polygon grown outward by d with rounded corners."""
    p = ccw(poly)
    n = len(p)
    out = []
    for i in range(n):
        a, b, c = p[i - 1], p[i], p[(i + 1) % n]
        n1 = _onorm(a, b)
        n2 = _onorm(b, c)
        a1, a2 = math.atan2(n1[1], n1[0]), math.atan2(n2[1], n2[0])
        while a2 < a1:
            a2 += 2 * math.pi
        if a2 - a1 > 2 * math.pi - 1e-9:
            a2 -= 2 * math.pi
        for k in range(arc_pts + 1):
            t = a1 + (a2 - a1) * k / arc_pts
            out.append((b[0] + d * math.cos(t), b[1] + d * math.sin(t)))
    return dedupe(out)


def dedupe(pts, tol=1e-3):
    """Drop points closer than tol to the previous one (and a closing duplicate)."""
    out = []
    for p in pts:
        if not out or math.dist(p, out[-1]) > tol:
            out.append(p)
    while len(out) > 2 and math.dist(out[0], out[-1]) <= tol:
        out.pop()
    return out


def rounded(poly, r, arc_pts=4):
    """Convex polygon with its corners rounded to radius r (same overall size)."""
    return grow(inset(poly, r), r, arc_pts)


def _onorm(a, b):
    ex, ey = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ex, ey)
    return (ey / L, -ex / L)                           # outward normal for ccw


def along(poly, fracs):
    """Points at fractions of the perimeter of a closed polygon."""
    segs = list(zip(poly, poly[1:] + poly[:1]))
    lens = [math.dist(a, b) for a, b in segs]
    tot = sum(lens)
    out = []
    for f in fracs:
        s = (f % 1.0) * tot
        for (a, b), L in zip(segs, lens):
            if s <= L + 1e-9:
                t = s / L if L else 0.0
                out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
                break
            s -= L
    return out


def radial(poly, n=72, c=(0.0, 0.0)):
    """n points on a convex polygon by rays from c at equal angles (for lofting sections)."""
    p = ccw(poly)
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        dx, dy = math.cos(a), math.sin(a)
        best = None
        for i in range(len(p)):
            x1, y1 = p[i]
            x2, y2 = p[(i + 1) % len(p)]
            ex, ey = x2 - x1, y2 - y1
            den = dx * ey - dy * ex
            if abs(den) < 1e-12:
                continue
            t = ((x1 - c[0]) * ey - (y1 - c[1]) * ex) / den
            s = ((x1 - c[0]) * dy - (y1 - c[1]) * dx) / den
            if t > 0 and -1e-9 <= s <= 1 + 1e-9 and (best is None or t > best):
                best = t
        out.append((c[0] + best * dx, c[1] + best * dy))
    return out


def clip_top(poly, xmax):
    """Clip a convex polygon to x <= xmax (Sutherland-Hodgman against one edge)."""
    out = []
    p = ccw(poly)
    for i in range(len(p)):
        a, b = p[i - 1], p[i]
        ina, inb = a[0] <= xmax, b[0] <= xmax
        if inb:
            if not ina:
                t = (xmax - a[0]) / (b[0] - a[0])
                out.append((xmax, a[1] + t * (b[1] - a[1])))
            out.append(b)
        elif ina:
            t = (xmax - a[0]) / (b[0] - a[0])
            out.append((xmax, a[1] + t * (b[1] - a[1])))
    return out
