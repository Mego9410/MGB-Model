"""Crankshaft, main bearing shells, thrust washers and main caps.

Crankshaft frame: crank axis along X through the origin, engine X positions
(so place it at (0, 0, crank_z)). Throws drawn at No 1 TDC: 1 and 4 up, 2 and 3 down.
Shell and cap frame: axis along X through the origin.
"""
import math
from pathlib import Path

from build123d import Align, Box, Cylinder, Location, Part, Plane, Rot, Solid, Vector

from mgb import engine_layout as E, probes, shapes as Sh, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parents[3]
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
EL = E.layout(HL)
BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def _l(p, spec):
    p.label = spec.id
    return p


def xcyl(r, x0, x1, y=0.0, z=0.0):
    return Cylinder(r, abs(x1 - x0), rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _web(x, w, pin_z, r_axis, r_pin):
    """A crank web: the hull of a disc on the axis and a disc on the crankpin."""
    from build123d import BuildSketch, Circle, Locations, Plane, extrude, make_hull, BuildLine
    pts = []
    for zc, r in ((0.0, r_axis), (pin_z, r_pin)):
        for k in range(24):
            a = 2 * math.pi * k / 24
            pts.append((r * math.cos(a), zc + r * math.sin(a)))
    # convex hull in the YZ plane
    pts = sorted(set(pts))
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
    hull = lower[:-1] + upper[:-1]
    from build123d import Face, Wire
    face = Face(Wire.make_polygon([(x - w / 2, y, z) for y, z in hull], close=True))
    return extrude(face, w, dir=(1, 0, 0))


def crankshaft(spec) -> Part:
    from build123d import extrude  # noqa: F401
    rm = spec.nom("main_journal_diameter") / 2
    rp = spec.nom("crankpin_diameter") / 2
    t = spec.nom("throw")
    wt = spec.nom("web_thickness")
    pl = spec.nom("crankpin_length")
    c = None
    for mx in EL.main_x:                                         # main journals
        j = xcyl(rm, mx - 16, mx + 16)
        c = j if c is None else c + j
    for cyl, x in enumerate(EL.cyl_x, start=1):
        z = t * math.cos(math.radians(EL.pin_angle[cyl]))
        c = c + xcyl(rp, x - pl / 2, x + pl / 2, z=z)            # crankpin
        for side in (-1, 1):                                      # webs either side
            wx = x + side * (pl / 2 + wt / 2)
            c = c + _web(wx, wt, z, rm + 8, rp + 7)
            # counterweight lobe opposite the pin
            c = c + _web(wx, wt, -z * 0.55, rm + 8, rm + 10)
    # journals joining the webs of adjacent throws with no main bearing between (1-2 and 3-4)
    for a, b in ((EL.cyl_x[0], EL.cyl_x[1]), (EL.cyl_x[2], EL.cyl_x[3])):
        c = c + xcyl(rm, b + pl / 2 + wt - 1, a - pl / 2 - wt + 1)
    # links from the outer and centre webs into the main journals
    for a, b in ((EL.cyl_x[0] + pl / 2 + wt - 1, EL.main_x[0] - 15),
                 (EL.cyl_x[1] - pl / 2 - wt + 1, EL.main_x[1] + 15),
                 (EL.main_x[1] - 15, EL.cyl_x[2] + pl / 2 + wt - 1),
                 (EL.main_x[2] + 15, EL.cyl_x[3] - pl / 2 - wt + 1)):
        c = c + xcyl(rm, min(a, b), max(a, b))
    front = EL.main_x[0] + 16
    c = c + xcyl(spec.nom("snout_diameter") / 2, front, front + 72)          # snout: sprocket, pulley
    rear = EL.main_x[2] - 16
    c = c + xcyl(rm - 2, rear - 22, rear) + xcyl(spec.nom("flange_diameter") / 2, rear - 34, rear - 22)
    return _l(c, spec)


def shell(spec, journal_d=None) -> Part:
    """One bearing half-shell, lower half, axis along X."""
    L = spec.nom("length")
    w = spec.nom("wall_thickness")
    d = journal_d
    r_in = d / 2
    ring = Rot(0, 90, 0) * Sh.tube(d + 2 * w, d, L, z0=-L / 2)
    half = ring & Box(L + 2, d + 2 * w + 2, (d + 2 * w) / 2 + 1, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return _l(half, spec)


def main_shell(spec):
    return shell(spec, 54.015)


def big_end_shell(spec):
    return shell(spec, 47.655)


def thrust_washer(spec) -> Part:
    t, od = spec.nom("thickness"), spec.nom("outside_diameter")
    ring = Rot(0, 90, 0) * Sh.tube(od, 55.0, t, z0=-t / 2)
    half = ring & Box(t + 2, od + 2, od / 2 + 1, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return _l(half, spec)


def main_cap(spec) -> Part:
    w, sp, h = spec.nom("width_along_crank"), spec.nom("stud_spacing"), spec.nom("height")
    body = Box(w, sp + 26, h, align=(Align.CENTER, Align.CENTER, Align.MAX))
    body = body - xcyl(28.82, -w, w)
    for y in (-sp / 2, sp / 2):
        body = body - Cylinder(5.8, h * 3).moved(Location((0, y, 0)))
    return _l(body, spec)


PARTS = {
    "engine.block.crankshaft": {"build": crankshaft},
    "engine.block.main-bearing-shell": {"build": main_shell, "probes": {"length": lambda p: probes.bbox_size(p, "x")}},
    "engine.block.thrust-washer": {"build": thrust_washer},
    "engine.block.main-cap": {"build": main_cap},
}
