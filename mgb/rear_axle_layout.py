"""Rear axle (P7), early three-quarter floating banjo axle (18G, 1962-67), wire wheels: the datums
every axle part is built and placed from, and the datums P6 (propeller shaft), P8 (brakes) and P9
(rear springs, dampers, rebound straps, wheels) attach to.

Axle frame (AF): origin on the axle centre (car_layout REAR_AXLE_X, y 0, WHEEL_Z), axes as the car
frame (x forward, y to the car's left, z up). Parts are drawn in the axle frame; the assemblies
place them with AF. Distances along the axle are |y| outward from the centre; the right-hand
(off-side) hub is the left-hand one mirrored, with its threads handed by the side tables below.

What Haynes fixes (Ch 8, printed p142-143): three-quarter floating axle on early (18G, 18GA)
cars; ratio 3.909:1 (43/11); the parts and their order (Fig 8.1): the banjo case with its gear
carrier studs, breather, filler and drain plugs, the differential carrier on a gasket held by
nuts and spring washers, the cage on two bearings with packing washers in the carrier's saddles
under two caps, the crown wheel bolted to the cage with lockwashers, two side gears and two
pinions on a pinion shaft held by a peg, each with its thrust washer, the pinion with its
thrust washer (0.112-0.126 in), rear bearing, spacer, front bearing and shims (0.004-0.030 in),
the oil seal, dust cover, flange, spring washer and nut (135-140 lbf ft); for wire wheels the
hub on its bearing on the case, its oil seal, the bearing nut (RH thread one side, LH the
other) and its locking washer, the hub extension (RH and LH) bolted with the brake drum to the
hub's studs and held by a screw, its Welch plug, the axleshaft splined into it and the O-ring
seal (Sec 4 paras 5-6, Sec 5). The bearing's outer face stands 0.001-0.004 in proud of the hub
so the driving flange clamps it (Sec 5 para 4d). Filler/level plug on the rear face, breather on
top (Sec 2). Rebound straps on the axle's spindles (Fig 8.1 item 5; Ch 8 Sec 3 para 4: check
straps on the anchor pins), U-bolts, pedestals, pads and the damper bracket clamp the axle to
the springs (Ch 11 Fig 11.4, printed p207).

Supplier data (S): hub bearing 40 x 80 x 23 mm double row, BMC 2K7477 (mgaguru.com RA-112); hub
oil seal 1 15/16 x 2 3/4 x 5/16 in (mgaguru.com RA-112A); hub nut 1 61/64 in across the flats
of its eight-sided spanner (MGOC 18G152B box spanner; mgaguru.com hub_06; magnette.org: the nut
is octagonal); right-hand thread on the right-hand hub, left-hand thread on the left (mgaguru.com
hub_06; BritishCarForum "left rear hub nut"); 42 mm series Rudge-Whitworth splined hub extensions
with 12 tpi spinner threads to chassis GHN3-30850 (MGOC "wheel spinners"; S C Parts 6954/6955;
mgaguru.com WL-113); left-hand spinner threads on the car's right-hand side (MGOC); Welch plug
1 5/16 in (MGOC 2K8160); shaft-to-hub screw 1/4 UNF x 3/4 countersunk (MGOC SF604061); pinion nut
3/4 UNF thin locknut and 3/4 spring washer (MGOC FNZ612, WL600121); carrier nuts 5/16 UNF with
spring washers (MGOC GHF201, GHF332); cap nuts 3/8 UNF, large plain washer (GHF202, PWZ206).

Derived (D), not published: every size and station below. Track from car_layout (wheel centre
planes); the drum face sits inside the inner half of the 4 1/2J rim, the hub extension's inner
cone under the wheel centre plane; crown wheel 190 mm pitch diameter (module 4.42), hypoid
offset 1 in below the axle centre; Fig 8.1 proportions for the banjo, carrier and nose (the nose
is about as long as the carrier flange is wide). The pinion flange face is placed where the
propeller shaft sits near the middle of its Haynes travel (overall length 31 1/8 in, the MGOC
AHH7487 shaft for banjo axle overdrive cars), with the pinion level, parallel to the overdrive
output shaft, so the two joint angles cancel (Ch 7 Fig 7.4 yokes in line).
"""
from __future__ import annotations

import math

from build123d import Location

from mgb import car_layout as CL

IN = 25.4
AX, AZ = CL.REAR_AXLE_X, CL.WHEEL_Z
AF = Location((AX, 0.0, AZ))                 # axle frame: origin at the axle centre, car axes

# ---- gearing (H p142: 3.909 = 43/11) -----------------------------------------------------------------
Z_CROWN, Z_PINION = 43, 11
RATIO = Z_CROWN / Z_PINION
CROWN_PITCH_R = 95.0                         # heel pitch radius (D)
PITCH_ANGLE_PINION = math.degrees(math.atan(Z_PINION / Z_CROWN))      # 14.35 deg
CONE_DIST = CROWN_PITCH_R / math.sin(math.radians(90.0 - PITCH_ANGLE_PINION))
FACE_W = 28.0
HYPOID_OFFSET = 1.0 * IN                     # pinion axis below the axle centre (D)
PINION_Z = -HYPOID_OFFSET                    # axle frame z of the pinion axis (y 0, level)
CROWN_HEEL_Y = CROWN_PITCH_R * Z_PINION / Z_CROWN    # crown wheel on the left: heel pitch circle plane
CROWN_BACK_Y = 48.0                          # crown wheel back face (mounting face on the cage flange)
CROWN_BOLT_R = 64.0
CROWN_BOLTS = 8

# ---- differential (cage axis = axle axis) -------------------------------------------------------------
Z_SIDE, Z_PLANET = 16, 10
SIDE_PITCH_R = 34.0
PLANET_PITCH_R = SIDE_PITCH_R * Z_PLANET / Z_SIDE
DIFF_BRG = (38.1, 80.0, 21.0)                # bore, OD, width (MGOC CHM163; sizes D)
DIFF_BRG_Y = (68.0, 89.0)                    # |y| of the bearing faces
PACKING_T = 0.006 * IN                       # packing washer, within 0.002-0.010 in (H p143)
SADDLE_Y = (66.0, 92.0)                      # carrier saddles and caps (inside the 102.5 mm opening)
CAP_X = (-52.0, 0.0)                         # caps behind the split line through the bearing axis
CAP_STUD_Z = 50.0                            # two studs per cap, above and below the bearing
CAP_STUD = "3/8"

# ---- pinion stations, x forward of the axle centre along the pinion axis ------------------------------
PINION_HEEL_X = CROWN_PITCH_R + 2.0          # back face of the pinion head
THRUST_T = 0.119 * IN                        # pinion head thrust washer, 0.112-0.126 in (H p143)
RBRG = (35.0, 72.0, 24.0)                    # rear pinion bearing (taper roller): bore, OD, width
RBRG_X = (PINION_HEEL_X + THRUST_T, PINION_HEEL_X + THRUST_T + RBRG[2])
FBRG = (30.0, 62.0, 18.0)                    # front pinion bearing
SHIM_T = 0.010 * IN                          # within 0.004-0.030 in (H p143)
SPACER_X = (RBRG_X[1], 245.0)
FBRG_X = (SPACER_X[1] + SHIM_T, SPACER_X[1] + SHIM_T + FBRG[2])
SEAL = (38.1, 2.385 * IN, 10.0)                    # ID (flange track), OD (2.385 in, mgaguru RA-201), width
SEAL_X = (270.0, 280.0)
NOSE_END_X = 284.0
PINION_SPLINE = (16, 25.4, 22.0)             # count, major, minor
PINION_THREAD = "3/4"

# ---- propeller shaft joint at the pinion flange (P6) -----------------------------------------------------
# P6 places the pinion flange face where the shaft sits at its nominal length; the value is kept here
# as the axle's datum. See mgb.propshaft_layout for the calculation it must agree with.
PINION_FLANGE_FACE_X = 354.1                 # forward of the axle centre
PINION_FLANGE_R = 48.0
PINION_FLANGE_DISC = (PINION_FLANGE_FACE_X - 8.0, PINION_FLANGE_FACE_X)
PINION_FLANGE_PCD = 3.125 * IN               # four 5/16 UNF bolts, as the overdrive flange
PINION_FLANGE_HOLES = [45.0 + 90.0 * k for k in range(4)]   # from up toward the left (seen from in front)
PINION_RECESS = (20.0, PINION_FLANGE_FACE_X - 14.0)        # radius, x of the floor
PINION_NUT_X = (PINION_RECESS[1] + 2.0, PINION_RECESS[1] + 10.0)

# ---- banjo case -----------------------------------------------------------------------------------------
CASE_FACE_X = 78.0                           # front face of the banjo ring (carrier gasket on it)
GASKET_T = 0.4
CARRIER_FLANGE = (CASE_FACE_X + GASKET_T, CASE_FACE_X + GASKET_T + 10.0)
OPENING_R = 102.5
RING_R = 125.0
CASE_STUD_R = 113.0
CASE_STUDS = 10
CASE_STUD_ANGLES = [18.0 + 36.0 * k for k in range(CASE_STUDS)]       # in the y-z plane, from up toward the left
CASE_STUD = "5/16"
SHELL_T = 3.5
BOWL = [(0.0, -121.0), (32.0, -119.5), (58.0, -114.0), (82.0, -105.0), (102.0, -91.0), (117.0, -72.0), (126.0, -50.0),
        (130.5, -24.0), (131.5, 0.0), (130.5, 26.0), (128.0, 50.0), (126.0, 70.0)]
                                             # (r about the x axis, x) outside of the banjo bowl, rear to front
TUBE_R = 38.0                                # tube outside radius
TUBE_Y = (100.0, 540.0)
NECK_Y = (112.0, 215.0)                      # pressed neck from the bowl to the round tube
BACKPLATE_FACE_Y = 562.0                     # outer face of the brake backplate flange (P8)
BACKPLATE_FLANGE_T = 6.0
BACKPLATE_FLANGE_R = 66.0
BACKPLATE_BOLT_PCD = 108.0
BACKPLATE_BOLT_ANGLES = [45.0 + 90.0 * k for k in range(4)]   # in the x-z plane, from up toward the front
BACKPLATE_BOLT = "3/8"
SEAL_TRACK_R = 1.9375 * IN / 2               # hub oil seal runs on the case here
SEAL_TRACK_Y = (BACKPLATE_FACE_Y, 584.0)
JOURNAL_R = 20.0                             # hub bearing seat (40 mm bore)
HUB_BRG = (40.0, 80.0, 23.0)
HUB_BRG_Y = (584.0, 584.0 + HUB_BRG[2])
BRG_PROUD = 0.0025 * IN                      # 0.001-0.004 in proud of the hub face (H p143)
HUB_FACE_Y = HUB_BRG_Y[1] - BRG_PROUD        # outer face of the hub flange
THREAD_D = 1.5 * IN                          # hub nut thread on the case end (D), 16 tpi
THREAD_TPI = 16
CASE_END_Y = 625.0
CASE_BORE_R = 16.0                           # bore through the case end for the axleshaft
LOCKWASHER_T = 1.2
NUT_AF = (1.0 + 61.0 / 64.0) * IN            # 1 61/64 in, eight flats
NUT_T = 14.0
NUT_Y = (HUB_BRG_Y[1] + LOCKWASHER_T, HUB_BRG_Y[1] + LOCKWASHER_T + NUT_T)

# ---- hub and hub extension (wire wheels) ----------------------------------------------------------------
HUB_Y = (574.0, HUB_FACE_Y)
HUB_FLANGE_Y = (HUB_FACE_Y - 8.0, HUB_FACE_Y)
HUB_SEAL_Y = (574.5, 574.5 + 0.3125 * IN)
HUB_FLANGE_R = 72.0
STUD_PCD = 4.5 * IN                          # drum and hub extension studs (D: the MGB 4 x 4 1/2 in pattern)
STUD_ANGLES = [45.0 + 90.0 * k for k in range(4)]      # in the x-z plane from up toward the front
STUD = "1/2"
SCREW_ANGLE = 0.0                            # the countersunk screw (item 46) at the top
EXT_FLANGE_Y = (HUB_BRG_Y[1], HUB_BRG_Y[1] + 8.0)
DRUM_FACE_Y = EXT_FLANGE_Y[1]                # P8: the drum's face seats on the hub extension flange
EXT_COLLAR_Y = (EXT_FLANGE_Y[1], 640.0)      # inner cone the wheel seats on (wheel centre plane over it)
EXT_CONE_R = (33.0, 27.5)
EXT_SPLINE_Y = (640.0, 712.0)
EXT_SPLINE = (36, 42.0, 39.4)                # Rudge-Whitworth 42 mm series: count (D), major, minor
EXT_THREAD_Y = (714.0, 744.0)
EXT_THREAD_D = 39.0
EXT_TPI = 12                                 # to GHN3-30850 (S)
EXT_END_Y = EXT_THREAD_Y[1]
WELCH_D = 1.3125 * IN
SHAFT_SPLINE_OUT = (10, 30.0, 26.0)          # axleshaft outer splines into the hub extension
SHAFT_SPLINE_OUT_Y = (650.0, 700.0)
SHAFT_SPLINE_IN = (10, 30.0, 26.0)           # inner splines into the side gear
SHAFT_IN_Y = (24.0, 58.0)
SHAFT_D = 1.125 * IN

# thread hands by side: +1 = left (near side), -1 = right (off side)
HUB_NUT_HAND = {1: "left", -1: "right"}      # mgaguru.com hub_06, BritishCarForum (forward rotation tightens)
SPINNER_HAND = {1: "right", -1: "left"}      # MGOC: right-hand side of the car uses left-hand threads

# ---- spring seats, U-bolts, rebound strap spindles (P9) ------------------------------------------------
SPRING_Y = 420.0                             # spring centre line (D: under the body side members)
SPRING_W = 1.75 * IN
SEAT_FACE_Z = -TUBE_R - 10.0                 # flat underside of the welded seat (locating plate, pad, spring below)
SEAT_X = (-50.0, 50.0)
UBOLT_X = 45.0                               # U-bolt legs fore and aft of the tube
UBOLT_DY = 30.0                              # two U-bolts per side, either side of the spring
REBOUND_Y = 486.0                            # bracket plate centre
REBOUND_SPINDLE = (-22.0, 500.0, -88.0)      # (x, |y|, z) where the strap's eye sits, spindle along y outward
REBOUND_SPINDLE_END = 522.0

# ---- other fittings ------------------------------------------------------------------------------------
BREATHER = (0.0, -150.0)                     # (x, y) on the top of the right-hand neck
FILLER = (40.0, -25.0)                       # (y, z) on the rear of the bowl
DRAIN = (-40.0, 0.0)                         # (x, y) on the underside
PIPE_BRACKET = (10.0, -190.0)                # (x, y) tab on the top of the right-hand neck for the brake 3-way union (P8:
                                             # Haynes Figs 9.1-9.3 draw the union right of the differential on RHD and LHD cars)
BALANCE_PIVOT = (60.0, -78.0)                # (y, z) pin on the rear of the bowl for the handbrake balance lever (P8)


def side_pt(side, x, ay, z):
    """Axle frame point on one side: |y| = ay; side +1 left, -1 right."""
    return (x, side * ay, z)


def car(p):
    """Axle frame point -> car frame."""
    return (AX + p[0], p[1], AZ + p[2])


# ---- datums for the next phases, car frame ----------------------------------------------------------------
PINION_AXIS = (0.0, AZ + PINION_Z)           # (y, z) of the pinion axis (level)
PINION_FLANGE_FACE_CAR_X = AX + PINION_FLANGE_FACE_X
BACKPLATE_FACE = {s: s * BACKPLATE_FACE_Y for s in (1, -1)}      # P8: car y of the backplate seating faces
DRUM_FACE = {s: s * DRUM_FACE_Y for s in (1, -1)}                # P8: car y of the drum seating faces
SPRING_SEAT = {s: car((0.0, s * SPRING_Y, SEAT_FACE_Z)) for s in (1, -1)}        # P9: seat face centre
UBOLT_LEGS = {s: [car((dx, s * (SPRING_Y + dy), SEAT_FACE_Z)) for dx in (-UBOLT_X, UBOLT_X)
                  for dy in (-UBOLT_DY, UBOLT_DY)] for s in (1, -1)}
PEDESTAL_SEAT = {s: car((0.0, s * SPRING_Y, TUBE_R)) for s in (1, -1)}           # P9: bump rubber pedestal on the tube top
REBOUND_EYE = {s: car((REBOUND_SPINDLE[0], s * REBOUND_SPINDLE[1], REBOUND_SPINDLE[2])) for s in (1, -1)}
WHEEL_INNER_CONE = {s: s * (EXT_COLLAR_Y[0] + EXT_COLLAR_Y[1]) / 2 for s in (1, -1)}   # P9: wire wheel seat
