"""Gear, spline and dog-tooth solids for the gearbox (and later the overdrive and axle).

All built along +Z from z = 0, centred on the Z axis, in standalone (algebra) mode.

Tooth form: a 20 degree involute flank sampled at a few points between the base (or root)
circle and the tip, joined by straight segments; root and tip are short arcs of straight
segments. That gives a true-looking tooth with planar faces on spur gears, which mesh
cheaply. Helical gears twist the same section along the axis by the lead angle
(Solid.extrude_linear_with_rotation), right or left hand.

Sizes are module based (mm). Transverse module mt = mn / cos(beta) for a helical gear.
"""
from __future__ import annotations

import math

from build123d import Align, Compound, Cylinder, Face, Location, Part, Plane, Polygon, Solid, Wire, extrude

PA = math.radians(20.0)
BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def _inv(a):
    return math.tan(a) - a


def tooth_outline(n: int, mt: float, add: float = 1.0, ded: float = 1.25, flank_pts: int = 4,
                  root_pts: int = 2, shift: float = 0.0) -> list[tuple[float, float]]:
    """Closed 2D outline of an n-tooth involute gear, transverse module mt (mm).

    add/ded are the addendum and dedendum in modules; shift raises the tip and root
    (modules) on small pinions (the 11-tooth laygear first gear) so the root does not
    undercut; the tooth thickness stays standard, so gears mesh at the standard centres.
    """
    rp = n * mt / 2
    rb = rp * math.cos(PA)
    ra = rp + (add + shift) * mt
    rf = max(rp - (ded - shift) * mt, 0.5 * rp)
    # half tooth thickness angle at the pitch circle, plus the involute function there
    half = math.pi / (2 * n)
    pts = []
    r0 = max(rb, rf)
    for k in range(n):
        c = 2 * math.pi * k / n
        flank = []
        for i in range(flank_pts + 1):
            r = r0 + (ra - r0) * i / flank_pts
            a = math.acos(min(1.0, rb / r))
            th = half + _inv(PA) - _inv(a)              # angle of the flank point from the tooth centre
            flank.append((r, th))
        # root: from the previous gap centre to the flank foot
        gap = math.pi / n
        right = [(r, c - th) for r, th in flank]        # rising flank on the -angle side
        left = [(r, c + th) for r, th in reversed(flank)]
        foot = right[0][1]
        for j in range(root_pts):
            t = c - gap + (foot - (c - gap)) * j / root_pts
            pts.append((rf, t))
        if r0 > rf + 1e-6:
            pts.append((rf, foot))
        pts += right
        pts += left
        if r0 > rf + 1e-6:
            pts.append((rf, left[-1][1]))
    return [(r * math.cos(t), r * math.sin(t)) for r, t in pts]


def _section(pts):
    return Face(Wire.make_polygon([(x, y, 0) for x, y in pts], close=True))


def spur(n: int, m: float, width: float, bore: float = 0.0, **kw) -> Part:
    g = extrude(_section(tooth_outline(n, m, **kw)), width)
    if bore:
        g = g - Cylinder(bore / 2, width + 2, align=BASE).moved(Location((0, 0, -1)))
    return g


def helical(n: int, mn: float, beta_deg: float, width: float, hand: str = "right", bore: float = 0.0,
            **kw) -> Part:
    """Helical gear, normal module mn, helix angle beta, with an optional bore radius (made
    as an inner wire, so no boolean touches the twisted faces). Right hand: the teeth twist
    clockwise looking along +Z (away from the viewer)."""
    beta = math.radians(beta_deg)
    mt = mn / math.cos(beta)
    rp = n * mt / 2
    twist = math.degrees(width * math.tan(beta) / rp) * (-1 if hand == "right" else 1)
    outer = Wire.make_polygon([(x, y, 0) for x, y in tooth_outline(n, mt, **kw)], close=True)
    inner = [Wire.make_circle(bore)] if bore else None
    if inner:
        return Solid.extrude_linear_with_rotation(outer, (0, 0, 0), (0, 0, width), twist, inner_wires=inner)
    return Solid.extrude_linear_with_rotation(_section(tooth_outline(n, mt, **kw)), (0, 0, 0), (0, 0, width), twist)


def glue(a: Part, *others: Part) -> Part:
    """Fuse solids that only touch (shared faces, no overlap) in OCCT's fast glue mode; falls
    back to an ordinary fuse if the glued result is not valid."""
    out = a
    for b in others:
        n = len(out.solids()) + len(b.solids()) - 1
        g = out.fuse(b, glue=True)
        out = g if g.is_valid and len(g.solids()) <= max(n, 1) else out.fuse(b)
    good = [s for s in out.solids() if abs(s.volume) > 1e-3]
    if len(good) < len(out.solids()):                     # drop slivers left by the fuse
        out = good[0] if len(good) == 1 else Part(Compound(good))
    return out


def pitch_radius(n, mn, beta_deg=0.0):
    return n * mn / math.cos(math.radians(beta_deg)) / 2


def spline_outline(n: int, r_major: float, r_minor: float, land: float = 0.5) -> list[tuple[float, float]]:
    """Straight-sided spline: n keys, each keeps a fraction `land` of the pitch at the major
    diameter. Returned as a closed outline (external spline; subtract it for a hub)."""
    pts = []
    for k in range(n):
        c = 2 * math.pi * k / n
        p = 2 * math.pi / n
        w = land * p * r_major / 2                     # half width of the key (mm)
        a_o = w / r_major
        a_i = min(w / r_minor, 0.49 * p)
        pts += [(r_minor, c - p / 2 + 1e-3), (r_minor, c - a_i), (r_major, c - a_o), (r_major, c + a_o),
                (r_minor, c + a_i)]
    return [(r * math.cos(t), r * math.sin(t)) for r, t in pts]


def spline_shaft(n: int, d_major: float, d_minor: float, length: float, land: float = 0.5) -> Part:
    return extrude(_section(spline_outline(n, d_major / 2, d_minor / 2, land)), length)


def spline_bore(n: int, d_major: float, d_minor: float, length: float, land: float = 0.5) -> Part:
    """Cutter for an internally splined hub (subtract it): keyways cut out to the major
    diameter, the bore at the minor diameter."""
    return spline_shaft(n, d_major + 0.2, d_minor + 0.2, length + 2, land=1.0 - land + 0.02).moved(
        Location((0, 0, -1)))


def dog_ring(n: int, r_out: float, r_in: float, depth: float, fill: float = 0.5) -> Part:
    """Ring of n short straight dog teeth (as on the gear's synchro cone shoulder)."""
    return extrude(_section(spline_outline(n, r_out, r_in, land=fill)), depth)


def cone(r0: float, r1: float, length: float, bore: float) -> Part:
    """Synchro cone from radius r0 at z = 0 to r1 at z = length, with a bore."""
    from mgb.shapes import revolved
    return revolved([(bore / 2, 0), (r0, 0), (r1, length), (bore / 2, length)])
