"""Gearbox bellhousing datums (engine frame) for the clutch release gear, set in P4 so the
P5 bellhousing is built to match. Early (three-synchro) gearbox, 1963.

What Haynes fixes (Ch 5, printed p109-110): the slave cylinder is on the right-hand side of
the bellhousing, held by two bolts and spring washers (Sec 6 para 1); the withdrawal lever
pivots on a bolt with a washer and locknut and passes out through a dust cover (Sec 7
para 3, photo 7.3); the release bearing sits in the lever's fork, held by two spring clips
turned through 90 degrees (Sec 7 para 2, photo 7.1b).

Derived (D):
- Bellhousing front face on the gearbox face of the engine rear plate, bolted through the
  plate's bellhousing holes (parts/engine/block/plates.py BELL_HOLES); input shaft axis on
  the crank axis.
- Lever pivot: a vertical bolt between two lugs on the right of the gearbox front cover
  (photo 7.3; mgaguru.com gt110, MGA: "a pivot bolt attached to the gearbox front cover").
  The fork is a half ring round the right of the bearing whose ends sit on the cup's
  trunnion pins at 12 and 6 o'clock (Fig 5.1 item 8; photo 7.1b shows the two clips either
  side of the bearing). P5: the two lugs sit above and below the lever boss
  (PIVOT_LUG_Z, PIVOT_LUG_T), clear of the fork ring.
- The outer arm leaves through an opening in the right-hand wall and sweeps back to the
  slave cylinder pushrod. The slave cylinder lies along the car ahead of the lever end, so
  its pushrod pushes the lever end rearward and the fork forward onto the release plate.
- The slave cylinder flange bolts to the rear face of a pad cast on the right-hand wall; the
  cylinder body passes forward through the pad's bore.
"""
from __future__ import annotations

from pathlib import Path

from mgb import clutch_layout as K, engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parent.parent
_EL = E.layout(head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml")))
_EP = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "block" / "end-plate.yaml")}
_BL = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "block" / "block.yaml")}

AXIS_Y, AXIS_Z = 0.0, _EL.crank_z                   # first motion shaft axis = crank axis
_X0 = -_BL["engine.block.casting"].nom("length") / 2
BELL_FACE_X = (_X0 - _EP["engine.block.rear-plate-gasket"].nom("thickness")
               - _EP["engine.block.rear-plate"].nom("thickness"))      # gearbox face of the rear plate
BELL_DEPTH = 160.0                                   # front face to the gearbox front face (D)
BELL_REAR_X = BELL_FACE_X - BELL_DEPTH
BELL_MAX_R = 172.0                                   # bolt circle radius of the flange; the bell shell itself is 163 (P5a) (D)

# withdrawal lever (Sec 7)
PIVOT = (K.TRUNNION_X, -75.0, AXIS_Z)                # pivot bolt centre, axis vertical
PIVOT_AXIS = (0.0, 0.0, 1.0)
PIVOT_BOSS_R = 13.0                                  # lever boss round the bush
PIVOT_LUG_Z = 13.0                                   # gap between the two lugs is 2 x this (the boss height)
PIVOT_LUG_T = 10.0                                   # lug thickness above and below
YOKE_R = K.TRUNNION_R                                # the fork is a half ring round the right of the bearing
LEVER_END = (K.TRUNNION_X - 36.0, -205.0, AXIS_Z)    # slave pushrod clevis pin, axis vertical
LEVER_WALL_Y = -158.0                                # the lever leaves through the right-hand wall here


def lever_point(y):
    """Point on the outer arm's centre line (pivot to lever end) at a given y."""
    t = (y - PIVOT[1]) / (LEVER_END[1] - PIVOT[1])
    return (PIVOT[0] + t * (LEVER_END[0] - PIVOT[0]), y, AXIS_Z)


LEVER_PORT = lever_point(LEVER_WALL_Y)               # opening in the wall, dust cover over it
_dx, _dy = LEVER_END[0] - PIVOT[0], LEVER_END[1] - PIVOT[1]
LEVER_DIR = (_dx / (_dx ** 2 + _dy ** 2) ** 0.5, _dy / (_dx ** 2 + _dy ** 2) ** 0.5, 0.0)

# slave cylinder (Sec 6)
SLAVE_Y, SLAVE_Z = LEVER_END[1], LEVER_END[2]        # cylinder axis, along X
SLAVE_PAD_X = LEVER_END[0] + 48.0                    # rear face of the pad the flange bolts to
SLAVE_BOLT_DZ = 30.0                                 # two flange bolts above and below the axis
SLAVE_BORE_IN_PAD = 34.0                             # bore in the pad the body passes through (D)


# =================================================================================================
# P5a: the gearbox itself (Haynes Ch 6, early three-synchro box with Laycock type D overdrive).
#
# What Haynes fixes: ratios 3.64, 2.21, 1.37, 1.00, reverse 4.76 (Ch 6 specs, printed p111);
# the parts and their order (Fig 6.3, p114-115; Fig 6.4 remote control, overdrive fitted, p116);
# the casing and bellhousing are one casting (Fig 6.3 item 1); on overdrive cars the overdrive
# casing comes off the "gearbox extension" on eight nuts on 1/4 in studs, one stud longer, and
# the mainshaft runs on into the overdrive (Sec 11 paras 3-5); the speedometer drive is in the
# overdrive rear casing on these cars (Fig 6.13 items 78, 88, 89), so it is not on the gearbox.
#
# Tooth counts (S): MGA 1600 / early MGB standard ratio box, mgaguru.com gt102a: constant mesh
# 21/30, third 25/26, second 31/20, first 28/11, reverse idler 17/13 - they give exactly the
# Haynes ratios. First and reverse are straight cut; the others are helical (Haynes photos 4.21a,
# 4.22 and 4.24b show helical teeth on the mainshaft and laygear).
#
# Everything else here is derived (D). The gearbox frame used to build the internals:
# GF puts local z rearward along the mainshaft from the casing front face (d below), local x
# up, local y to the car's left, like the clutch frame.
# =================================================================================================
from build123d import Location as _Loc, Rot as _Rot   # noqa: E402

IN = 25.4
CASE_FRONT_X = BELL_REAR_X                       # gearbox front face inside the bellhousing (front cover joint)
GF = _Loc((CASE_FRONT_X, AXIS_Y, AXIS_Z)) * _Rot(0, -90, 0)


def gx(d):
    """Car x of a station d mm rearward of the casing front face."""
    return CASE_FRONT_X - d


def to_local(p):
    """Car point (x, y, z) -> gearbox frame (up, left, d)."""
    return (p[2] - AXIS_Z, p[1] - AXIS_Y, CASE_FRONT_X - p[0])


# ---- gear train geometry (D: tooth counts S above; pitches chosen so the 39-tooth first-gear pair
# and the 51-tooth helical pairs share one centre distance) -----------------------------------------
M_SPUR = IN / 8                                  # first and reverse: 8 DP, 20 deg
MN_HEL = IN / 12                                 # helical normal module: 12 DP normal
C_LAY = 39 * M_SPUR / 2                          # mainshaft to layshaft centres, 61.9 mm
MT_HEL = 2 * C_LAY / 51                          # helical transverse module
import math as _m                                # noqa: E402
BETA = _m.degrees(_m.acos(MN_HEL / MT_HEL))      # helix angle, about 29 deg
TEETH = {"constant": (21, 30), "third": (25, 26), "second": (31, 20), "first": (28, 11), "reverse": (17, 13)}
LAY_UP = -C_LAY                                  # layshaft axis: straight below the mainshaft (local x)
# reverse idler: meshes the laygear first gear (17 on 11) and the mainshaft first gear (13 on 28)
_r1, _r2 = (17 + 11) * M_SPUR / 2, (13 + 28) * M_SPUR / 2
_u = (_r1 ** 2 - _r2 ** 2 - C_LAY ** 2) / (2 * C_LAY)          # local x of the idler axis
REV_UP, REV_LEFT = _u, _m.sqrt(_r2 ** 2 - _u ** 2)             # left side, under the selector rods

# ---- stations along the mainshaft, d rearward from CASE_FRONT_X (D) ------------------------------
FRONT_WALL = 14.0                                # casing front wall thickness
FMS_BRG = (-2.0, 19.0)                           # first motion shaft bearing, proud of the face under the cover
CM_GEAR = (20.0, 44.0)                           # constant mesh gear (first motion shaft)
FMS_DOG = (44.0, 49.5)                           # fourth gear dog teeth
FMS_CONE = (49.5, 58.5)                          # fourth gear synchro cone
FMS_END = 59.0
SYN34 = (62.0, 90.0)                             # 3rd/4th synchroniser hub (sleeve slides +/- 9)
TW98 = (98.0, 102.0)                             # third gear locking thrust washer, inside the third gear cone
G3 = (93.0, 129.0)                               # third gear: cone 93-102 and dogs 102-107.5 at the front
G3_TEETH = (107.5, 129.0)
RING107 = (129.0, 132.5)                         # interlocking ring between the bushes
G2 = (132.5, 166.0)                              # second gear: teeth 132.5-154, dogs and cone behind
G2_TEETH = (132.5, 154.0)
SYN12 = (167.0, 221.0)                           # 1st/2nd hub; first gear (the outer member) slides on it
G1 = (167.0, 196.0)                              # first gear in neutral: fork collar 167-177, teeth 179-196
G1_TEETH = (179.0, 196.0)
G1_TRAVEL = (-9.0, 25.0)                         # forward to the second gear dogs, back into mesh with the laygear
TW97 = (221.0, 225.0)
CTR_BRG = (228.0, 248.0)                         # centre bearing in its housing in the rear wall
CASE_LEN = 250.0                                 # front face to rear face
REAR_WALL = 10.0
CASE_REAR_X = gx(CASE_LEN)
LAY = {"constant": (20.0, 44.0), "third": (107.5, 129.0), "second": (132.5, 154.0), "first": (198.0, 223.5)}
LAY_ENDS = (18.0, 223.9)                         # laygear body ends (thrust washers outside these)
REV_POS = (196.5, 223.5)                         # reverse idler in neutral: 13 tooth 196.5-207, groove, 17 tooth 212.5-223.5
REV_TRAVEL = 18.0                                # slides forward into mesh with first gear
REV_SHAFT_D = (160.0, CASE_LEN)                  # reverse shaft: front boss to the rear wall

# ---- selector rods (left, high), detent block on the rear face (D) -------------------------------
ROD_UP = 62.0
ROD_LEFT = {"first-second": 24.0, "third-fourth": 40.0, "reverse": 56.0}
ROD_D = 0.4375 * IN                              # 7/16 in rods

# ---- casing exterior (D) -------------------------------------------------------------------------
CASE_TOP = 92.0                                  # local x of the top face
CASE_BOTTOM = -112.0                             # sump bottom under the laygear
CASE_LEFT = 104.0                                # left (side cover) face
CASE_RIGHT = -84.0
SIDE_COVER_D = (40.0, 200.0)                     # side cover opening along the case
SIDE_COVER_UP = (-70.0, 72.0)

# ---- overdrive "gearbox extension" (adaptor) and the face the overdrive bolts to (for P5b) -----------
ADAPTOR_LEN = 76.0
JOINT_T = 0.8                                    # paper joint between the casing and the adaptor, and under the remote housing
AD_END = CASE_LEN + JOINT_T + ADAPTOR_LEN        # d of the adaptor's rear face
OD_FACE_X = gx(AD_END)                           # rear face of the adaptor: overdrive main casing joint (gasket 37H1901 on it)
OD_STUD_R = 78.0                                 # eight 1/4 in UNF studs (Sec 11 para 3), one long
OD_STUD_ANGLES = [22.5 + 45.0 * k for k in range(8)]       # from up toward left, local frame
OD_STUD_LONG = 2                                 # index of the long stud (upper left)
OD_STUD_SIZE = "1/4"
OD_SPIGOT_R = 56.0                               # register bore the overdrive front casing enters
OD_OIL_PORT = (OD_FACE_X, AXIS_Y, AXIS_Z - 82.0)  # oil passes to the overdrive pump filter through the adaptor bottom
# mainshaft tail in the overdrive (D, from Fig 6.11/6.12: cam keyed on the shaft for the pump, splines for
# the clutch and planet carrier, the tail running in the needle bearing in the output shaft)
MS_TAIL_R = 0.875 * IN / 2                       # plain shaft through the adaptor
MS_CAM_D = (AD_END + 22.0, AD_END + 44.0)   # cam seat with a 1/2 in Woodruff keyway
MS_CAM_R = 0.875 * IN / 2
MS_SPLINE_D = (AD_END + 70.0, AD_END + 150.0)
MS_SPLINE = (24, 0.875 * IN, 0.78 * IN)          # count, major, minor diameter
MS_PILOT_D = (AD_END + 150.0, AD_END + 182.0)
MS_PILOT_R = 0.5 * IN / 2
MS_END_X = gx(MS_PILOT_D[1])

# ---- remote control (Fig 6.4) and the gear lever in the car (D) ---------------------------------
REMOTE_D = (CASE_LEN + 6.0, CASE_LEN + 205.0)    # remote control housing, front to rear
SEL_SHAFT_UP, SEL_SHAFT_LEFT = 118.0, 40.0       # selector lever shaft, along the car above the selectors
SEL_D = (272.0, 290.0)                           # selectors on the rod ends, behind the detent block
FINGER_D = (277.0, 285.0)                        # front selector lever finger in the selector slots
REMOTE_BOTTOM_UP = 96.0                          # underside of the remote housing behind the adaptor (P5b: keep the overdrive below)
LEVER_BALL_D = CASE_LEN + 178.0                  # gear lever ball centre
LEVER_BALL_UP = 135.0
LEVER_BALL = (gx(LEVER_BALL_D), AXIS_Y, AXIS_Z + LEVER_BALL_UP)
KNOB = (LEVER_BALL[0] - 70.0, AXIS_Y, AXIS_Z + LEVER_BALL_UP + 215.0)    # knob centre, in the cockpit
# support bracket (Fig 6.4 item 39) under the remote housing's rear feet: its two lower lugs bolt down
# to bosses P5b must provide on the overdrive main casing, at this height and these left offsets,
# at station REMOTE_BRACKET_D
REMOTE_BRACKET_D = REMOTE_D[1] - 8.0
REMOTE_BRACKET_UP = 70.0
REMOTE_BRACKET_HOLES = [-53.0, 87.0]
REMOTE_FEET_LEFT = (-34.0, 68.0)                 # the remote housing's two rear feet on the bracket
