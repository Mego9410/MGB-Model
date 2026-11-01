"""Camshaft, tappets, pushrods and tappet side covers.

Camshaft frame: cam axis along X through the origin, engine X positions (place at
(0, cam_y, cam_z)). Lobes are phased from the Haynes valve timing (p22) and
drawn at No 1 TDC on compression.
Tappet and pushrod frame: axis Z, base at z = 0.
"""
import math
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Face, Location, Part, Rot, Sphere, Wire, extrude, fillet

from mgb import engine_layout as E, fasteners as F, probes, shapes as Sh, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parents[3]
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
EL = E.layout(HL)
BASE = (Align.CENTER, Align.CENTER, Align.MIN)

# crank angle of each cylinder's compression TDC, firing order 1-3-4-2
TDC = {1: 0.0, 3: 180.0, 4: 360.0, 2: 540.0}
INLET_PEAK = ((-360 - 16) + (-360 + 180 + 56)) / 2   # crank deg: midpoint of opening (16 BTDC) and closing (56 ABDC) of the intake stroke
EXHAUST_PEAK = (180 - 51 + 360 + 21) / 2        # crank deg: midpoint of 51 BBDC .. 21 ATDC


def _l(p, spec):
    p.label = spec.id
    return p


def xcyl(r, x0, x1):
    return Cylinder(r, abs(x1 - x0), rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, 0, 0)))


def lobe_angle(kind: str, cyl: int) -> float:
    """Cam angle (deg, about +X) of the lobe nose, measured from +Z (toward the tappet)."""
    peak = (INLET_PEAK if kind == "inlet" else EXHAUST_PEAK) + TDC[cyl]
    return -(peak / 2.0)  # cam turns at half crank speed


def _lobe(x, width, base_r, lift, angle_deg):
    nose_r = 6.0
    d = base_r + lift - nose_r
    pts = []
    for k in range(48):  # convex hull of base circle and nose circle, in the YZ plane
        a = 2 * math.pi * k / 48
        pts.append((base_r * math.cos(a), base_r * math.sin(a)))
        pts.append((nose_r * math.cos(a), d + nose_r * math.sin(a)))
    pts = sorted(set(pts))
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    hull = lo[:-1] + hi[:-1]
    face = Face(Wire.make_polygon([(x - width / 2, y, z) for y, z in hull], close=True))
    return Rot(angle_deg, 0, 0) * extrude(face, width, dir=(1, 0, 0))


def camshaft(spec) -> Part:
    dj = [spec.nom(k) / 2 for k in ("front_journal_diameter", "centre_journal_diameter", "rear_journal_diameter")]
    base_r = spec.nom("base_circle_diameter") / 2
    lift, w = spec.nom("lobe_lift"), spec.nom("lobe_width")
    xs = EL.cam_journal_x
    c = xcyl(13.0, xs[2] - 14, xs[0] + 14)                       # core shaft
    for x, r, L in zip(xs, dj, (30, 25, 25)):
        c = c + xcyl(r, x - L / 2, x + L / 2)
    for v in HL.valves:
        c = c + _lobe(v.x, w, base_r, lift, lobe_angle(v.kind, v.cyl))
    gear = xcyl(15.0, EL.drive_x - 9, EL.drive_x + 9)    # skew gear for distributor and oil pump drive
    for k in range(14):
        a = 360 * k / 14
        gear = gear - Rot(a, 0, 0) * (Location((EL.drive_x, 0, 15.0)) * Rot(0, 0, 30) * Box(22, 2.0, 4.0))
    c = c + gear
    c = c + xcyl(11.0, xs[0] + 15, xs[0] + 42)                    # nose for the timing sprocket
    return _l(c, spec)


def tappet(spec) -> Part:
    od, L, wt = spec.nom("outside_diameter"), spec.nom("length"), spec.nom("wall_thickness")
    t = Sh.chamfered_cyl(od, L, 0.6)
    t = t - Sh.cyl(od - 2 * wt, L - 6, z0=6.01)
    t = t + Sh.revolved([(0, 4), (5.0, 4), (5.0, 7.5), (0, 9.5)])   # seat for the pushrod ball
    return _l(t, spec)


def pushrod(spec) -> Part:
    L, d = spec.nom("length"), spec.nom("diameter")
    rod = Sh.cyl(d, L - 8, z0=4)
    ball = Sphere(4.4).moved(Location((0, 0, 4.4)))
    cup = Sh.cyl(10.5, 6, z0=L - 6) - Sphere(4.0).moved(Location((0, 0, L + 1.2)))
    return _l(rod + ball + cup, spec)


def _yfillet(part, r):
    try:
        return fillet(part.edges().filter_by(Axis.Y), r)
    except Exception:  # noqa: BLE001
        return part


def tappet_cover(spec) -> Part:
    """Pressed steel cover: flat flange, raised panel with two stiffening beads
    across its upper half and the fixing bolt through the middle (Haynes photo 61.1(a)).
    Cover frame: flange face on y = 0, panel standing out along +Y."""
    L, h, d = spec.nom("length"), spec.nom("height"), spec.nom("depth")
    t = 1.2
    C = (Align.CENTER, Align.MIN, Align.CENTER)
    flange = _yfillet(Box(L, t, h, align=C), 12.0)
    dome = _yfillet(Box(L - 16, d, h - 16, align=C), 9.0)
    try:
        dome = fillet(dome.edges().group_by(Axis.Y)[-1], 4.0)
    except Exception:  # noqa: BLE001
        pass
    inner = _yfillet(Box(L - 16 - 2 * t, d - t, h - 16 - 2 * t, align=C), 8.0).moved(Location((0, -0.01, 0)))
    c = flange + dome - inner
    for bz in (14.0, 22.0):                                       # stiffening beads
        c = c + Cylinder(2.2, L - 56, rotation=(0, 90, 0)).moved(Location((0, d - 0.6, bz)))
    c = c - Cylinder(4.2, d * 3, rotation=(90, 0, 0))
    return _l(c, spec)


def tappet_cover_gasket(spec) -> Part:
    t = spec.nom("thickness")
    C = (Align.CENTER, Align.MIN, Align.CENTER)
    g = _yfillet(Box(160, t, 78, align=C), 12.0) - _yfillet(Box(144, t * 3, 62, align=C), 10.0).moved(Location((0, -t, 0)))
    return _l(g, spec)


def cover_bolt(spec) -> Part:
    return _l(F.hex_bolt("5/16", spec.nom("length") / 25.4), spec)


def _cam_journal(i):
    return lambda p: 2 * max(f.radius for f in p.faces().filter_by(__import__("build123d").GeomType.CYLINDER)
                             if abs(f.center().X - EL.cam_journal_x[i]) < 1.0)


PARTS = {
    "engine.block.camshaft": {"build": camshaft, "probes": {
        "front_journal_diameter": _cam_journal(0), "centre_journal_diameter": _cam_journal(1),
        "rear_journal_diameter": _cam_journal(2)}},
    "engine.block.tappet": {"build": tappet, "probes": {
        "outside_diameter": lambda p: probes.bbox_size(p, "x"), "length": lambda p: probes.bbox_size(p, "z")}},
    "engine.block.pushrod": {"build": pushrod},
    "engine.block.tappet-cover": {"build": tappet_cover},
    "engine.block.tappet-cover-gasket": {"build": tappet_cover_gasket},
    "engine.block.tappet-cover-bolt": {"build": cover_bolt},
}
