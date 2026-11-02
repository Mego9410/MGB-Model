"""Inlet and exhaust manifolds and their joint, on the left of the head.
Haynes Sec 15 and 61; photos 61.1(a) and (b); owners' photos. Built in the engine
frame: the manifold joint face of the head is the plane y = y_max (mgb.head_layout).
"""
import math
from pathlib import Path

from build123d import (Align, Axis, Box, Circle, Cylinder, FilletPolyline, Location, Part, Plane, SlotCenterToCenter, extrude,
                       fillet, sweep)

from mgb import exhaust_layout as EX, fasteners as F, shapes as Sh, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parents[3]
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
FACE = HL.y_max                        # head joint face for the manifolds
GASKET_T = 1.6
FLANGE_FACE = FACE + GASKET_T
COLLECT = (-10.0, 158.0, -92.0)        # branches meet below the centre port, above the down pipe flange (photo 61.1(a))
CARB_Y, CARB_Z = 176.0, 48.0           # carburettor flange faces of the inlet manifold


def _l(p, spec):
    p.label = spec.id
    return p


def _yslot(x, z, length, height, y0, t, vertical=False):
    """Stadium plate in an XZ plane, from y0 outward by t."""
    pl = Plane(origin=(x, y0, z), x_dir=(0, 0, 1) if vertical else (1, 0, 0), z_dir=(0, 1, 0))
    return extrude(pl * SlotCenterToCenter(max(length - height, 0.01), height), t)


def _ycyl(r, x, z, y0, y1):
    return Cylinder(r, y1 - y0, rotation=(-90, 0, 0)).moved(Location((x, (y0 + y1) / 2, z)))


def _pipe(points, r, wall, radius=24.0):
    path = FilletPolyline(*points, radius=radius)
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    return sweep(pl * (Circle(r) - Circle(r - wall)) if wall else pl * Circle(r), path=path)


def _rod(points, r, radius=24.0):
    return _pipe(points, r, None, radius)


def exhaust_manifold(spec) -> Part:
    """Cast iron, three ports (the centre one siamesed) sweeping down to two outlets side by side under the
    centre port: cylinders 1 and 4 by a Y to the front outlet, the siamesed 2/3 port to the rear one (MGOC Spares
    "MGB exhaust systems": twin downpipes). One flange carries both outlets, each with two studs across the car
    and a counterbore for the downpipe's sealing ring (photo 46.2; P11a mgb.exhaust_layout)."""
    r, wall = spec.nom("branch_bore") / 2 + 4, 4.0
    y0, t = FLANGE_FACE, spec.nom("flange_thickness")
    cx, cy, cz = COLLECT
    fz = EX.OUTLET_FACE_Z                       # underside of the outlet flange
    flange = None
    branches = None

    def target(valves):
        return EX.OUTLETS["rear" if len(valves) > 1 else "front"]

    def route(x, z, valves, start):
        tx, ty = target(valves)
        outer = len(valves) == 1
        return [(x, start, z), (x, y0 + 30, z - 6), (x * 0.55 + tx * 0.45, ty - 4 + (6 if outer else 0), z - 70),
                (tx + x * 0.08, ty + (5 if outer else 0), cz)]
    for x, z, valves in HL.exhaust_ports:
        siamese = len(valves) > 1
        pad = _yslot(x, z, 64 if siamese else 46, 46, y0, t)
        flange = pad if flange is None else flange + pad
        rr = r + (3 if siamese else 0)
        b = _rod(route(x, z, valves, y0), rr)
        branches = b if branches is None else branches + b
    # ears: out to the end studs, and across to the lower centre studs
    for x, z, kind in HL.manifold_studs:
        sgn = 1 if x > 0 else -1
        if kind == "end":
            flange = flange + _yslot(x - sgn * 8, z, 42, 26, y0, t)
        elif z < 30:
            flange = flange + _yslot(x - sgn * 9, z + 2, 44, 24, y0, t)
    m = flange + branches
    ox = [p[0] for p in EX.OUTLETS.values()]
    for x, y in EX.OUTLETS.values():                                   # the two outlet bosses
        m = m + Location((x, y, fz + t)) * Cylinder(r + 3, cz - fz - t + 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pad = Location(((max(ox) + min(ox)) / 2, cy, fz + t / 2)) * Box(max(ox) - min(ox) + 46, 2 * EX.STUD_DY + 22, t)
    pad = fillet(pad.edges().filter_by(Axis.Z), 11)
    m = m + pad
    # bores: ports, branches (hollow), outlets with their sealing ring counterbores, stud holes
    for x, z, valves in HL.exhaust_ports:
        siamese = len(valves) > 1
        m = m - _yslot(x, z, 42 if siamese else 30, 30, y0 - 1, t + 2)
        m = m - _rod(route(x, z, valves, y0 - 1), (r + (3 if siamese else 0)) - wall)
    for x, y in EX.OUTLETS.values():
        m = m - Location((x, y, fz - 1)) * Cylinder(EX.OUTLET_BORE / 2, cz - fz + 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
        m = m - Location((x, y, fz - 1)) * Cylinder(EX.SEAT_D / 2, EX.SEAT_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, y in EX.STUDS:
        m = m - Location((x, y, fz - 1)) * Cylinder(3.6, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, z, kind in HL.manifold_studs:
        if kind == "end" or z < 30:
            m = m - _ycyl(4.6, x, z, y0 - 1, y0 + t + 1)
    return _l(m, spec)


def inlet_manifold(spec) -> Part:
    """Two siamesed runners out to the twin carburettor flanges, joined by a balance
    pipe; flange ears up to the centre studs (photo 61.1(b))."""
    r, wall = spec.nom("runner_bore") / 2 + 3.5, 3.5
    y0, t = FLANGE_FACE, spec.nom("flange_thickness")
    m = None
    for x, z, _ in HL.inlet_ports:
        pad = _yslot(x, z, 56, 44, y0, t)
        ear = _yslot(x - math.copysign(HL.pitch / 2, x), 58.0, 30, 22, y0, t)
        arm = Location(((x + x - math.copysign(HL.pitch / 2, x)) / 2, y0 + t / 2, (z + 58) / 2)) * Box(abs(HL.pitch / 2), t, 22)
        pts = [(x, y0, z), (x, y0 + 30, z + 2), (x * 0.95, CARB_Y - 18, CARB_Z), (x * 0.95, CARB_Y, CARB_Z)]
        run = _rod(pts, r, 20.0)
        carb = _yslot(x * 0.95, CARB_Z, 74, 52, CARB_Y - 10, 10)             # carburettor flange
        part = pad + ear + arm + run + carb
        m = part if m is None else m + part
    bal = Cylinder(spec.nom("balance_pipe_diameter") / 2, 2 * HL.pitch * 0.95, rotation=(0, 90, 0)).moved(
        Location((0, CARB_Y - 34, CARB_Z + 4)))
    m = m + bal
    for x, z, _ in HL.inlet_ports:
        m = m - _yslot(x, z, 40, 30, y0 - 1, t + 2)
        pts = [(x, y0 - 1, z), (x, y0 + 30, z + 2), (x * 0.95, CARB_Y - 18, CARB_Z), (x * 0.95, CARB_Y + 1, CARB_Z)]
        m = m - _rod(pts, r - wall, 20.0)
        for sx in (-24, 24):                                               # carburettor studs
            m = m - _ycyl(3.6, x * 0.95 + sx, CARB_Z, CARB_Y - 12, CARB_Y + 1)
        m = m - _ycyl(4.6, x - math.copysign(HL.pitch / 2, x), 58.0, y0 - 1, y0 + t + 1)
    m = m - Cylinder(spec.nom("balance_pipe_diameter") / 2 - 3, 2 * HL.pitch * 0.9, rotation=(0, 90, 0)).moved(
        Location((0, CARB_Y - 34, CARB_Z + 4)))
    return _l(m, spec)


def gasket(spec) -> Part:
    """One-piece gasket for all five ports and the six studs."""
    t = spec.nom("thickness")
    g = Location((0, FACE + t / 2, 35)) * Box(440, t, 70)
    g = fillet(g.edges().filter_by(Axis.Y), 10)
    for x, z, valves in HL.exhaust_ports:
        g = g - _yslot(x, z, 44 if len(valves) > 1 else 32, 32, FACE - 1, t + 2)
    for x, z, _ in HL.inlet_ports:
        g = g - _yslot(x, z, 42, 32, FACE - 1, t + 2)
    for x, z, _ in HL.manifold_studs:
        g = g - _ycyl(4.4, x, z, FACE - 1, FACE + t + 1)
    return _l(g, spec)


def washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def nut(spec) -> Part:
    return _l(F.hex_nut("5/16"), spec)


PARTS = {
    "engine.manifolds.exhaust": {"build": exhaust_manifold},
    "engine.manifolds.inlet": {"build": inlet_manifold},
    "engine.manifolds.gasket": {"build": gasket},
    "engine.manifolds.washer-large": {"build": washer},
    "engine.manifolds.washer-small": {"build": washer},
    "engine.manifolds.nut": {"build": nut},
}
