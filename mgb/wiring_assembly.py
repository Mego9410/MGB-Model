"""Shared builder for the P10b wiring assemblies: every part whose spec names the assembly is placed
once, in the car frame (wires, joints and earth points are built where they sit)."""
from __future__ import annotations

from pathlib import Path

from build123d import Location

from mgb import spec as S

ROOT = Path(__file__).resolve().parent.parent


def instances(assembly_id, explode=None):
    """(inst_id, part_id, Location, opts) for every spec part of the assembly, in file order.
    explode: {part id: explode dict} for the parts that lift away (switch gear and connectors)."""
    out = []
    explode = explode or {}
    for f in sorted((ROOT / "specs").rglob("*.yaml")):
        for sp in S.load_file(f):
            if sp.data.get("assembly") == assembly_id:
                o = {}
                if sp.id in explode:
                    o["explode"] = explode[sp.id]
                out.append((sp.id + "#1", sp.id, Location((0, 0, 0)), o))
    return out
