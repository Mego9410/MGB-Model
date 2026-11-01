"""Distributor and HT lead layout (engine frame).

The distributor housing sits in the leaning boss on the right-hand side of the block
(mgb.block_section / parts/engine/block/block.py: boss on the gallery ledge, axis
tilted 22 degrees outward). Plug positions come from the head layout (parts in the
head assembly sit at the plug seats, axis tilted 57 degrees toward the right).
"""
from __future__ import annotations

import math
from pathlib import Path

from mgb import block_section as B, engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parent.parent
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
EL = E.layout(HL)

LEAN_DEG = 22.0                                     # boss axis tilt, top outward (-Y)
AXIS = (0.0, -math.sin(math.radians(LEAN_DEG)), math.cos(math.radians(LEAN_DEG)))
_BOSS_CENTRE = (EL.drive_x, B.YR - 15.0, B.LEDGE_Z + 10.0)
BOSS_TOP = tuple(c + 32.0 * a for c, a in zip(_BOSS_CENTRE, AXIS))   # face the housing flange sits on
LUG_X = 32.0                                        # housing bolt lug: frame x of the bolt, on the boss line
LUG_DEPTH = 24.0                                    # lug runs this far down the axis from the boss face

PLUG_U = (0.0, -0.839, 0.544)                       # plug axis, from the head assembly


def plug_seats():
    return [(x, HL.y_min - 4.0, 37.7) for x, _y, _z in HL.plugs]


def plug_point(seat, along):
    return tuple(s + u * along for s, u in zip(seat, PLUG_U))


def to_engine(local):
    """Distributor frame (z up the axis from the boss top, x forward) to the engine frame."""
    x, y, z = local
    c, s = math.cos(math.radians(LEAN_DEG)), math.sin(math.radians(LEAN_DEG))
    return (BOSS_TOP[0] + x, BOSS_TOP[1] + y * c - z * s, BOSS_TOP[2] + y * s + z * c)


# distributor frame heights (z along the axis from the boss top)
FLANGE_T = 6.0
CLAMP_Z = FLANGE_T                                  # clamp plate on the housing flange
BODY_Z = CLAMP_Z + 4.0                              # underside of the body bowl
BOWL_H = 40.0
CAP_Z = BODY_Z + BOWL_H
CAP_H = 44.0
TOWER_Z = CAP_Z + 24.0                              # side-entry towers on the cap
TOWER_R = 33.0
FIRING = [1, 3, 4, 2]                               # Haynes p94; rotor turns anticlockwise


def tower_angle(k):
    """Angle (deg, in the distributor frame) of the cap tower for the k-th firing."""
    # rotor turns anticlockwise seen from above, so the towers step that way; No 1 faces
    # forward and outboard, keeping every boss off the line of the block (D)
    return -45.0 + 90.0 * k
