"""Reusable solids built in standalone (algebra) mode, z up, origin at the base.

Call these outside any builder context, then combine with + / - / .moved().
"""
from __future__ import annotations

import math

from build123d import (Axis, Box, Cylinder, Edge, Face, Location, Part, Plane, Polygon,
                       Pos, Rot, Solid, Wire, extrude, make_face, revolve, sweep)

ALIGN_BASE = (__import__("build123d").Align.CENTER,) * 2 + (__import__("build123d").Align.MIN,)


def revolved(profile: list[tuple[float, float]]) -> Part:
    """Revolve a closed (r, z) profile about Z. Points go round the outline in order."""
    pts = [(r, 0, z) for r, z in profile]
    face = Face(Wire.make_polygon(pts, close=True))
    return revolve(face, Axis.Z)


def cyl(d: float, h: float, z0: float = 0.0) -> Part:
    return Cylinder(d / 2, h, align=ALIGN_BASE).moved(Location((0, 0, z0)))


def tube(od: float, id_: float, h: float, z0: float = 0.0) -> Part:
    return revolved([(id_ / 2, z0), (od / 2, z0), (od / 2, z0 + h), (id_ / 2, z0 + h)])


def washer(od: float, id_: float, t: float) -> Part:
    return tube(od, id_, t)


def coil_spring(wire: float, od: float, length: float, coils: float, end_turns: float = 0.75) -> Part:
    """Helical compression spring with closed, ground ends, from z = 0 to z = length.

    `coils` is the total number of turns. The closed end turns are flattened by
    grinding: the swept coil is cut flat at both ends.
    """
    r = (od - wire) / 2
    active = max(coils - 2 * end_turns, 0.5)
    pitch = max((length - (2 * end_turns + 1) * wire) / active, wire * 1.05)
    height = length + wire  # sweep a little past both ends, then grind flat
    helix = Edge.make_helix(pitch, height, r, center=(0, 0, -wire / 2))
    start = helix.position_at(0)
    tangent = helix.tangent_at(0)
    prof = Face(Wire.make_circle(wire / 2, Plane(start, z_dir=tangent)))
    coil = sweep(prof, path=helix, is_frenet=True)
    keep = Box(od * 2, od * 2, length, align=ALIGN_BASE)
    return coil & keep


def chamfered_cyl(d: float, h: float, ch: float, z0: float = 0.0, top=True, bottom=True) -> Part:
    r = d / 2
    pts = [(0, z0)]
    pts += [(r - ch, z0), (r, z0 + ch)] if bottom else [(r, z0)]
    pts += [(r, z0 + h - ch), (r - ch, z0 + h)] if top else [(r, z0 + h)]
    pts += [(0, z0 + h)]
    return revolved(pts)


def slot_plate(length: float, width: float, t: float) -> Part:
    """Rounded-end flat plate centred on the origin along X."""
    from build123d import SlotOverall
    return extrude(SlotOverall(length, width), t)
