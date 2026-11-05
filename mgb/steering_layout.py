"""Steering datums (P9): rack-and-pinion RHD, the column and the steering wheel, and the body datums for the
column clamps (P11). Car frame as mgb.car_layout.

What Haynes fixes (Ch 11, printed p202-203, 209-213, Figs 11.6 and 11.8): rack and pinion bolted to the
crossmember by two brackets with shims (0.020 in) on the crossmember's mounting bosses; the tie-rods on ball
joints at the rack ends locked by the ball housings and locknuts, rubber gaiters with clips; outer ball joints
with self-locking nuts in the steering levers; the column (inner and outer, RHD) with its upper and lower
bearings, held by the upper clamp (59) to a body bracket with packing washers and a bottom bracket (65) at the
toe board with a blanking plate and draught excluder (69); one universal joint to the pinion, pinch bolts
through the splines' cut-outs (Sec 17 para 3); the column must line up with the pinion - the alignment gauges
on the pinion shaft and the column meet at their points (Sec 20 paras 4-6, Fig 11.8), so the pinion and
column are drawn on one axis; turns lock to lock 2.93 (early); turning circle 32 ft; steering wheel nut 41-43
lbf ft. MGOC Spares: the original 1962-69 wheel is a 16 1/2 in three-spoke banjo wheel, black rim and hub,
central horn push with the MG badge.

Derived (D), not published: every station below. The rack lies ahead of the crossmember on its bosses with
the pinion on the right (RHD); the column runs back from the pinion, beside the engine, through a tube in
the right-hand tower of the (RHD) crossmember and the toe board, to the wheel in front of the driver. The
driver's centre line is P10's (body_layout.DRIVER_Y, under the instruments); the wheel centre is about 590 mm
above the road (a low seat; the rim top under the instruments) so that the column passes under P8's pedal box
and master cylinder pipe at the bulkhead.
"""
from __future__ import annotations

import math

from mgb import car_layout as CL, front_suspension_layout as FS

IN = 25.4

# ---- rack ------------------------------------------------------------------------------------------------------
RACK_X, RACK_Z = FS.RACK_AXIS
HOUSING_R = 19.0                                     # rack housing tube outside radius
HOUSING_Y = (-318.0, 318.0)                          # housing tube end faces
RACK_R = 11.1                                        # rack bar (7/8 in)
INNER_BALL_Y = 340.0                                 # |y| of the inner ball joints (ball housing on the rack end)
BALL_HOUSING_Y = (HOUSING_Y[1] + 4.0, INNER_BALL_Y + 12.0)
TIE_ROD_R = 7.9
OUTER_BALL = (FS.ARM_BALL[0], FS.ARM_BALL[1], FS.ARM_BALL[2] - 22.0)   # ball centre in the outer joint, under the lever
OUTER_SHANK_Y = 474.0                                # tie-rod end of the outer joint's shank (|y|)
RACK_TRAVEL = 2.93 / 2 * 2 * math.pi * 16.0          # lock to lock / 2 (H 2.93 turns; pinion pitch radius 16 mm, D)
PINION_PITCH_R = 16.0
PINION_TEETH = 7

# ---- pinion and column, one axis (Sec 20: the alignment gauges meet) -------------------------------------------
PINION_Y = -278.0
PINION_MESH = (RACK_X, PINION_Y, RACK_Z + RACK_R + PINION_PITCH_R + 4.0)   # where the pinion axis passes over the rack
from mgb import body_layout as BL  # noqa: E402  (P10: facia, instruments over the column)
# The wheel is placed on Oliver's car (QA fix round 1, cockpit): a circle fitted to 678 points of the rim in his body
# scan (mgb.scan_layout registration) has its centre at x -981, y -294, 830 mm above the road, radius 198.8 (the
# 16 1/2 in rim's centre line) and its axis 20 deg to the horizontal. The rim centre is held; the hub face lies
# DISH mm ahead of it on the one pinion/column axis (Sec 20), which then rises at about 24 deg. The wheel sits
# 56 mm inboard of P10's driver line (the binnacle's centre), as in the scan.
RIM_CENTRE = (-981.0, -294.0, CL.GROUND_Z + 830.0)       # D: Oliver's body scan, rim circle fit
DISH = 62.0                                              # rim plane above (toward the driver) the hub face
_r = [RIM_CENTRE[i] - PINION_MESH[i] for i in range(3)]
_rl = math.sqrt(sum(v * v for v in _r))
WHEEL_CENTRE = tuple(RIM_CENTRE[i] - DISH * _r[i] / _rl for i in range(3))   # steering wheel centre (hub face plane)
_d = [WHEEL_CENTRE[i] - PINION_MESH[i] for i in range(3)]
_L = math.sqrt(sum(v * v for v in _d))
COLUMN_DIR = tuple(v / _L for v in _d)               # up the column, rearward


def col(t):
    """Point on the pinion/column axis, t mm up from the pinion's mesh point."""
    return tuple(PINION_MESH[i] + t * COLUMN_DIR[i] for i in range(3))


def t_at_x(x):
    return (x - PINION_MESH[0]) / COLUMN_DIR[0]


PINION_T = (-34.0, 70.0)                             # pinion from its lower end (end cover) to its splined top
PINION_TEETH_T = (-14.0, 14.0)
PINION_HOUSING_T = (-44.0, 46.0)
UJ_T = PINION_T[1] + 18.0                            # universal joint centre
COLUMN_T0 = UJ_T + 18.0                              # inner column's lower splined end
OUTER_TUBE_T = (t_at_x(150.0), t_at_x(WHEEL_CENTRE[0] + 70.0))
TOE_BOARD_T = t_at_x(CL.BULKHEAD_X - 40.0)           # bottom bracket (65) and draught excluder (69)
UPPER_CLAMP_T = t_at_x(-780.0)                       # column clamp (59) under the dash
WHEEL_T = _L
COLUMN_TOP_T = WHEEL_T + 22.0                        # threaded top for the wheel nut
OUTER_TUBE_R = 0.75 * IN                             # 1 1/2 in outer tube (D)
INNER_SHAFT_R = 0.375 * IN                           # 3/4 in inner column (D)
CROSSMEMBER_TUBE_R = 36.0                            # tube through the RHD crossmember's right tower

# ---- steering wheel (MGOC: 16 1/2 in three-spoke banjo wheel) ---------------------------------------------------
WHEEL_D = 16.5 * IN
RIM_SECTION = (22.0, 26.0)                           # rim grip section: across, along the axis
SPOKES = 3
SPOKE_ANGLES = [105.0, 180.0, 255.0]                 # from the wheel's "up" toward the driver's left, wheels straight
                                                     # ahead (D: Oliver's kf121, kf148 - two side spokes 15 deg below
                                                     # the horizontal and one straight down)
SPOKE_WIRES = [3, 2, 3]                              # polished spring steel wires per spoke (D: kf121, kf148)
WIRE_R = 2.0                                         # wire radius (D: kf121 scaled on the rim)
HUB_ARM_R = [78.0, 60.0, 78.0]                       # reach of the black cast hub's arms (wire sockets) per spoke (D)
CLAMP_LEN = 34.0                                     # black clamp blocks where the wires meet the rim (D)

# ---- body datums for P11 (car frame) -------------------------------------------------------------------------------
COLUMN_TOP_CLAMP = col(UPPER_CLAMP_T)                # upper clamp (59) on the body bracket under the dash; packing washers
COLUMN_TOE_PLATE = col(TOE_BOARD_T)                  # bottom bracket (65) on the toe board, blanking plate, excluder (69)
