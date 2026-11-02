"""Laycock de Normanville type D overdrive (1963 MGB, three-synchro gearbox): the datums every
overdrive part and the rear mounting are built and placed from.

Frame: the gearbox frame of mgb.gearbox_layout (GF): local z (d) rearward along the mainshaft from
the gearbox casing front face, local x up, local y the car's left. Overdrive stations are given as
e, millimetres rearward of the overdrive main casing's front face; d = Z0 + e.

What is fixed elsewhere (P5a, mgb/gearbox_layout.py): the adaptor's rear face OD_FACE_X with the
0.8 mm gasket 37H1901 on it, the eight 1/4 in UNF studs on OD_STUD_R, the register OD_SPIGOT_R, the
oil way OD_OIL_PORT, the mainshaft tail (cam seat MS_CAM_D, splines MS_SPLINE_D, pilot MS_PILOT_D,
end MS_END_X), the remote housing underside REMOTE_BOTTOM_UP and the support bracket screw bosses
at REMOTE_BRACKET_*.

What Haynes fixes (Ch 6, printed p111 and p126-131): ratio 0.802; the parts and their order
(Fig 6.13); the sectional view (Fig 6.12, p127) - main casing, brake ring and rear casing in
line, the operating cylinders and bridge pieces in front, the clutch springs on four bolts, the
thrust bearing housing, the cone clutch between the brake ring and the annulus, planets, the
uni-directional roller clutch, the annulus and output shaft on two bearings with the speedometer
drive gear and spacer between, the oil seal and the coupling flange; the pump plunger under the
cam with the non-return valve below it; the operating valve under a plug reached from inside
the car (Sec 14 para 5); solenoid and operating lever under a cover with three bolts (Sec 13,
Fig 6.17); drain, non-return valve and relief valve plugs on the underside (Fig 6.18); the
filter behind a cover plate on the left-hand side (Sec 2 para 5); pump spring free length
2.00 in, clutch spring free length 1.51 in (p111); output shaft endfloat and shims (Sec 12).

Derived (D): every size below. Proportions are scaled from Fig 6.12 (4.36 px/mm on the 220 dpi
render, set by the mainshaft from the overdrive face to its pilot end, 182 mm in P5a): main
casing about 80 mm long, brake ring about 200 mm across, front face to flange face about 300 mm,
flange about 96 mm across. Tooth counts: 0.802 = Za / (Za + Zs) with Zs 25, Zp 38, Za 101 (101/126
= 0.8016, 0.802 to three places), module 1.25: the sun keeps a wall over the 7/8 in mainshaft,
(Zs + Za) / 3 is whole so the three planets are equally spaced, and they are timed to the sun
as Fig 6.16's etched marks do. Which side things are on: Fig 6.18 (underside) and Fig 6.17 put the solenoid on the
right with the speedometer drive boss on the same side; Sec 2 para 5 puts the filter cover on
the left.
"""
from __future__ import annotations

import math

from mgb import gearbox_layout as G

IN = 25.4
OD_JOINT_T = 0.8                                  # gasket 37H1901 (P5a gearbox.casing.od-gasket)
Z0 = G.AD_END + OD_JOINT_T                         # d of the main casing front face


def d(e):
    """Gearbox-frame d of an overdrive station e."""
    return Z0 + e


def e_of(dd):
    return dd - Z0


def x_of(e):
    """Car x of an overdrive station."""
    return G.gx(d(e))


# ---- mainshaft datums in e (P5a) -----------------------------------------------------------------
CAM_E = (e_of(G.MS_CAM_D[0]), e_of(G.MS_CAM_D[1]))          # 21.2 .. 43.2
CAM_MID = sum(CAM_E) / 2
SPLINE_E = (e_of(G.MS_SPLINE_D[0]), e_of(G.MS_SPLINE_D[1]))  # 69.2 .. 149.2
PILOT_E = (e_of(G.MS_PILOT_D[0]), e_of(G.MS_PILOT_D[1]))     # 149.2 .. 181.2
SHAFT_R = G.MS_TAIL_R                                        # 11.11, plain tail and spline major
SPLINE_MINOR_R = G.MS_SPLINE[2] / 2

# ---- casings ---------------------------------------------------------------------------------------
SPIGOT = (-8.0, 0.0)                     # spigot entering the adaptor register (R 56)
SPIGOT_R = (G.OD_SPIGOT_R - 0.5, 50.0)   # outer, inner
MC_FLANGE = (0.0, 11.0)                  # main casing front flange
MC_FLANGE_R = 94.0                       # top kept under the remote housing (REMOTE_BOTTOM_UP 96)
MC_BODY_R = 80.0
MC_LEN = 80.0                            # main casing front face to the brake ring joint
MC_REAR_FL = (70.0, MC_LEN)              # rear flange the brake ring clamps to
CASE_R = 94.0                            # rear flange, brake ring and rear casing flange outside radius
CASE_STUD_R = 86.0                       # eight studs main casing -> brake ring -> rear casing
CASE_STUD_ANGLES = [22.5 + 45.0 * k for k in range(8)]
BR = (MC_LEN, 96.0)                      # brake ring
RC_FLANGE = (96.0, 106.0)                # rear casing front flange
RC_BODY_R = 81.0                         # just behind the flange: clear of the remote bracket legs
RC_END = 266.0                           # rear casing rear face (oil seal housing)
SUMP_BOTTOM = -118.0                     # up, underside of the main casing sump
SUMP_LEFT = (-50.0, 60.0)                # sump sides (left)
SUMP_E = (6.0, 74.0)


def stud_xy(r, a):
    """(up, left) of a point on a circle of radius r at angle a (deg) from up toward the left."""
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))


OD_STUDS = [stud_xy(G.OD_STUD_R, a) for a in G.OD_STUD_ANGLES]
CASE_STUDS = [stud_xy(CASE_STUD_R, a) for a in CASE_STUD_ANGLES]

# ---- operating cylinders, bridge pieces, clutch bolts and springs ------------------------------------
CYL_LEFT = 36.0                          # two cylinders, left and right of the mainshaft, at its height
PISTON_D = 0.875 * IN
CYL_E = (0.0, 24.0)                      # bore depth from the front face
BOLT_UP = 18.0                           # four bolts in pairs above and below each cylinder
BOLTS = [(s * BOLT_UP, side * CYL_LEFT) for side in (1, -1) for s in (1, -1)]
BOLT_SIZE = "5/16"
BRIDGE_E = (-10.0, -4.0)                 # bridge pieces in front of the face, inside the spigot
PISTON_E = (-4.0, 16.0)                  # piston, its spigoted end on the bridge piece
SPRING_E = (28.0, 60.0)                  # clutch springs on the bolts: seat on the cylinder pads -> retainer plate
SPRING_FREE = 1.51 * IN
PLATE_E = (60.0, 62.0)                   # retainer plate
HOUSING_E = (62.0, 76.0)                 # thrust bearing housing (lugs 62-70, bolt heads behind)
TB = (45.0, 68.0, 12.0)                  # thrust bearing bore, outside diameter, width
TB_E = (63.6, 75.6)

# ---- cone clutch (sliding member), brake ring cone, annulus cone (direct drive position) -------------
CLUTCH_HUB_E = (54.0, 82.0)
CLUTCH_HUB_R = (17.6, 22.5)              # splined bore on the sun wheel, bearing seat
CLUTCH_DISC_E = (77.0, 82.0)
CONE_E = (82.0, 96.0)                    # lined cone ring
BR_CONE_R = (75.0, 79.0)                 # brake ring inner cone radius at CONE_E[0] and [1] (small end forward)
LINING_T = 2.0
GAP = 0.6                                # running clearance to the brake ring in direct drive
ANN_CONE_R = (63.0, 67.0)                # annulus outer cone at CONE_E (inner lining seated on it)

# ---- sun wheel, planets, carrier, annulus ------------------------------------------------------------
MOD = 1.25
ZS, ZP, ZA = 25, 38, 101
RATIO = ZA / (ZA + ZS)
SUN_R = ZS * MOD / 2
PLANET_R = ZP * MOD / 2
ANN_R = ZA * MOD / 2
PLANET_CIRCLE = SUN_R + PLANET_R
GEAR_E = (104.0, 122.0)                  # gear face (sun, planets, annulus teeth)
SUN_E = (46.0, 122.0)                    # sun wheel: steady bush in its front bore, splines, sleeve, gear
SUN_SPLINE_E = (48.0, 82.0)
SUN_SPLINE = (18, 35.0, 31.0)            # count, major, minor diameter (clutch hub)
BUSH_E = (46.0, 60.0)                    # steady bush (Fig 6.13 item 83) in the sun wheel's front bore
BUSH_OD = 26.4
CARRIER_E = (98.0, 134.0)                # front plate 98-104, planets, rear plate 122-128, hub to 134
ANN_E = (84.0, 168.0)                    # cone lip, shell, teeth, back wall, neck to the shaft
ANN_SHELL_R = 72.0
ANN_TEETH_E = (100.0, 126.0)
ANN_WALL_E = (128.6, 150.0)
UD_E = (134.6, 146.6)                    # uni-directional clutch
UD_R = (25.0, 32.0)                      # inner member ramp radius, outer race bore
UD_ROLLER = (7.0, 12.0)                  # diameter, length
UD_N = 12
UD_CLIP_E = 129.6                        # circlip 72 in the annulus bore in front of the clutch, oil thrower behind it
NEEDLE_E = (151.0, 181.0)                # needle bearing for the pilot in the output shaft
PILOT_NEEDLE_R = (G.MS_PILOT_R, G.MS_PILOT_R + 3.0)   # needle bearing bore and outside radius
NEEDLE_R_OUT = PILOT_NEEDLE_R[1]
OUT_BRG_FRONT = (35.0, 72.0, 17.0)       # 77: bore, OD, width
OUT_BRG_REAR = (30.0, 62.0, 16.0)        # 81
FRONT_BRG_E = (168.0, 185.0)
SPEEDO_E = (192.0, 208.0)                # speedometer driving gear (worm) 78
SPACER_E = (208.0, 232.0)                # bush 79
SHIM_T = 0.095 * IN                      # thrust washer / shim 80 (0.090-0.105 in)
SHIM_E = (232.0, 232.0 + SHIM_T)
REAR_BRG_E = (SHIM_E[1], SHIM_E[1] + OUT_BRG_REAR[2])
SEAL_E = (254.0, 264.0)
SEAL_RUN_R = 22.0                        # flange hub the rear oil seal runs on
FLANGE_E = (254.0, 300.0)                # hub in the seal, disc 292-300
FLANGE_DISC_E = (292.0, 300.0)
FLANGE_FACE_E = FLANGE_DISC_E[1]         # propeller shaft joint face (P6)
FLANGE_R = 48.0
FLANGE_PCD = 3.125 * IN
FLANGE_BOLTS = 4
FLANGE_BOLT = "5/16"
SHAFT_SPLINE_E = (251.0, 288.0)
SHAFT_THREAD_E = (288.0, 306.5)
OUT_SPLINE = (20, 26.0, 23.0)            # count, major, minor diameter
WASHER_E = (288.6, 291.1)                # in the recess in the flange's rear face
NUT_E = (291.2, 306.2)
FLANGE_RECESS = (20.0, 288.0)            # radius, e of its floor

# ---- speedometer drive (right-hand side, below the output shaft) -------------------------------------
SPEEDO_WORM_R = 19.8                     # tip radius of the driving gear
SPEEDO_PINION_R = 7.5
SPEEDO_UP = -(SPEEDO_WORM_R - 1.5 + SPEEDO_PINION_R)       # driven gear axis height
SPEEDO_AXIS_E = sum(SPEEDO_E) / 2
SPEEDO_BOSS_LEFT = -64.0                 # outer face of the boss (the housing flange seats on it)
SPEEDO_HOUSING_D = 22.0

# ---- hydraulics -------------------------------------------------------------------------------------
CAM_THROW = 2.5                          # eccentricity (D)
CAM_R = 18.0
PUMP_E = CAM_MID
PUMP_TOP = -(CAM_R - CAM_THROW)          # plunger pin on the cam's low point (Sec 11 para 5)
PIN_D = 6.0                              # pump plunger pin (42), along the car under the cam
PUMP_HEAD = (PUMP_TOP - PIN_D, PUMP_TOP - 16.0)     # fork head of the plunger (up)
PUMP_BODY = (-106.0, -64.0)              # pump body (43): bottom, top of its small end
PUMP_BODY_STEP = -80.0                   # small end above this, full diameter below
GRUB_UP = -94.0                          # grub screw (47) from the front face into the body groove
NRV = (-114.0, -106.0)                   # non-return valve body (45) below the pump body
RELIEF_BODY = (-104.0, -72.0)            # relief valve body (99) in its bore
RELIEF_LEFT = -28.0                      # relief valve bore beside the pump (Fig 6.18 plugs 2, 3)
PLUG_FACE = SUMP_BOTTOM - 4.0            # bosses on the underside the three plugs seat on
DRAIN = (64.0, 24.0)                     # (e, left) of the drain plug on the underside
FILTER = (36.0, -101.5)                   # (e, up) of the filter axis, along y from the left face
FILTER_FACE = SUMP_LEFT[1]               # left face the cover plate seats on
FILTER_R = 12.0
COVER = (4.0, 68.0, -126.0, -82.0)       # filter cover plate: e0, e1, up0, up1
OPVALVE = (56.0, -55.0)                  # (e, left) of the operating valve bore (vertical)
OPVALVE_TOP = 72.0                       # boss top face (plug 20 seats here), under REMOTE_BOTTOM_UP
CROSS_SHAFT = (56.0, 10.0)               # (e, up) of the operating lever cross-shaft (along y)
CHAMBER = (42.0, 80.0, -48.0, 26.0)      # lever chamber on the right: e0, e1, up0, up1
CHAMBER_FACE = -134.0                    # cover face (left)
LEVER_LEFT = -119.0                      # plane of the operating lever
SOL_AXIS = (-16.0, -119.0)               # (up, left) of the solenoid axis, along the car
SOL_E = (CHAMBER[1], CHAMBER[1] + 92.0)
SOL_R = 22.0
PLUG39 = (32.0, -80.0)                   # (e, up) of plug 39 on the right of the sump, horizontal

# ---- rear mountings on the main casing sides --------------------------------------------------------
MOUNT_E = (48.0, 80.0)
MOUNT_UP = (-80.0, -54.0)
MOUNT_FACE = 86.0                        # |left| of the pad faces
MOUNT_SCREWS = [(56.0, -67.0), (72.0, -67.0)]      # (e, up) of the two 5/16 UNF screws per pad

# ---- P6 (propeller shaft) datums, car frame -----------------------------------------------------
FLANGE_FACE_X = x_of(FLANGE_FACE_E)      # rear face of the coupling flange: the propeller shaft flange seats here
FLANGE_AXIS = (G.AXIS_Y, G.AXIS_Z)       # (y, z) of the output shaft axis
FLANGE_HOLE_ANGLES = [45.0 + 90.0 * k for k in range(FLANGE_BOLTS)]   # from up toward the left
NUT_PROTRUSION = NUT_E[1] - FLANGE_FACE_E                            # the nut stands this far proud of the face
