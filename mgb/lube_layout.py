"""Lubrication layout: oil pump, strainer, sump, filter, relief valve and dipstick.

Engine frame (mgb.engine_layout). Haynes Fig 1.16 (schematic), Fig 1.1 (early
oil filter), Sec 2, 17, 20, 21; photos 2.4, 54.3, 55.2, 55.4. Positions derived (D):
the pump hangs below the crankcase on the drive pillar under the camshaft skew gear,
the filter head bolts to the pad on the right-hand side, the relief valve sits in the
boss at the left rear, and the dipstick enters on the right (Haynes Sec 2).
"""
from __future__ import annotations

import math
from pathlib import Path

from mgb import block_section as B, engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parent.parent
EL = E.layout(head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml")))

SZ = EL.sump_z                          # sump flange face of the block
DRIVE_X = EL.drive_x
DRIVE_Y = EL.cam_y + 18.0               # camshaft skew gear 11 mm + drive gear 7 mm (pitch radii)
PUMP_TOP = SZ                           # pump flange on a pad level with the sump face
PUMP_PAD_Z = SZ + 16.0                  # top of the pad inside the crankcase
PUMP_FLANGE = (DRIVE_X - 4.0, DRIVE_Y - 6.0)   # centre of the three-stud flange, clear of the No 3 big end
PUMP_STUD_R = 28.0


def pump_studs():
    return [(PUMP_FLANGE[0] + PUMP_STUD_R * math.cos(math.radians(30 + 120 * k)),
             PUMP_FLANGE[1] + PUMP_STUD_R * math.sin(math.radians(30 + 120 * k))) for k in range(3)]

GASKET_T = 3.0                          # cork sump gasket
SUMP_TOP = SZ - GASKET_T                # sump flange top face
SUMP_DEPTH = 118.0                      # flange to the floor of the deep well
SUMP_SHALLOW = 52.0                     # rear part, over the gearbox bellhousing
SUMP_STEP_X = -96.0                     # where the deep well ends toward the rear
SUMP_FLOOR = SUMP_TOP - SUMP_DEPTH

FILTER_PAD = (-30.0, B.wall_y(-185.0, -1) - 9, -185.0)       # centre of the block pad face (x, y, z)
FILTER_AXIS_Y = FILTER_PAD[1] - 52.0                          # bowl hangs outboard of the pad
RELIEF = (-178.0, B.wall_y(B.RELIEF_Z, 1) + 12, B.RELIEF_Z)  # domed nut seat on the left rear boss

DIPSTICK_X = 96.0                      # between the No 1 and No 2 crank webs
DIPSTICK_ENTRY = (DIPSTICK_X, B.wall_y(-172.0, -1), -172.0)
_d = (0.0, 0.35, -0.94)
_n = math.hypot(*_d)
DIPSTICK_DIR = tuple(c / _n for c in _d)                    # into the block and down to the sump


def sump_bolts():
    """Flange bolt positions (x, y): down both rails and across the ends."""
    x0, x1 = -B_HALF + 12, B_HALF - 12
    pts = []
    for k in range(9):
        x = x0 + (x1 - x0) * k / 8
        pts += [(x, -B.FLANGE_HW + 6), (x, B.FLANGE_HW - 6)]
    for y in (-60.0, 60.0):
        pts += [(x1 + 4, y), (x0 - 4, y)]
    # P10: none where the flange is relieved for the starter yoke (mgb.electrical_layout)
    from mgb import electrical_layout as EZ
    return [(x, y) for x, y in pts if not EZ.in_starter_recess(x, y, SUMP_TOP, 8.0)]


B_HALF = 226.0
