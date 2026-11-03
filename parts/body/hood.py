"""Hood (soft top), shown up (Haynes Ch 12 Sec 1: the open two-seater; height with the hood up 49.4 in, mgexp.com): the
cover from the windscreen's top rail back over the cockpit to the rear deck, its rear window, and the frame's three
bows and side rails under it. The early cars' hood is the detachable 'build-up' type: its frame comes apart and
stows with the cover in the boot, so this assembly is the hood as erected. Shape derived (D) from the published
height and the screen, door glass and rear deck datums, and from Oliver's photos 15, 18, 25 and 27 (black hood, flat
top with tight corners, a wide rear window low in the back); hide body.hood in the Parts tree to see the cockpit.
"""
from __future__ import annotations

import math

from build123d import Compound, Face, thicken

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


def half_width(u, h):
    """Half-width of the hood at u, from the door glass tops at the sides to the rounded crown."""
    w0 = 600.0 - 20.0 * u                     # Oliver's photos 15, 18, 27: nearly the cockpit's width all the way back
    return w0 if u < 0.86 else w0 - (u - 0.86) / 0.14 * 30.0


def hood_pt(u, v):
    """Cover point: u along the car (screen to deck), v across (-1 right side bottom .. +1 left side bottom)."""
    x_front = S.screen_top(0.0)[0] - 18.0
    xs = [x_front, REAR_X]
    side = 1.0 if v >= 0 else -1.0
    a = abs(v)
    hc = crown(u)
    hb = SIDE_H if u < 0.75 else SIDE_H - (SIDE_H - REAR_H) * ((u - 0.75) / 0.25) ** 1.2
    hb = min(hb, hc - 20.0)
    w = half_width(u, hc)
    # rounded section: elliptical across the top, steepening to the sides
    t = v * math.pi / 2
    y = w * math.sin(t)
    h = hb + (hc - hb) * max(math.cos(t), 0.0) ** 0.26          # flat top, tight corners (photos 15, 18)
    sweep = S.SCREEN_TOP_SWEEP * (y / S.SCREEN_HALF_W) ** 2 * (1 - u)
    x = x_front + (REAR_X - x_front) * u - sweep
    return (x, y, H(h))


def cover(spec):
    """Hood cover: hood material from the top rail's fastener brackets back over the cockpit to the rear deck,
    sitting on the door glass tops at the sides."""
    from mgb import body_shell as B
    rows = [[hood_pt(0.02 + 0.97 * i / 24, -0.985 + 1.97 * j / 20) for j in range(21)] for i in range(25)]
    f = B._fit(rows, 0.3)
    for t in (2.5, -2.5, 2.0, -2.0):
        try:
            th = thicken(f, t)
            if th.is_valid:
                return _l(th, spec)
        except Exception:  # noqa: BLE001 - try the other side
            pass
    raise ValueError("hood cover offset failed")


def rear_window(spec):
    """Rear window: the clear panel sewn into the cover's back."""
    def out(p, d=3.5):                     # stand just proud of the cover (no coincident faces)
        x, y, z = p
        zc = H(980.0)
        L = math.hypot(y, z - zc) or 1.0
        return (x - d * 0.35, y + d * y / L, z + d * (z - zc) / L)
    rows = [[out(hood_pt(0.70 + 0.15 * i / 6, -0.62 + 1.24 * j / 8)) for j in range(9)] for i in range(7)]
    f = Face.make_surface_from_array_of_points(rows, tol=0.1, min_deg=1, max_deg=3)
    return _l(thicken(f, 1.5), spec)


BOW_U = (0.28, 0.52, 0.76)


def bow(k):
    def build(spec):
        """Hood frame bow: a steel tube following the cover inside it, its feet in the side rails."""
        u = BOW_U[k]
        pts = [hood_pt(u, -1.0 + 2.0 * j / 10) for j in range(11)]
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
