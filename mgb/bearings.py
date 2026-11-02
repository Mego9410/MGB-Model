"""Rolling bearings drawn as one solid each (races and rolling elements fused), along +z from 0."""
from __future__ import annotations

import math

from build123d import Location, Part, Rot, Sphere

from mgb import shapes as Sh


def _ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def ball_bearing(bore, od, w, rows=1):
    """Deep groove ball bearing (or double row), inner and outer rings, balls between."""
    ri, ro = bore / 2, od / 2
    t = (ro - ri) * 0.3
    pc = (ri + ro) / 2
    rb = (ro - ri - 2 * t) / 2 + 0.25                  # balls just bite into both rings
    b = _ring(ri, ri + t, 0, w) + _ring(ro - t, ro, 0, w)
    zs = [w / 2] if rows == 1 else [w * 0.28, w * 0.72]
    if rows == 2:
        rb = min(rb, w * 0.24)
    n = max(8, int(2 * math.pi * pc / (2.25 * rb)))
    for i, z in enumerate(zs):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * i) / n
            b = b + Location((pc * math.cos(a), pc * math.sin(a), z)) * Sphere(rb)
    for z in zs:                                       # cage band
        b = b + _ring(pc - rb * 0.5, pc + rb * 0.5, z - 0.5, z + 0.5)
    return b


def taper_roller(bore, od, w, alpha=12.0):
    """Taper roller bearing: cone (inner race with ribs), rollers, cup. The large end of the
    rollers (the cone's back face) at z = 0, the small end toward +z."""
    ri, ro = bore / 2, od / 2
    a = math.radians(alpha)
    d0 = 0.30 * (ro - ri)
    d1 = 0.82 * d0
    za, zb = 0.14 * w, 0.84 * w
    rp0 = (ri + ro) / 2 + 0.06 * (ro - ri)

    def rp(z):
        return rp0 - (z - za) * math.tan(a)

    def dr(z):
        return d0 + (d1 - d0) * (z - za) / (zb - za)
    # cup: conical raceway (outer) - the cup is the full width, flush with the cone at the back
    cup = Sh.revolved([(rp(0) + dr(za) / 2 - 0.05, 0.0), (ro, 0.0), (ro, w), (rp(w) + dr(zb) / 2 - 0.05, w)])
    cone = Sh.revolved([(ri, 0.0), (rp(za) - d0 * 0.1, 0.0), (rp(za) - d0 * 0.1, za - 0.4), (rp(za) - dr(za) / 2 + 0.05, za - 0.4),
                        (rp(zb) - dr(zb) / 2 + 0.05, zb + 0.4), (rp(zb) - dr(zb) * 0.25, zb + 0.4), (rp(zb) - dr(zb) * 0.25, w),
                        (ri, w)])
    L = (zb - za) / math.cos(a)
    roller = Sh.revolved([(0, 0), (d0 / 2, 0), (d1 / 2, L), (0, L)])
    n = int(2 * math.pi * rp((za + zb) / 2) / ((d0 + d1) / 2 * 1.22))
    b = cup + cone
    for k in range(n):
        b = b + Rot(0, 0, 360.0 * k / n) * Location((rp(za), 0, za)) * Rot(0, -alpha, 0) * roller
    # cage: a thin conical band
    b = b + Sh.revolved([(rp(za) - 0.4, za + 0.3), (rp(za) + 0.4, za + 0.3), (rp(zb) + 0.4, zb - 0.3), (rp(zb) - 0.4, zb - 0.3)])
    return b
