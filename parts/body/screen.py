"""Windscreen (Haynes Ch 12 Sec 18, Figs 12.7-12.9, printed p224-225): the curved glass in its glazing rubber, the RH
and LH pillars with their feet bolted through the scuttle sides, the top rail, the bottom rail on the scuttle, the
centre rod and its brackets, and the interior mirror on the top rail. Geometry from mgb.body_shell_layout (screen_*).
"""
from __future__ import annotations

import math

from build123d import Compound, Face, Location, Solid, Vector, Wire, thicken

from mgb import body_geom as G, body_shell_layout as S
from mgb.chassis_geom import box, rod, swept_rod, xcyl, zcyl

H = S.z_of
GLASS_T = 6.0                               # laminated screen (D)
W = S.SCREEN_HALF_W - 9.0                   # glass edge inside the pillars' channels (no light past it)


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


def glass(spec):
    """Windscreen glass (Fig 12.7 item 14): curved in plan, raked, its corners rounded, in the glazing rubber (15)."""
    rows = []
    for k in range(13):
        y = -W + 2 * W * k / 12
        rows.append([S.screen_pt(y, 0.006 + 0.988 * j / 8) for j in range(9)])
    f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
    g = thicken(f, GLASS_T)
    return _l(g, spec)


def _edge(v, ys, off=0.0):
    return [tuple(a + b for a, b in zip(S.screen_pt(y, v), (0.0, 0.0, off))) for y in ys]


def _channel(path, across, w_in, w_out, t, r=3.5):
    """Chrome frame section swept along path (car points): a flat channel w_in over the glass edge and w_out beyond it
    (across(point) gives the in-plane direction away from the glass), t thick normal to the glass, its corners
    rounded r (Oliver's photos 09, 27: the frame is a flat chrome band about 30 mm wide round the glass)."""
    wires = []
    for i, p in enumerate(path):
        q0, q1 = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        tng = Vector(*q1) - Vector(*q0)
        tng = tng.normalized()
        a = Vector(*across(p))
        a = (a - tng * a.dot(tng)).normalized()
        n = tng.cross(a).normalized()
        sec = []
        for (ca, cb, a0) in ((w_out - r, t / 2 - r, 0.0), (-w_in + r, t / 2 - r, 90.0), (-w_in + r, -t / 2 + r, 180.0),
                             (w_out - r, -t / 2 + r, 270.0)):
            for k in range(4):
                ang = math.radians(a0 + 90.0 * k / 3)
                sec.append(Vector(*p) + a * (ca + r * math.cos(ang)) + n * (cb + r * math.sin(ang)))
        wires.append(Wire.make_polygon(sec, close=True))
    return Solid.make_loft(wires, ruled=False)


def _up(y):
    (xb, hb), (xt, ht) = S.screen_base(y), S.screen_top(y)
    return (xt - xb, 0.0, ht - hb)


def top_rail(spec):
    """Top rail (Fig 12.7 item 4): flat chrome channel over the glass's top edge from pillar to pillar (about 26 mm
    deep, Oliver's photos 09, 27), the hood's front fastener brackets (6) underneath."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    r = _channel(_edge(1.0, ys), lambda p: _up(p[1]), 12.0, 16.0, 13.0)
    brackets = [box(S.screen_top(y)[0] - 30.0, S.screen_top(y)[0] - 10.0, y - 20.0, y + 20.0, H(S.screen_top(y)[1]) - 6.0,
                    H(S.screen_top(y)[1]) + 2.0) for y in (-330.0, 330.0)]
    return _c([r] + brackets, spec)


def bottom_rail(spec):
    """Bottom rail (Fig 12.7 item 5) on the scuttle under the glass, its seal (18) closing it to the scuttle."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    rail = _channel(_edge(0.0, ys), lambda p: tuple(-c for c in _up(p[1])), 12.0, 10.0, 12.0)
    return _c([rail], spec)


def bottom_seal(spec):
    """Bottom rail's seal (Fig 12.7 item 18): the black rubber strip closing the rail to the scuttle, standing out
    below the chrome all along the screen's foot (Oliver's photos 09, 15, 27 and scan)."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    pts = []
    for (x, y, z) in _edge(0.0, ys):                 # a bead on the scuttle along the rail's front foot
        xs = x + 13.0
        pts.append((xs, y, S.z_of(S.top_h(xs, y)) + 3.0))
    return _c([swept_rod(pts, 9.0)], spec)


def pillar(side):
    def build(spec):
        """Screen pillar (Fig 12.7 items 2, 3): the flat chrome side post along the glass's edge (about 32 mm across,
        Oliver's photos 09, 15, 27), its foot down through the scuttle side to the reinforcement plate (16, 17) and
        the packing (12, 13)."""
        y = side * S.SCREEN_HALF_W
        pts = [S.screen_pt(y, v) for v in (-0.02, 0.25, 0.5, 0.75, 1.03)]
        post = _channel(pts, lambda p: (0.0, side * 1.0, 0.0), 12.0, 20.0, 14.0)
        bx, bh = S.screen_base(y)
        foot = box(bx - 8.0, bx + 60.0, y - 16.0, y + 16.0, H(bh) - 70.0, H(bh))      # under the scuttle, ahead of the door
        plate = box(bx - 12.0, bx + 65.0, y - 22.0, y + 22.0, H(bh) - 76.0, H(bh) - 72.0)
        return _c([post, foot, plate], spec)
    return build


def centre_rod(spec):
    """Centre rod (Fig 12.7 item 9) from the scuttle bracket (12) to the top rail's centre bracket, nut (10)."""
    a = S.screen_pt(0.0, 0.0)
    b = S.screen_pt(0.0, 1.0)
    a2 = (a[0] - 24.0, 0.0, a[2] + 4.0)
    b2 = (b[0] - 22.0, 0.0, b[2] - 8.0)
    r = rod(a2, b2, 4.0)
    lower = box(a2[0] - 16.0, a2[0] + 16.0, -12.0, 12.0, a2[2] - 6.0, a2[2] + 4.0)
    upper = box(b2[0] - 12.0, b2[0] + 12.0, -12.0, 12.0, b2[2] - 4.0, b2[2] + 8.0)
    return _c([r, lower, upper], spec)


def mirror(spec):
    """Interior mirror on a stem from the top rail's centre."""
    tx, th = S.screen_top(0.0)
    z = H(th)
    stem = rod((tx - 15.0, 0.0, z - 4.0), (tx - 60.0, 0.0, z - 55.0), 5.0)
    head = box(tx - 75.0, tx - 60.0, -95.0, 95.0, z - 95.0, z - 40.0)
    glass_ = box(tx - 76.0, tx - 75.0, -88.0, 88.0, z - 90.0, z - 45.0)
    return _c([stem, head, glass_], spec)


PARTS = {
    "body.glass.windscreen": {"build": glass},
    "body.glass.top-rail": {"build": top_rail},
    "body.glass.bottom-rail": {"build": bottom_rail},
    "body.glass.bottom-seal": {"build": bottom_seal},
    "body.glass.pillar-l": {"build": pillar(1)},
    "body.glass.pillar-r": {"build": pillar(-1)},
    "body.glass.centre-rod": {"build": centre_rod},
    "body.glass.mirror": {"build": mirror},
}
