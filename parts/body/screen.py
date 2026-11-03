"""Windscreen (Haynes Ch 12 Sec 18, Figs 12.7-12.9, printed p224-225): the curved glass in its glazing rubber, the RH
and LH pillars with their feet bolted through the scuttle sides, the top rail, the bottom rail on the scuttle, the
centre rod and its brackets, and the interior mirror on the top rail. Geometry from mgb.body_shell_layout (screen_*).
"""
from __future__ import annotations

import math

from build123d import Compound, Face, Location, thicken

from mgb import body_geom as G, body_shell_layout as S
from mgb.chassis_geom import box, rod, swept_rod, xcyl, zcyl

H = S.z_of
GLASS_T = 6.0                               # laminated screen (D)
W = S.SCREEN_HALF_W - 22.0                  # glass edge inside the pillars


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
        rows.append([S.screen_pt(y, 0.03 + 0.94 * j / 8) for j in range(9)])
    f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
    g = thicken(f, GLASS_T)
    return _l(g, spec)


def _edge(v, ys, off=0.0):
    return [tuple(a + b for a, b in zip(S.screen_pt(y, v), (0.0, 0.0, off))) for y in ys]


def top_rail(spec):
    """Top rail (Fig 12.7 item 4): chrome channel over the glass's top edge from pillar to pillar, the hood's front
    fastener brackets (6) underneath."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    r = swept_rod(_edge(1.0, ys, 6.0), 11.0)
    brackets = [box(S.screen_top(y)[0] - 30.0, S.screen_top(y)[0] - 10.0, y - 20.0, y + 20.0, H(S.screen_top(y)[1]) - 6.0,
                    H(S.screen_top(y)[1]) + 2.0) for y in (-330.0, 330.0)]
    return _c([r] + brackets, spec)


def bottom_rail(spec):
    """Bottom rail (Fig 12.7 item 5) on the scuttle under the glass, its seal (18)."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    return _l(swept_rod(_edge(0.0, ys, 2.0), 9.0), spec)


def pillar(side):
    def build(spec):
        """Screen pillar (Fig 12.7 items 2, 3): the chrome side post along the glass's edge, its foot down through the
        scuttle side to the reinforcement plate (16, 17) and the packing (12, 13)."""
        y = side * S.SCREEN_HALF_W
        pts = [S.screen_pt(y, v) for v in (0.0, 0.35, 0.7, 1.0)]
        post = swept_rod(pts, 12.0)
        bx, bh = S.screen_base(y)
        foot = box(bx - 50.0, bx + 30.0, y - 16.0, y + 16.0, H(bh) - 70.0, H(bh))
        plate = box(bx - 55.0, bx + 35.0, y - 22.0, y + 22.0, H(bh) - 76.0, H(bh) - 72.0)
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
    "body.glass.pillar-l": {"build": pillar(1)},
    "body.glass.pillar-r": {"build": pillar(-1)},
    "body.glass.centre-rod": {"build": centre_rod},
    "body.glass.mirror": {"build": mirror},
}
