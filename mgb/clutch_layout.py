"""Clutch layout (engine frame): the stack of parts behind the flywheel, and where the
clutch control gear sits in the car.

The clutch runs on the crank axis. Every station along X below is measured rearward from
the flywheel friction face, which comes from the flywheel assembly: the crankshaft flange
sits 4.5 mm into the flywheel register (assemblies/engine_flywheel.py imports FW_X from
here) and the friction face is one rim thickness (specs/engine/flywheel) behind it.

Stack (D): Haynes Fig 5.2 (sectional view, printed p108) scaled to the published 8 in
driven plate (Ch 5 specs, printed p106). In that drawing the facings span 1235 px across
203.2 mm, so 0.1645 mm/px; the depths below are read off it to the nearest half-millimetre.
"""
from __future__ import annotations

import math
from pathlib import Path

from mgb import car_layout as C, engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parent.parent
_EL = E.layout(head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml")))
_FW = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "flywheel" / "flywheel.yaml")}

CZ = _EL.crank_z                                     # clutch axis height (crank axis)
FLANGE_REAR = _EL.main_x[2] - 16 - 34                # rear face of the crankshaft flange (crank model)
FW_X = FLANGE_REAR + 4.5                             # flywheel front face (register over the flange)
FACE_X = FW_X - _FW["engine.flywheel.flywheel"].nom("rim_thickness")    # flywheel friction face
BOLT_R = _FW["engine.flywheel.flywheel"].nom("clutch_bolt_circle") / 2  # cover bolts, 6 at 60 deg from +Y
BOLT_ANGLES = [60.0 * k for k in range(6)]           # angle from +Y toward +Z, as the flywheel drills them
DOWEL_ANGLES = [30.0 + 120.0 * k for k in range(3)]  # three cover dowels (flywheel model)


def ring_point(r, deg, x):
    """Point at radius r, angle deg (from +Y toward +Z) about the clutch axis, at station x."""
    a = math.radians(deg)
    return (x, r * math.cos(a), CZ + r * math.sin(a))


# ---- stations along X, rearward from the friction face (D, Fig 5.2) ----------------------------
PLATE_T = 8.0                       # driven plate over the facings, clamped
PLATE_MID = FACE_X - PLATE_T / 2
HUB_FRONT = PLATE_MID + 9.0         # short end of the hub toward the flywheel (Sec 4 para 10)
HUB_REAR = PLATE_MID - 24.0
PP_FACE = FACE_X - PLATE_T          # pressure plate friction face
PP_T = 15.5                         # pressure plate ring
PP_RIDGE = 5.5                      # fulcrum ridge on the back of the plate
PP_RIDGE_R = 86.0                   # the diaphragm's outer edge bears here
DIA_T = 2.4                         # diaphragm spring thickness
DIA_OUT_R, DIA_PIVOT_R, DIA_IN_R = 92.0, 63.0, 21.0
DIA_X_OUT = PP_FACE - PP_T - PP_RIDGE - DIA_T / 2    # mid-plane of the diaphragm at its outer edge
DIA_X_PIVOT = DIA_X_OUT - 3.0                        # dished: pivot circle 3 mm further back
DIA_X_TIP = DIA_X_OUT - 8.5                          # finger tips
COVER_T = 2.5                       # pressed steel cover
COVER_DEPTH = 43.5                  # flywheel face to the inside of the cover's back wall
COVER_BACK = FACE_X - COVER_DEPTH   # inside face of the back wall
COVER_HOLE_R = 55.0                 # central opening: the fingers show through it (Fig 5.1)
RP_FRONT = DIA_X_TIP - DIA_T / 2 - 0.3              # release plate on the finger tips
RP_BACK = FACE_X - 47.0                              # release plate face the bearing runs on
BEARING_GAP = 0.5                   # carbon clear of the plate, clutch engaged (D)
BEARING_FACE = RP_BACK - BEARING_GAP
CARBON_PROUD = 5.0                  # carbon ring stands this far out of its cup
CUP_FRONT = BEARING_FACE - CARBON_PROUD
CUP_DEPTH = 22.0
TRUNNION_X = CUP_FRONT - 13.0       # trunnion pins on the cup's lugs, at 12 and 6 o'clock
CUP_R = 46.0                        # outside of the cup
TRUNNION_R = 56.0                   # pins pass through the fork ends here (ends span r 52-60)

# ---- clutch control gear in the car (D) ---------------------------------------------------------
# Early cars (Fig 5.3): the clutch and brake master cylinders bolt side by side to the front of
# the pedal box on the right-hand (driver's) side of the bulkhead, cylinders along the car,
# pushrods back to the pedals, which hang from a common pivot in the box. RHD: the clutch is
# the inboard cylinder and pedal.
PEDAL_BOX_FACE_X = C.BULKHEAD_X + 75.0          # master cylinder flange face (front of the pedal box)
# QA fix round 1, steering: the box (and with it both cylinders, the pivot and the clevises) stands PEDAL_BOX_RAISE
# higher than first drawn, so that the steering column on its straight line from the pinion to the rim in Oliver's
# body scan (steering_layout) passes under the box's floor and through the toe board below it (Haynes Ch 11 Fig 11.6
# items 59/65/69: column bracket at the toe board; Ch 9 Sec 17 para 6: the box is bolted to the toe plate as well as
# the bulkhead; Oliver's kf151: the pedals hang from high up under the facia with the column above them). D: the
# least round-figure raise that clears the column's outer tube by 24 mm under the box floor and 10 mm under the
# spring anchor bar. The pads stay where they were (PEDAL_PAD).
PEDAL_BOX_RAISE = 120.0
# QA fix round 1, cockpit: the box (and with it both cylinders and the pedals' upper arms) moves 42 mm outboard, so the
# clutch arm clears the transmission tunnel (it ran 21 mm into it at y -215: Oliver, "the pedals are clipping into the
# centre column") and the column (8 mm); 42 is as far as the right-hand valance's control box, fuse block and flasher
# (body_layout CONTROL_BOX etc., inboard faces at y -377) let it go. Oliver's photo 13 and his engine-bay scan put the
# cylinders further out still, in the bulkhead's corner beside the heater; that needs the valance fittings moved.
MC_Y, MC_Z = -257.0, -70.0 + PEDAL_BOX_RAISE    # clutch master cylinder axis
# The pads where Oliver's keyframes kf151 and kf152 show them (SfM cameras; the pads' image x solved for y at the
# pads' x and z, the two views within 14 mm; the cameras' horizontal checked on the tachometer and the column to ~5 px,
# their vertical is out by 30-60 px so the pads keep their fore-aft place and height): clutch y -316, brake -418,
# accelerator -490. P8 had -215, -290 and -412. The arms step outboard to them below the column (parts/clutch/pedal.py).
PAD_Y = -316.0
JOG_F = 0.45                                       # the arms' outboard step: this far down their lower length
PEDAL_PIVOT = (C.BULKHEAD_X + 30.0, MC_Y, MC_Z + 45.0)   # pedal pivot in the box, axis along Y
PEDAL_CLEVIS = (C.BULKHEAD_X + 30.0, MC_Y, MC_Z)          # pushrod clevis pin on the pedal
PEDAL_PAD = (C.BULKHEAD_X - 165.0, PAD_Y, -285.0)         # centre of the pad face, in the footwell (unchanged by the raise)
HOSE_BRACKET = (C.bx(-330.0), -268.0, -150.0)   # pipe-to-hose bracket on the right-hand chassis leg (body station)
