"""Bevel gear teeth (straight or spiral) for the final drive and the differential.

Local frame: gear axis +z, the heel pitch circle (radius R) in the plane z = 0, the pitch cone apex
on the axis at z = H = R / tan(delta). Teeth stand off the pitch cone along its outward normal
(toward +z for a near-flat crown wheel, outward for a pinion). Each tooth is lofted through
sections across the face width F; a spiral angle turns the sections progressively round the axis,
so the tooth runs along a curve (spiral bevel / hypoid look). Tooth forms are trapezoidal (20 deg
flanks), scaled toward the apex. Callers build the gear body to the root cone given by `cone_pt`.
"""
from __future__ import annotations

import math

from build123d import Compound, Part, Solid, Wire

from mgb import shapes as Sh

PA = math.radians(20.0)


class Bevel:
    def __init__(self, n, R, delta_deg, F, add, ded, spiral_deg=0.0, hand=1, sections=3):
        self.sections = sections
        self.n, self.R, self.F, self.add, self.ded = n, R, F, add, ded
        d = math.radians(delta_deg)
        self.H = R / math.tan(d)
        self.L = math.hypot(R, self.H)
        self.nr, self.nz = self.H / self.L, R / self.L          # outward normal of the pitch cone (r, z)
        self.spiral = math.radians(spiral_deg) * hand
        self.p = 2 * math.pi * R / n

    def cone_pt(self, s, off):
        """(r, z) of the point s along the generator from the heel, offset `off` along the normal
        (scaled toward the apex like the teeth)."""
        k = 1.0 - s / self.L
        return (self.R * k + self.nr * off * k, self.H * s / self.L + self.nz * off * k)

    def _section(self, s, phi):
        k = 1.0 - s / self.L
        half = self.p / 4 * 0.93                       # running backlash
        half_root = (half + self.ded * math.tan(PA)) * k
        half_tip = max((half - self.add * math.tan(PA)) * k, 0.25 * k)
        pts = []
        for off, w in ((-self.ded - 0.4, half_root + 0.15 * k), (-self.ded, half_root), (self.add, half_tip)):
            pts.append((off, w))
        prof = [(o, -w) for o, w in pts] + [(o, w) for o, w in reversed(pts)]
        out = []
        er = (math.cos(phi), math.sin(phi))
        t = (-math.sin(phi), math.cos(phi))
        for off, w in prof:
            r, z = self.cone_pt(s, off)
            out.append((r * er[0] + w * t[0], r * er[1] + w * t[1], z))
        return Wire.make_polygon(out, close=True)

    def tooth(self, phi0, sections=None):
        """One tooth centred at angle phi0 (rad) at the heel."""
        sections = sections or self.sections
        wires = []
        for i in range(sections):
            f = i / (sections - 1)
            s = -0.2 + f * (self.F + 0.4)
            # spiral: the tooth's angular drift grows along the face (circular arc look)
            r_mean = self.R * (1.0 - self.F / (2 * self.L))
            phi = phi0 + math.tan(self.spiral) * (f - 0.5) * (1.0 + 0.35 * (f - 0.5)) * self.F / r_mean
            wires.append(self._section(s, phi))
        return Solid.make_loft(wires, ruled=sections == 2)

    def teeth(self, phase_deg=0.0):
        return [self.tooth(math.radians(phase_deg) + 2 * math.pi * k / self.n) for k in range(self.n)]


def gear(bv: Bevel, body: Part, phase_deg=0.0) -> Part:
    """Fuse the teeth to a body whose surface follows the root cone."""
    teeth = bv.teeth(phase_deg)
    out = body.fuse(*teeth)
    out = out.clean()
    return out
