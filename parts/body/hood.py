"""Hood (soft top), shown up (Haynes Ch 12 Sec 1: the open two-seater; height with the hood up 49.4 in, mgexp.com): the
cover from the windscreen's top rail back over the cockpit to the rear deck, its rear window, and the frame's three
bows and side rails under it. The early cars' hood is the detachable 'build-up' type: its frame comes apart and
stows with the cover in the boot, so this assembly is the hood as erected. Shape derived (D) from the published
height and the screen, door glass and rear deck datums, and from Oliver's photos 15, 18, 25 and 27 (black hood, flat
top with tight corners, a wide rear window low in the back); hide body.hood in the Parts tree to see the cockpit.
"""
from __future__ import annotations

import math

from build123d import Compound, Face, Plane, RectangleRounded, Vector, extrude, thicken

from mgb import body_geom as G, body_shell_layout as S, car_layout as CL
from mgb.chassis_geom import rod, swept_rod
from parts.body import closures as C

H = S.z_of
TOP_H = CL.HEIGHT_HOOD_UP - 2.5            # crown's underside: the published hood-up height (S) less the cover
REAR_X = S.COCKPIT_REAR_X + 15.0
REAR_H = 868.0
SIDE_H = C.GLASS_TOP_H - 6.0


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


def crown(u):
    """Height of the hood's crown at u (0 at the screen top rail, 1 at the rear deck): up from the top rail, nearly
    level over the seats, then down in a long curve behind them to the deck."""
    hs = S.SCREEN_TOP_H + 10.0
    if u < 0.16:
        return hs + (TOP_H - hs) * math.sin(math.pi / 2 * u / 0.16)
    if u < 0.52:
        return TOP_H
    t = (u - 0.52) / 0.48
    return TOP_H - (TOP_H - REAR_H) * (t ** 1.6)


SWEEP_SIDE = 1.15                             # (y / SCREEN_HALF_W)^2 at the hood's sides, for the sweep at its edge


def _edge_x(u):
    """x of the cover's lower edge at u (the screen top's sweep carried back and dying out at the rear)."""
    x_front = S.screen_top(0.0)[0] - 18.0
    return x_front + (REAR_X - x_front) * u - S.SCREEN_TOP_SWEEP * SWEEP_SIDE * (1 - u)


def _edge(x):
    """(|y|, height) of the cover's lower edge at x: over the screen pillar's top and the quarter-light frame at the
    front, then along the door glass's top and raked rear edge (the glass runs up 8 mm inside it), then down on the
    body's top along the cockpit edge behind the door to the rear deck (Oliver's photos 09, 15, 18, 27: no light
    between the hood and the glass or the body)."""
    xq0 = C.ql_outline()[3][0]                      # quarter-light top front corner
    xf = C.QL_POST_X - 4.0                          # door glass front edge
    xr = C.GLASS_REAR_X                             # door glass rear edge (at the door's rear shut line)
    if x >= xq0:
        return C.QL_FRONT_Y + 1.0, C.QL_TOP_H + 9.0
    if x >= xf:
        t = (xq0 - x) / (xq0 - xf)
        h = C.QL_TOP_H + 9.0 + (C.GLASS_TOP_H - 8.0 - C.QL_TOP_H - 9.0) * t
        return C.ql_y(x, h) + 8.0, h
    if x >= xr:
        h = C.glass_top_h(x) - 8.0
        return C._glass_ys(h) + 8.0, h
    # behind the door glass: on the body's top just outside the cockpit opening, to the rear corners
    y0 = C._glass_ys(C.glass_top_h(xr) - 8.0) + 8.0
    yw = _interp_y(x)
    t = min(1.0, (xr - x) / 40.0)
    y = y0 + (yw - y0) * t
    return y, S.top_h(x, y) + 3.0


def _interp_y(x):
    tab = [(-1609.0, 690.0), (-1660.0, 678.0), (-1750.0, 664.0), (-1850.0, 636.0), (REAR_X, 596.0)]
    if x >= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x1 <= x <= x0:
            return y0 + (y1 - y0) * (x0 - x) / (x0 - x1)
    return tab[-1][1]


def half_width(u, h=None):
    """Half-width of the hood at u: its lower edge's |y| (the sides drop vertically to it)."""
    return _edge(_edge_x(u))[0]


# Across the cover: v (-1 right side bottom .. +1 left side bottom); the samples crowd toward the edges, where the
# section turns down into the vertical sides.
_C_SIDE = (0.87, 0.75, 0.6, 0.45, 0.3, 0.15, 0.0)
_T = sorted({round(v, 6) for v in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]} |
            {round(math.acos(c ** (1 / 0.26)) / (math.pi / 2), 6) for c in _C_SIDE})
V_SAMPLES = [-t for t in reversed(_T[1:])] + _T


def hood_pt(u, v):
    """Cover point: u along the car (screen to deck), v across (-1 right side bottom .. +1 left side bottom)."""
    x_front = S.screen_top(0.0)[0] - 18.0
    hc = crown(u)
    w, hb = _edge(_edge_x(u))
    hb = min(hb, hc - 20.0)
    t = v * math.pi / 2
    y = w * math.sin(t)
    h = hb + (hc - hb) * max(math.cos(t), 0.0) ** 0.26          # flat top, tight corners (photos 15, 18)
    sweep = S.SCREEN_TOP_SWEEP * (y / S.SCREEN_HALF_W) ** 2 * (1 - u)
    x = x_front + (REAR_X - x_front) * u - sweep
    if u > 0.9:                                                 # the back edge lies on the rear deck
        s = ((u - 0.9) / 0.1) ** 2
        h = h + (S.top_h(x, y) + 3.0 - h) * s
    return (x, y, H(h))


def cover(spec):
    """Hood cover: hood material from the top rail's fastener brackets back over the cockpit to the rear deck,
    sitting on the door glass tops at the sides, with the rear window's opening cut through its back."""
    from mgb import body_shell as B
    rows = [[hood_pt(0.005 + 0.995 * i / 96, v) for v in V_SAMPLES] for i in range(97)]
    f = B._fit(rows, 0.3)
    for t in (2.5, -2.5, 2.0, -2.0):
        try:
            th = thicken(f, t)
            if th.is_valid:
                cut = th - extrude(_window_plane() * RectangleRounded(WIN_W, WIN_L, WIN_R), amount=60.0, both=True)
                if cut.is_valid:
                    return _l(cut, spec)
        except Exception:  # noqa: BLE001 - try the other side
            pass
    raise ValueError("hood cover offset failed")


# Rear window: a flat clear rectangle with rounded corners low in the cover's back (Oliver's photos 18, 23: wide and
# shallow, nearly the width of the deck between the hood's side curves).
WIN_U = (0.69, 0.86)
WIN_V = 0.60
WIN_R = 28.0


def _window_plane():
    """Plane through the window's four corners on the cover: x across the car, y up the cover's back."""
    a, b = [Vector(*hood_pt(u, -WIN_V)) for u in WIN_U], [Vector(*hood_pt(u, WIN_V)) for u in WIN_U]
    o = (a[0] + a[1] + b[0] + b[1]) * 0.25
    xd = ((b[0] + b[1]) - (a[0] + a[1])).normalized()
    up = ((a[1] + b[1]) - (a[0] + b[0])).normalized()
    n = xd.cross(up).normalized()
    if n.Z < 0:
        n = -n
    return Plane(o, x_dir=xd, z_dir=n)


def _win_size():
    a0, a1 = Vector(*hood_pt(WIN_U[0], -WIN_V)), Vector(*hood_pt(WIN_U[1], -WIN_V))
    b0 = Vector(*hood_pt(WIN_U[0], WIN_V))
    return (b0 - a0).length, (a1 - a0).length


WIN_W, WIN_L = _win_size()


def rear_window(spec):
    """Rear window: a flat clear panel set into the opening in the cover's back."""
    pl = _window_plane()
    return _l(extrude(pl * RectangleRounded(WIN_W - 1.0, WIN_L - 1.0, WIN_R - 0.5), amount=1.6, both=True), spec)


BOW_U = (0.28, 0.50, 0.66)                   # the rear bow ahead of the rear window


def bow(k):
    def build(spec):
        """Hood frame bow: a steel tube following the cover inside it, its feet in the side rails."""
        u = BOW_U[k]
        pts = [hood_pt(u, -0.97 + 1.94 * j / 10) for j in range(11)]          # feet on the side rails, above the body
        pts = [(x, y * 0.985, z - 14.0) for x, y, z in pts]
        return _l(swept_rod(pts, 8.0), spec)
    return build


def side_rail(side):
    def build(spec):
        """Hood frame side rail along the cover's lower edge from the screen to the rear bow's foot."""
        pts = [hood_pt(u, side * 1.0) for u in (0.03, 0.3, 0.55, 0.78)]
        pts = [(x, y * 0.985, z + 6.0) for x, y, z in pts]
        return _l(swept_rod(pts, 6.0), spec)
    return build


PARTS = {
    "body.hood.cover": {"build": cover},
    "body.hood.rear-window": {"build": rear_window},
    "body.hood.bow-front": {"build": bow(0)},
    "body.hood.bow-middle": {"build": bow(1)},
    "body.hood.bow-rear": {"build": bow(2)},
    "body.hood.side-rail-l": {"build": side_rail(1)},
    "body.hood.side-rail-r": {"build": side_rail(-1)},
}
