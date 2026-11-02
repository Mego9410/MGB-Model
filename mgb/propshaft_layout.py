"""Propeller shaft (P6): Hardy Spicer tubular shaft, overdrive length, between the overdrive coupling
flange (mgb.overdrive_layout FLANGE_*) and the rear axle pinion flange (mgb.rear_axle_layout).

Shaft frame: each part is drawn along its own local z. Flange yokes: z = 0 on the flange's joint
face, +z toward the joint, local x along the yoke's journal (the flange yokes' journals are vertical).
Sleeve yoke and shaft assembly: z along the shaft from the front joint centre rearward, local y
along their journals (the car's y: the yokes on the shaft lie in line, Haynes Fig 7.4).

What Haynes fixes (Ch 7, printed p138-141): tubular, telescopic, needle roller universal joints, a
sliding spline at the front (Sec 1); overdrive shaft overall length fully extended 31 7/8 in,
fully compressed 30 3/16 in, length of shaft assembly 26 15/32 in (specifications; the printed
cm figures 76.5 and 67.0 disagree with the inch figures by about 2 mm, the inch figures govern);
flange nuts 30 to 35 lbf ft; non-sealed joints with a grease nipple on each spider facing the
shaft and a third on the sleeve, gaskets and gasket retainers on the journals, circlips (Sec 2,
Sec 4, Fig 7.1); the dust cap, steel washer and cork washer on the sleeve, arrows on the sleeve
and shaft lined up (Sec 4 paras 3, 10-11); self-locking nuts, bolts and washers at the flanges
(Sec 3).

Supplier data (S): the 1962-67 banjo axle overdrive shaft is 31 1/8 in (MGOC AHH7487; Brit Parts NW
AHH7487EOD "MGB 63 to 67 overdrive banjo axle"); joint GUJ115, greasable for early cars (MGOC
propshaft page; Rimmer Bros); flange bolts AAA4039 with GHF332 spring washers and GHF222 5/16 UNF
nyloc nuts, eight per car on three-synchro cars (MGOC propshaft page).

Derived (D): the joint (cups 27 mm, 74.6 mm across the cups, the size of the URO URGUJ115 joint
listed for the MGB, GMB 2151100); everything else is scaled from Fig 7.4 at 0.282 mm/px of the
300 dpi render, set by the 96 mm flange (the overdrive flange it mates): flange face to joint
centre 34 mm, sleeve 38 mm across, splined stub 30 mm, tube 2 1/4 in. The installed length is the
supplier length, which puts the stub 46 mm into the sleeve, near the middle of the Haynes travel
(fully extended: 27 mm engaged; fully compressed: 70 mm).
"""
from __future__ import annotations

import math

from build123d import Location, Rot

from mgb import overdrive_layout as O, rear_axle_layout as RA

IN = 25.4

# ---- published lengths ------------------------------------------------------------------------------
LEN_EXTENDED = (31.0 + 7.0 / 8.0) * IN
LEN_COMPRESSED = (30.0 + 3.0 / 16.0) * IN
LEN_SHAFT_ASSY = (26.0 + 15.0 / 32.0) * IN
LEN_NOMINAL = (31.0 + 1.0 / 8.0) * IN        # supplier, installed (S)

# ---- universal joint (D) ------------------------------------------------------------------------------
CUP_D = 27.0
CUP_SPAN = 74.6                              # outside of one cup to the outside of the opposite cup
CUP_LEN = 16.5
CUP_BASE = 2.4
JOURNAL_D = 15.0
ROLLER_D = (CUP_D - 2 * 2.6 - JOURNAL_D) / 2           # needle diameter: cup wall 2.6 mm
SHOULDER_R = CUP_SPAN / 2 - CUP_LEN - 4.3    # journal shoulder (gasket seat), radius from the centre
EYE_R = 18.0                                 # yoke eye boss radius
EAR_OUT = CUP_SPAN / 2 + 1.8                 # outer face of each yoke ear (circlip outboard of the cup)
EAR_IN = CUP_SPAN / 2 - CUP_LEN - 0.4        # inner face
EAR_HALF_W = 17.0                            # half width of an ear across its journal axis

# ---- flange yoke -------------------------------------------------------------------------------------
FLANGE_R = 48.0
FLANGE_T = 6.5
FACE_TO_JOINT = 34.0
RECESS = (22.0, 7.5)                         # clearance for the overdrive / pinion nut: radius, depth
PCD = O.FLANGE_PCD
HOLE_D = 8.3

# ---- sleeve yoke, dust cap, shaft (stations from the front joint centre) ----------------------------------
SLEEVE_R = 19.0
SLEEVE_TUBE_Z = (28.0, 130.0)
SLEEVE_BORE_Z = (45.0, 130.0)
SLEEVE_THREAD_Z = (116.0, 130.0)
NIPPLE_Z = 37.0
CAP_Z = (114.0, 136.0)
STEEL_WASHER_Z = (130.0, 130.8)
CORK_WASHER_Z = (130.8, 132.4)
SPLINE = (18, 30.0, 26.0)                    # count, major, minor
STUB_LEN = 78.0                              # splines 66, plain neck 12
STUB_SPLINE_LEN = 66.0
CONE_LEN = 20.0
TUBE_D = 2.25 * IN
TUBE_WALL = 1.63                             # 16 swg
REAR_YOKE_NECK = 42.0                        # tube end to the rear joint centre
JOINT_TO_REAR_FACE = FACE_TO_JOINT
STUB_FRONT_TO_JOINT = LEN_SHAFT_ASSY - JOINT_TO_REAR_FACE        # stub front end to the rear joint centre
TUBE_LEN = STUB_FRONT_TO_JOINT - STUB_LEN - CONE_LEN - REAR_YOKE_NECK

# ---- placement in the car ------------------------------------------------------------------------------
FRONT_FACE = (O.FLANGE_FACE_X, O.FLANGE_AXIS[0], O.FLANGE_AXIS[1])
REAR_FACE = (RA.PINION_FLANGE_FACE_CAR_X, RA.PINION_AXIS[0], RA.PINION_AXIS[1])
FRONT_JOINT = (FRONT_FACE[0] - FACE_TO_JOINT, FRONT_FACE[1], FRONT_FACE[2])
REAR_JOINT = (REAR_FACE[0] + FACE_TO_JOINT, REAR_FACE[1], REAR_FACE[2])
_dx, _dz = FRONT_JOINT[0] - REAR_JOINT[0], FRONT_JOINT[2] - REAR_JOINT[2]
JOINT_DIST = math.hypot(_dx, _dz)
ANGLE = math.degrees(math.atan2(_dz, _dx))   # shaft slope, down toward the rear (deg)
INSTALLED_LEN = JOINT_DIST + 2 * FACE_TO_JOINT
STUB_FRONT_Z = JOINT_DIST - STUB_FRONT_TO_JOINT       # stub front end, from the front joint centre
ENGAGED = SLEEVE_TUBE_Z[1] - STUB_FRONT_Z
ENGAGED_EXTENDED = ENGAGED - (LEN_EXTENDED - INSTALLED_LEN)
ENGAGED_COMPRESSED = ENGAGED + (INSTALLED_LEN - LEN_COMPRESSED)
assert abs(INSTALLED_LEN - LEN_NOMINAL) < 1.0, INSTALLED_LEN         # the axle datum must agree
assert LEN_COMPRESSED < INSTALLED_LEN < LEN_EXTENDED
assert ENGAGED_EXTENDED > 25.0 and STUB_FRONT_Z - ENGAGED_COMPRESSED + ENGAGED > SLEEVE_BORE_Z[0]

# frames (car): flange yokes, local z toward their joint; shaft parts, local z rearward along the shaft
FRONT_YOKE = Location(FRONT_FACE) * Rot(0, -90, 0)                  # local z -> car -x, local x -> car +z
REAR_YOKE = Location(REAR_FACE) * Rot(0, 90, 0) * Rot(0, 0, 180)    # local z -> car +x, local x -> car +z
SHAFT = Location(FRONT_JOINT) * Rot(0, -90 - ANGLE, 0)              # local z along the shaft, local y = car y
SHAFT_AT_STUB = SHAFT * Location((0, 0, STUB_FRONT_Z))
FLANGE_HOLE_ANGLES = O.FLANGE_HOLE_ANGLES                            # from up toward the left


def front_hole(a):
    """Car point of a front flange bolt hole on the joint face, at angle a from up toward the left."""
    r = PCD / 2
    return (FRONT_FACE[0], FRONT_FACE[1] + r * math.sin(math.radians(a)), FRONT_FACE[2] + r * math.cos(math.radians(a)))


def rear_hole(a):
    r = PCD / 2
    return (REAR_FACE[0], REAR_FACE[1] + r * math.sin(math.radians(a)), REAR_FACE[2] + r * math.cos(math.radians(a)))
