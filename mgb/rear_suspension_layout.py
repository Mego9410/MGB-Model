"""Rear suspension (P9): semi-elliptic leaf springs, their mountings to the axle and the body, the lever dampers
and links, the bump rubbers and the rebound straps. Datums for the body phase (P11): spring front hangers, rear
shackle brackets, damper mounting faces, rebound strap bolts and the bump rubber strike faces.

Car frame as mgb.car_layout. The axle's own datums (spring seats, U-bolt positions, pedestal seats, rebound
strap spindles) are in mgb.rear_axle_layout; this module only adds what hangs off them.

What Haynes fixes (Ch 11, printed p202, 207-208, Figs 11.4 and 11.5): semi-elliptic leaf springs, rubber mounted;
early models five leaves plus a bottom plate; the order through the U-bolts - bump rubber pedestal (17) on the
axle, the locating plate (18) and spring seating pad (19) each side of the spring, the damper attachment
bracket (20) under it, eight locknuts and nuts (16) per spring; the front eye on an eyebolt (21) with nut and
spring washer (22, 23) through a bush (2); the rear eye on a shackle - the shackle and pin plate (10), shackle
plate (11), rubber bushes (12), nuts and spring washers (13, 14); the centre bolt (4) with nut and locknut
(6, 7); clips on the third and fourth leaves (8, 9); the rebound strap (24) on a bolt and tube at the body
(25, 29-31) and the axle spindle with plain and spring washers and nut (26-28); the hydraulic lever damper on
the body side member by two bolts, its link to the bracket on the spring (Fig 11.5); rear damper arm centres
5 1/4 in (133 mm).

Derived (D), not published: every station below. The axle sits a little forward of the spring's centre (eye
centres 22.5 in ahead of and 24 in behind the centre bolt, 46.5 in in all); the spring carries about 25 mm of
camber at the front eye laden; leaves 1 3/4 in wide (P7 SPRING_W) and 7/32 in thick; dampers ahead of the axle
(their filler plugs are reached from inside the car behind the seats: Haynes photo 2.4, "access grommet for
rear hydraulic shock absorbers, adjacent to the battery access apertures"), the link to the bracket's pin
inboard of the spring and ahead of the axle tube.
"""
from __future__ import annotations

from mgb import car_layout as CL, rear_axle_layout as A

IN = 25.4
AX, AZ = A.AX, A.AZ

# ---- spring -----------------------------------------------------------------------------------------------
SPRING_Y = A.SPRING_Y                         # 420
LEAF_W = A.SPRING_W                           # 1 3/4 in
LEAF_T = 7.0 / 32.0 * IN                      # 5.556 (D)
N_LEAVES = 5                                  # H p202: early models 5 plus bottom plate
BOTTOM_PLATE_T = 0.25 * IN
PLATE18_T = 3.0                               # locating plate
PAD19_T = 5.0                                 # rubber seating pad
SEAT_Z = AZ + A.SEAT_FACE_Z                   # underside of the axle's spring seat (car z)
TOP_Z = SEAT_Z - PLATE18_T - PAD19_T          # main leaf top at the centre bolt
FRONT_HALF = 22.5 * IN                        # eye centre ahead of the centre bolt
REAR_HALF = 24.0 * IN
FRONT_RISE = 25.0                             # main leaf top at the front eye, above TOP_Z (laden camber)
K_CAMBER = FRONT_RISE / FRONT_HALF ** 2       # leaf top: z = TOP_Z + K x^2 (x from the centre bolt)
EYE_R_IN = 1.125 * IN / 2                     # eye bore for the bushes
STACK_T = N_LEAVES * LEAF_T + BOTTOM_PLATE_T
BOTTOM_Z = TOP_Z - STACK_T                    # spring underside at the centre


def leaf_top(x):
    """Main leaf top surface height at x (from the centre bolt, + forward)."""
    return TOP_Z + K_CAMBER * x * x


def eye_centre(x):
    return leaf_top(x) - LEAF_T / 2 + EYE_R_IN + LEAF_T / 2


FRONT_EYE = (AX + FRONT_HALF, SPRING_Y, eye_centre(FRONT_HALF))
REAR_EYE = (AX - REAR_HALF, SPRING_Y, eye_centre(-REAR_HALF))
LEAF_HALF = [(FRONT_HALF, REAR_HALF), (FRONT_HALF - 22.0, REAR_HALF * 0.86), (FRONT_HALF * 0.70, REAR_HALF * 0.70),
             (FRONT_HALF * 0.53, REAR_HALF * 0.53), (FRONT_HALF * 0.36, REAR_HALF * 0.36), (FRONT_HALF * 0.16, REAR_HALF * 0.16)]
                                              # (front, rear) lengths from the centre bolt: leaves 1-5 and the bottom plate
CLIPS = {3: (0.92, 0.92), 4: (0.9, 0.9)}      # clip positions on leaves 3 and 4, as fractions of their half lengths

# rear shackle: upper pin above and a little behind the eye (P11 builds the body bracket on SHACKLE_TOP)
SHACKLE_L = 3.5 * IN
SHACKLE_TOP = (REAR_EYE[0] - 14.0, SPRING_Y, REAR_EYE[2] + (SHACKLE_L ** 2 - 14.0 ** 2) ** 0.5)
SHACKLE_PIN_D = 0.5 * IN
EYEBOLT = "1/2"
BUSH_FLANGE_T = 3.0

# ---- U-bolts, plates, pads, bracket, pedestal -------------------------------------------------------------------
UBOLT = "7/16"
UBOLT_DY = 34.0                               # legs either side of the spring (P7's 30 mm left the legs in its seat's sides)
PEDESTAL_T = 3.0
UBOLT_ROD_R = 7.0 / 16.0 * IN / 2
UBOLT_R = A.TUBE_R + PEDESTAL_T + UBOLT_ROD_R  # bend centre line radius over the pedestal
UBOLT_X = UBOLT_R                              # legs fore and aft of the tube
LOWER_STACK_TOP = BOTTOM_Z                     # spring underside: lower pad, lower plate, bracket below it
BRACKET_T = 3.5
BRACKET_UNDER_Z = BOTTOM_Z - PAD19_T - PLATE18_T - BRACKET_T
UBOLT_END_Z = BRACKET_UNDER_Z - 22.0
PEDESTAL_TOP_Z = AZ + A.TUBE_R + 26.0          # bump rubber seat on the pedestal
BUMP_H = 44.0
BUMP_GAP = 52.0                                # static gap to the body (D)
BUMP_STRIKE = {s: (AX, s * SPRING_Y, PEDESTAL_TOP_Z + BUMP_H + BUMP_GAP) for s in (1, -1)}   # P11: body underside

# ---- damper (Fig 11.5) and link ---------------------------------------------------------------------------------
DAMPER_ARM = 5.25 * IN                        # H p202: rear arm centres 5 1/4 in (133 mm)
LINK_X = AX + 52.0                            # link ahead of the axle tube
LINK_Y = 358.0                                # link and arm plane, inboard of the spring
LINK_LOW_Z = BRACKET_UNDER_Z - 8.0            # pin on the bracket (20)
DAMPER_SHAFT = (LINK_X + DAMPER_ARM, None, -240.0)   # shaft along y; arm level, pointing rearward to the link
LINK_TOP_Z = DAMPER_SHAFT[2]
DAMPER_FACE_Y = 436.0                         # body mounting face (P11: side member's inner face)
DAMPER_BOLTS = [(DAMPER_SHAFT[0] - 80.0, DAMPER_SHAFT[2] + 30.0), (DAMPER_SHAFT[0] + 74.0, DAMPER_SHAFT[2] + 30.0)]
                                              # (x, z) of the two retaining bolts, along y through the face
BRACKET_WEB_Y = (366.0, 369.5)

# ---- rebound strap (24) -------------------------------------------------------------------------------------------
STRAP_LOW = A.REBOUND_EYE                      # {side: car point}, on the spindle (along y)
STRAP_TOP_DX = -63.0                           # upper eye behind the lower one, clear of the axle tube
STRAP_LEN = 246.0
STRAP_TOP = {s: (STRAP_LOW[s][0] + STRAP_TOP_DX, STRAP_LOW[s][1],
                 STRAP_LOW[s][2] + (STRAP_LEN ** 2 - STRAP_TOP_DX ** 2) ** 0.5) for s in (1, -1)}   # P11: bolt 29


def side_pt(s, p):
    return (p[0], s * p[1], p[2])


# ---- datums for P11 (car frame, per side) ---------------------------------------------------------------------
FRONT_HANGER = {s: side_pt(s, FRONT_EYE) for s in (1, -1)}         # eyebolt axis (along y) through the hanger plates
SHACKLE_BRACKET = {s: side_pt(s, SHACKLE_TOP) for s in (1, -1)}    # upper shackle pin (along y) through the bracket
DAMPER_MOUNT = {s: [(x, s * DAMPER_FACE_Y, z) for x, z in DAMPER_BOLTS] for s in (1, -1)}   # bolts along y
REBOUND_BOLT = STRAP_TOP
