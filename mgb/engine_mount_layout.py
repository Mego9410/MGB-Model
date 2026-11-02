"""Front engine mountings (Haynes Ch 1 Fig 1.29 items 1-16, 39; Sec 64; printed p52): datums shared by the engine
block (P2: the left-hand mounting pad and its tapped holes), the front crossmember (P9: its angled brackets) and the
mountings themselves. Car frame as mgb.car_layout.

What Haynes fixes (Fig 1.29): a mounting bracket each side (RH and LH, differently fixed: screws 3 RH, 5 LH), a
bonded rubber mounting each side (10 RH, 11 LH) with nuts and spring washers, packing plates (39) on the
crossmember's brackets; the inset shows the bracket's V-shaped lower end.

Derived (D): every station below. The rubbers stand on the crossmember's two angled pads either side of the sump,
facing up and inboard at 40 deg; each engine bracket is a pressing with a vertical plate and the V-shaped flange
the rubber's upper studs pass through; the left-hand bracket's plate is screwed to a pad on the block's left wall,
the right-hand bracket is held by a tab behind the front plate's right-hand wing (P2 drilled the wing for it,
parts/engine/block/plates.py MOUNT_HOLES).
"""
from __future__ import annotations

import math

from mgb import front_suspension_layout as FS

PAD = FS.ENGINE_MOUNT_PAD                          # crossmember pad face centre (x, |y|, z)
ANGLE = FS.ENGINE_MOUNT_ANGLE
_a = math.radians(ANGLE)
N = (0.0, -math.sin(_a), math.cos(_a))             # pad normal, left-hand side: up and inboard
U = (0.0, math.cos(_a), math.sin(_a))              # up the slope, outboard
PACKING_T = 3.0
PLATE_T = 3.0
RUBBER_T = 30.0
BRACKET_T = 3.5
STACK = PACKING_T + PLATE_T + RUBBER_T + PLATE_T   # pad face to the bracket flange's underside
STUD_DX = 13.0                                     # studs fore and aft of the centre (crossmember pad holes)
RUBBER_W = (60.0, 58.0)                            # along x, along the slope


def along(p, d, k):
    return tuple(p[i] + d[i] * k for i in range(3))


def side(s, p):
    return (p[0], s * p[1], p[2])


def n_of(s):
    return (N[0], s * N[1], N[2])


def u_of(s):
    return (U[0], s * U[1], U[2])


FLANGE_C = along(PAD, N, STACK)                    # bracket flange underside centre (left)
FLANGE_LOW = along(FLANGE_C, U, -RUBBER_W[1] / 2 - 4.0)   # the V's bottom edge, where the plate meets the flange
PLATE_Y = FLANGE_LOW[1] - BRACKET_T * 0.5          # bracket's vertical plate, inner face |y|
PLATE_X = (PAD[0] - 30.0, PAD[0] + 18.0)
PLATE_TOP_Z = -196.0
LH_PAD_Z = (-256.0, -200.0)                        # pad on the block's left wall the plate screws to (P2 casting)
LH_SCREWS = [(PAD[0] - 6.0, -212.0), (PAD[0] - 6.0, -244.0)]   # (x, z), 3/8 UNC into the block
RH_TAB_X = (226.4, 229.6)                          # tab behind the front plate wing (wing rear face x 230)
