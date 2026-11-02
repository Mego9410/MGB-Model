"""Fuel pipes from the tank to the pump and from the pump to the engine bay feed union (Haynes Ch 3 Secs 5, 9, 12;
MGOC Spares "MGB fuel lines - rear & main"). Pipes and hoses are drawn in place in the car frame along the routes
in mgb.fuel_supply_layout; union nuts, clips and screws are drawn at the origin and placed by
assemblies/fuel_supply.py.
"""
from __future__ import annotations

import math

from build123d import Box, Cylinder, Location, Part, Plane, Rot

from mgb import fasteners as F, fuel_supply_layout as L, shapes as Sh
from parts.fuel.exhaust import tube

OD = L.PIPE_OD
HOSE_OD = 12.5


def _l(p, spec):
    p.label = spec.id
    return p


def _dir(a, b):
    v = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def braided_hose(points):
    """Steel-braided hose with a crimped ferrule at each end."""
    h = tube(points, HOSE_OD, None, radius=14.0)
    for a, b in ((points[0], points[1]), (points[-1], points[-2])):
        d = _dir(a, b)
        h = h + Location(Plane(origin=a, z_dir=d)) * Sh.revolved([(0, 0), (HOSE_OD / 2 + 1.6, 0),
                                                                  (HOSE_OD / 2 + 1.6, 16.0), (HOSE_OD / 2 + 0.6, 19.0),
                                                                  (0, 19.0)])
        for k in range(3):                                                          # crimp grooves
            g = h - Location(Plane(origin=a, z_dir=d)) * Location((0, 0, 4.0 + 4.5 * k)) * Sh.tube(
                HOSE_OD + 6.0, HOSE_OD + 1.6, 1.2)
            if g.is_valid and len(g.solids()) == 1:
                h = g
    return h


def tank_hose(spec) -> Part:
    """Braided flexible hose from the tank's outlet stub to the tank-to-pump pipe (braided hoses in the rear fuel
    line area to 1975, MGOC Spares)."""
    return _l(braided_hose(L.TANK_HOSE), spec)


def pump_hose(spec) -> Part:
    """Braided flexible hose from the pump's outlet connection to the main pipe's union on the heelboard, so the
    pump rides on its rubber mountings (D)."""
    return _l(braided_hose(L.PUMP_HOSE), spec)


def pipe(points):
    p = tube(points, OD, L.PIPE_WALL, radius=25.0)
    return p


def tank_pipe(spec) -> Part:
    """Rigid pipe, tank to pump (MGOC AHH6703 "pipe tank to pump"): across the tank's front face, up and over the
    axle under the arch, forward under the tonneau floor between the tunnel and the right-hand battery carrier and
    into the pump's inlet connection from behind."""
    return _l(pipe(L.TP_ROUTE), spec)


def feed_pipe(spec) -> Part:
    """Main underfloor pipe (MGOC: "clipped to the underside of the right side floor panels" with the rear brake
    pipe; enters the engine bay by the heater), from the union on the heelboard down, forward under the floor, up
    the toe board, up and across the bulkhead face above the bellhousing and forward to the feed union."""
    return _l(pipe(L.MAIN_ROUTE), spec)


def union_nut(spec) -> Part:
    """Pipe union nut, 5/16 in pipe, axis z, base at the origin."""
    n = F.hex_nut("7/16")
    h = n.bounding_box().size.Z
    u = n + Location((0, 0, h)) * Sh.revolved([(OD / 2 + 0.3, 0), (8.0, 0), (6.0, 3.0), (OD / 2 + 0.3, 3.0)])
    u = u - Location((0, 0, -1)) * Sh.cyl(OD + 0.6, h + 6)
    return _l(u - Location((0, 0, -1)) * Sh.cyl(11.3, h - 1.0), spec)          # 7/16 UNF thread bore


def pipe_union(spec) -> Part:
    """Male union on the main pipe's front end, into the feed union nut on P3's hose: a hexagon body and the
    threaded nose, axis z, nose toward +z."""
    n = F.hex_nut("7/16")
    h = n.bounding_box().size.Z
    u = n + Location((0, 0, h)) * Sh.cyl(9.0, 10.0) + Location((0, 0, -6.0)) * Sh.cyl(OD + 2.0, 6.0)
    u = u - Location((0, 0, -7)) * Sh.cyl(OD - 2 * L.PIPE_WALL, h + 20)
    return _l(u - Location((0, 0, -7)) * Sh.cyl(OD + 0.2, 7.0), spec)


def p_clip(spec, standoff=10.0) -> Part:
    """P-clip: a strip looped round the pipe (axis local x), its two ends brought together as a tab up to the body
    face at local z = standoff, with the screw hole."""
    w, t = spec.nom("width"), 0.9
    r = OD / 2 + 0.3
    loop = Location(Plane(origin=(-w / 2, 0, 0), z_dir=(1, 0, 0))) * Sh.tube(2 * (r + t), 2 * r, w)
    loop = loop - Location((0, 0, r + t)) * Box(w + 2, 2 * t + 0.4, 2 * t)
    tab = Location((0, 0, (r + standoff) / 2)) * Box(w, 2 * t + 0.2, standoff - r)
    foot = Location((0, -6.0, standoff - t / 2 - 0.01)) * Box(w, 14.0, t)
    c = loop + tab + foot - Location((0, -8.0, standoff - 3)) * Sh.cyl(4.2, 5.0)
    return _l(c, spec)


def clip_screw(spec) -> Part:
    """Self-tapping pan head screw for a P-clip, axis z, head at the origin, shank down -z."""
    Ln = spec.nom("length")
    s = Location((0, 0, -Ln)) * Sh.revolved([(0, 0), (1.2, 0), (2.4, 2.0), (2.4, Ln), (0, Ln)])
    s = s + Sh.revolved([(0, 0), (4.6, 0), (4.6, 1.2), (3.4, 2.8), (0, 3.0)])
    s = s - Location((0, 0, 2.0)) * Box(10.0, 1.0, 2.0)
    return _l(s, spec)


PARTS = {
    "fuel.supply.tank-hose": {"build": tank_hose},
    "fuel.supply.tank-pipe": {"build": tank_pipe},
    "fuel.supply.pump-hose": {"build": pump_hose},
    "fuel.supply.feed-pipe": {"build": feed_pipe,
                              "probes": {"outside_diameter": lambda p: (p & Location((-1000.0, L.FLOOR_Y, L.FLOOR_PIPE_Z)) *
                                                                         Box(3.0, 40.0, 40.0)).bounding_box().size.Y}},
    "fuel.supply.union-nut": {"build": union_nut},
    "fuel.supply.pipe-union": {"build": pipe_union},
    "fuel.supply.p-clip": {"build": p_clip},
    "fuel.supply.clip-screw": {"build": clip_screw},
}
