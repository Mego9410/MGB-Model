"""Measure features on built solids so the build can check them against the spec.

Each part script declares PROBES: {spec_key: callable(part) -> measured value}.
Values are mm (or degrees for angles). The build compares each against the
spec range, widened by PROBE_TOL to absorb tessellation-free float noise.
"""
from __future__ import annotations

import math

from build123d import GeomType, Part

PROBE_TOL = 1e-4  # mm or degrees


def bbox_size(part: Part, axis: str) -> float:
    bb = part.bounding_box()
    return {"x": bb.size.X, "y": bb.size.Y, "z": bb.size.Z}[axis]


def cylinder_diameters(part: Part) -> list[tuple[float, float]]:
    """(diameter, axial length) for every cylindrical face, largest length first."""
    out = []
    for f in part.faces().filter_by(GeomType.CYLINDER):
        r = f.radius
        bb = f.bounding_box()
        length = max(bb.size.X, bb.size.Y, bb.size.Z) if r * 2 < min(bb.size.X, bb.size.Y, bb.size.Z) + 1e-6 else bb.size.Z
        out.append((2 * r, length))
    return sorted(out, key=lambda t: -t[1])


def longest_cylinder_diameter(part: Part) -> float:
    return cylinder_diameters(part)[0][0]


def cone_face_angles(part: Part) -> list[float]:
    """Angle in degrees between each conical face and the plane normal to its axis."""
    out = []
    for f in part.faces().filter_by(GeomType.CONE):
        semi = f.geom_adaptor().Cone().SemiAngle()  # angle from the axis
        out.append(90.0 - abs(math.degrees(semi)))
    return out


def largest_cone_angle(part: Part) -> float:
    """Angle of the conical face furthest from the axis (e.g. a valve seat face)."""
    best, best_r = None, -1.0
    for f in part.faces().filter_by(GeomType.CONE):
        bb = f.bounding_box()
        rad = max(bb.size.X, bb.size.Y) / 2
        if rad > best_r:
            semi = f.geom_adaptor().Cone().SemiAngle()
            best, best_r = 90.0 - abs(math.degrees(semi)), rad
    return best


def within(value: float, lo: float, hi: float) -> bool:
    return lo - PROBE_TOL <= value <= hi + PROBE_TOL
