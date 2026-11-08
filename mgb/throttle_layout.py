"""Accelerator and choke (mixture) controls, car frame (mgb.car_layout: X forward, Y to the car's left, Z up,
origin on the engine centreline at the head joint face).

Sources. Haynes Ch 3: Fig 3.10 (HS4 installation, printed p73) items 35-72, Fig 3.13 (throttle lever adjustment, p76:
the feeler between the throttle shaft lever's stop and the choke interconnecting spindle), Sec 17 photo 17.1(b) (p72:
the return springs hooked down to the heat shield's turned-out lip), Sec 21 (p76: the folded clamps on the
interconnecting shaft, the 0.012 in clearance, the 1/16 in free movement of the choke wire), Sec 45 (p92: pedal pivot
bolt, split pin at the pedal's end); Ch 12 Sec 47 para 4 (p232: the choke cable nut behind the facia, the cable freed
from the air cleaner bracket on early cars). Factory parts list (F: MGB service parts list plates 108-G2 and 108-G4,
chassis 101 to 138400, barneymg.chicagolandmgclub.com spl_mgb_203-214.pdf): RHD accelerator pedal AHC135 on a pivot
bolt and distance tube AHH6504, rubber pad GPR105, RHD pedal stop AHB7162 with its stop screw and locknut, accelerator
cable guide AHH5308 on the bulkhead (gasket ACA5073), accelerator cable AHH6997 (RHD), choke cable, choke control
bracket AHH6731 and outer cable abutment AHH6734. Supplier listings (S: Rimmer Bros GRID019709, MGOC Spares
"accelerator choke cables"): the throttle cable P-clipped to the pedal box cover on single-line cars (PCR307), three
HS4 return springs AEC2075, the cable swivel pin ACC5062 with anti-rattle washer ACA5256, the choke trunnion and 5BA
screw (AUE34, 53K3503), the early round choke knob with its "C" (1962-69), the choke grommet 14A7033.

Derived (D): every position below. The pedal hangs from a bracket on the cabin face of the bulkhead outboard of the
brake pedal and the steering column, the inner cable on the short arm above the pivot, so pressing the pad draws the
inner rearward out of the guide; the outer runs from the guide's nose on the engine side up outboard of the pedal box,
over its cover, behind the cylinder head and forward between the rocker cover and the dashpots to an abutment bracket
on the heat shield between the instruments (Fig 3.13 draws the cable coming down to the shaft lever there). The choke
cable shares the bracket and the run, then crosses the bulkhead through its grommet to the facia knob.
"""
from __future__ import annotations

from mgb import body_layout as BL, car_layout as C, carb_layout as K, underbody_layout as U
from mgb.clutch_layout import PEDAL_BOX_RAISE

IN = 25.4
PANEL_T = 1.2                                          # body panels (parts/body/structure.py T)
BH = C.BULKHEAD_X                                      # bulkhead engine-side face (-400)
CAB = BH - PANEL_T                                     # its cabin face

# ---- accelerator pedal (cabin) ---------------------------------------------------------------------------------
PEDAL_Y = -412.0                       # pedal mid-plane: outboard of the column (y -319 at the toe board) and the
                                       # brake pedal (y -290), clear of the fuel pipe's run up the bulkhead (y -385)
PEDAL_T = 6.0                          # pressed arm thickness (along y)
PIVOT = (CAB - 27.0, PEDAL_Y, -156.0)  # pivot bolt axis (along y)
CABLE_END = (CAB - 27.0, PEDAL_Y, -128.0)   # inner cable through the pedal's top end, split pin behind (Sec 45 para 1)
# QA fix round 1, cockpit: the foot stub where Oliver's kf151 and kf152 show it, just outboard of the brake pad (SfM
# cameras, solved for y at the stub's x and height: -485 and -500); the arm steps outboard to it below the pivot
# (ARM[2]), so the pivot, the cable and its guide keep PEDAL_Y. P3b had the stub on PEDAL_Y.
PAD_Y = -490.0
PAD = (-540.0, PAD_Y, -318.0)          # centre of the pad face, 60 mm above the carpet
PAD_TILT_DEG = 35.0                    # pad face normal: rearward, tipped up by this
ARM = [PIVOT[::2], (-436.0, -205.0), (-468.0, -262.0)]   # (x, z) arm centre line from the pivot toward the foot plate
BRACKET_Y = (PEDAL_Y + PEDAL_T / 2 + 1.0, PEDAL_Y + PEDAL_T / 2 + 3.0)   # pivot bracket cheek, inboard of the pedal
TOE_T = PANEL_T


def toe_top_z(x):
    """Cabin face of the toe board at x (underbody_layout.toe_z is its underside)."""
    return U.toe_z(x) + TOE_T


_tn = (-(U.TOE_TOP[1] - U.TOE_FOOT[1]), U.TOE_TOP[0] - U.TOE_FOOT[0])
_tl = (_tn[0] ** 2 + _tn[1] ** 2) ** 0.5
TOE_N = (_tn[0] / _tl, _tn[1] / _tl)   # (x, z) unit normal out of the toe board into the footwell (rearward, up)
TOE_U = (TOE_N[1], -TOE_N[0])          # (x, z) up the toe board's slope (forward, up)
STOP_BASE_X = -470.0                   # pedal stop's boss on the toe board near its foot, ahead of the arm
STOP_BASE = (STOP_BASE_X, toe_top_z(STOP_BASE_X))
STOP_FIX_ALONG = (20.0, 38.0)          # its two fixing screws up the slope from the boss
STOP_LIFT = 10.5                       # the stop sits on the toe board's carpet (body.interior: 6 mm, 3.5 mm off the board)
STOP_SCREW_OUT = 27.0                  # stop screw head this far out of the carpet along TOE_N: 5 mm short of the
                                       # arm at rest (the full-throttle travel is not modelled, D)

# ---- accelerator cable guide (bulkhead) -------------------------------------------------------------------------
GUIDE = (BH, PEDAL_Y, CABLE_END[2])    # guide hole centre on the bulkhead's engine-side face
GUIDE_FLANGE_R = 15.5
GUIDE_NOSE = 20.0                      # nose (outer abutment) length forward of the flange
GUIDE_SCREWS = [(PEDAL_Y, CABLE_END[2] - 11.5), (PEDAL_Y, CABLE_END[2] + 11.5)]   # (y, z), above and below the hole

# ---- carburettor linkage (engine frame = car frame) -------------------------------------------------------------
FRONT, REAR = K.CARB_X
SPINDLE_LEN = 130.0                    # throttle spindle (carburettors.yaml): inboard end 65 mm from each axis
SPINDLE_END = FRONT - SPINDLE_LEN / 2  # |x| of the spindles' inboard ends (26.9)
SPINDLE_R = 4.0                        # (carburettors.py throttle_spindle)
LEVER_DX = 47.0                        # throttle lever mid-plane, inboard of each instrument's axis
LEVER_T = 3.0
LEVER_ARM = (242.0, 44.0)              # (y, z) spring hole at the outer end of the throttle lever arm
STOP_SCREW_Y = 230.0                   # throttle adjusting screw on the arm, tip down on the body's stop lug
STOP_LUG = ((-52.0, -36.0), (196.0, 234.0), (26.0, 32.0))   # body stop lug: (dx from axis, signed inboard), y, z
STOP_LUG_TOP = STOP_LUG[2][1]
SHAFT_R = 3.0 / 16.0 * IN              # interconnecting shaft, 3/8 in
SHAFT_HALF = 24.0                      # shaft from x -24 to +24, its ends in the folded clamps
CLAMP_X = (17.0, 36.0)                 # |x| of each folded clamp (spindle end 26.9 inside it)
NUT_X = (37.6, 41.6)                   # |x| of the spindle nut, tab washer to the lever's hub
PINCH_Z = 11.0                         # pinch bolts of the clamps and the shaft lever, above the shaft axis
ACCEL_LEVER_X = 0.0                    # throttle shaft lever (12H715) on the shaft between the instruments
ACCEL_PIN = (232.0, 44.0)              # (y, z) swivel pin for the cable inner on the lever
SWIVEL_PIN_X = 7.6                     # split pin through the swivel pin behind its washers
SWIVEL_DX = 8.0                        # the inner passes the swivel pin's cross hole this far to the front of the lever
ACCEL_SPRING = (242.0, 44.0)           # (y, z) hole for the centre return spring
LIP_Z = K.AXIS_Z - 92.0 + 1.6          # top of the heat shield's turned-out lip (carburettors.py heat_shield)
LIP_T = 1.6
SPRING_LIP_Y = 236.0                   # the three spring holes in the lip (photo 17.1(b))
SPRING_X = [FRONT - LEVER_DX, ACCEL_LEVER_X, REAR + LEVER_DX]

# jet (choke) linkage: one lever and link per instrument on a pivot bolt into a boss on the body, the levers joined
# by the choke interconnecting rod through lever-and-pin clamps; lifting the rod rocks the levers and the links push
# the jets down.
JET_LEVER_DX = 22.5                    # lever plate mid-plane, inboard of each instrument's axis
JET_LEVER_T = 3.0
JET_LINK_DX = 19.6                     # link plate mid-plane (its foot screwed to the jet head's lug end, Fig 3.10 51)
JET_LINK_T = 2.0
JET_LUG_END_DX = 18.0                  # the jet head's lug ends this far inboard of the axis (carburettors.py)
JET_PIVOT = (248.0, 20.0)              # (y, z) pivot bolt axis (along x) on the body boss
JET_BOSS_DX = (21.0, 7.0)              # body pivot boss from the lever's outer face to near the jet housing
JET_LINK_TOP = (234.0, 20.0)           # (y, z) pin joining lever and link
JET_LUG = (K.PISTON_Y, K.AXIS_Z - 88.0)   # (y, z) the jet head's lug (carburettors.py jet_assembly)
JET_PIN = (266.0, 20.0)                # (y, z) lever's outer hole, taking the clamp's pin
ROD = (266.0, 32.0)                    # (y, z) choke interconnecting rod axis (along x)
ROD_R = 0.125 * IN                     # 1/4 in rod
ROD_HALF = 64.0                        # rod from x -64 to +64
ROD_CLAMP_W = 8.0                      # lever-and-pin clamps (Fig 3.10 64/65) inboard of each lever plate
CHOKE_LEVER_X = 20.0                   # choke cable trunnion lever (Fig 3.10 69) on the rod
CHOKE_TRUNNION_Z = 48.0                # trunnion in the lever's upper end
TRUNNION_DX = 3.0                      # the inner passes the trunnion's cross hole this far to the front of the lever
FAST_IDLE_GAP = 0.012 * IN             # Haynes Sec 21 para 11: shaft lever stop to choke spindle (manual)

# abutment bracket on the heat shield (choke control bracket AHH6731 with the abutment AHH6734; the throttle outer
# shares it): a vertical plate screwed to the shield's outboard face, turned out over the linkage.
SHIELD_FACE_Y = K.MANIFOLD_FACE_Y + K.GASKET + K.SHIELD_T   # outboard face of the heat shield (178.4)
BRACKET_X = (-16.0, 36.0)
BRACKET_Z = (74.0, 104.0)              # vertical plate; the top flange at z 104 runs outboard
BRACKET_T = 1.6
BRACKET_FLANGE_Y = 280.0               # outer edge of the top flange (clear of the air cleaner cases at y 283.5)
BRACKET_SCREW_XZ = [(-6.0, 87.0), (26.0, 87.0)]    # two 1/4 UNF screws through the shield, above the manifold
FLANGE_TOP = BRACKET_Z[1] + BRACKET_T
THROTTLE_FERRULE = (ACCEL_LEVER_X + SWIVEL_DX, ACCEL_PIN[0], FLANGE_TOP)
CHOKE_FERRULE = (CHOKE_LEVER_X + TRUNNION_DX, ROD[0], FLANGE_TOP)

# ---- cable runs (car frame) -------------------------------------------------------------------------------------
# pedal box cover P-clip (Rimmer: PCR307 "cable to pedal box cover", single-line cars) on a No 10 screw near its
# outboard rear corner
COVER_CLIP = (-300.0, -342.0)          # (x, y) on the cover top (moved out with the box, QA fix round 1, cockpit)
COVER_CLIP_SCREW_DX = 10.5             # the clip's screw, forward of the band
COVER_CLIP_Z = 58.6 + PEDAL_BOX_RAISE   # the cover's top face there (probed on parts/brakes/master.py cover; the box
                                       # raised in QA fix round 1, steering: clutch_layout PEDAL_BOX_RAISE)
FERRULE_L = 14.0                       # crimped ferrules on the outers
THROTTLE_OUTER = [
    (THROTTLE_FERRULE[0], THROTTLE_FERRULE[1], FLANGE_TOP + FERRULE_L), (THROTTLE_FERRULE[0], ACCEL_PIN[0], 132.0),
    (-30.0, 182.0, 160.0), (-150.0, 160.0, 160.0),
    (-246.0, 150.0, 158.0), (-270.0, 100.0, 162.0), (-280.0, -110.0, 172.0), (-292.0, -230.0, 186.0),
    (COVER_CLIP[0], COVER_CLIP[1], COVER_CLIP_Z + 7.4), (-306.0, -384.0, 176.0), (-316.0, -388.0, 160.0), (-325.0, -391.0, -56.0), (-352.0, -404.0, -112.0),
    (-362.0, PEDAL_Y, GUIDE[2]), (BH + 1.0 + GUIDE_NOSE - 8.0 + FERRULE_L, PEDAL_Y, GUIDE[2]),
]
CHOKE_GROMMET = (BH, 140.0, 132.0)     # choke cable through the bulkhead (grommet 14A7033), left of the heater opening
CHOKE_KNOB = (BL.FACIA_X, -36.0, BL.IP_Z - 50.0)   # Oliver's photo 16: the "C" knob right of the ignition
CHOKE_BUSH_L = 26.0                    # threaded bush of the control forward of the facia's rear face
CHOKE_HOLE_R = 6.6                     # its hole in the facia (7/16 in bush)
CHOKE_OUTER = [
    (CHOKE_FERRULE[0], CHOKE_FERRULE[1], FLANGE_TOP + 2.0 + FERRULE_L), (CHOKE_FERRULE[0], ROD[0], 128.0),
    (-2.0, 196.0, 172.0), (-150.0, 172.0, 172.0),
    (-250.0, 166.0, 168.0), (-330.0, 150.0, 140.0), (BH + 30.0, CHOKE_GROMMET[1], CHOKE_GROMMET[2]),
    (CAB - 40.0, CHOKE_GROMMET[1], CHOKE_GROMMET[2]), (-560.0, 80.0, 170.0), (-690.0, CHOKE_KNOB[1], CHOKE_KNOB[2] - 6.0),
    (BL.FACIA_X + CHOKE_BUSH_L + 30.0, CHOKE_KNOB[1], CHOKE_KNOB[2]), (BL.FACIA_X + CHOKE_BUSH_L, CHOKE_KNOB[1], CHOKE_KNOB[2]),
]
CHOKE_KNOB_OUT = 3.0                   # knob this far off its stop (pushed home, the free movement of Sec 21)
