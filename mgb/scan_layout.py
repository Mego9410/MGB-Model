"""Registration of Oliver's two photogrammetry scans into the car frame (mgb/car_layout.py: X forward, Y left, Z up, mm,
origin on the engine centreline at the head joint face). Source label D, method "Oliver's scan".

The scans themselves are not in the repo (Oliver's files): Mgb.glb, the whole car with the hood down on concrete
between garages, and "Mgb engine.glb", the engine bay from above with the bonnet open. Both are glTF, y-up, in
arbitrary normalised units. A scan point v (its own units, after the file's node transform) maps to the car frame as

    x_car = SCALE * ROT @ v + TRANS

Body scan (P11b scan QA): the car cropped from the ground and garages by colour and connectivity; the start from the
red paint's principal axes and the ground plane; then (1) the car's own symmetry plane by registering its painted and
bright points against their mirror image (yaw 0.55, roll 0.14 deg corrected), (2) scale, pitch and x/z by trimmed ICP
of the red paint onto our painted panels. The reflective panel faces were not trusted on their own: the symmetry fit
and the four wire wheel rims are the checks. Checks in the result frame: rim circles (flange radius 190-194 mm,
expected about 195) centred at x +163/+166 front and -2156/-2164 rear (wheelbase 2324 against 91 in = 2311.4: the
scale is good to about 0.5 %), rims symmetric about y = 0 within 1 mm (faces at |y| 691-696); median distance of the
trusted red points to our panels 20 mm (the rest is reflection noise and real shape differences). The rear wheels sit
20 mm higher against the body than ours (Oliver's car rides lower at the back: see PLAN.md, Differences seen in
Oliver's scans).

Engine scan: registered on landmarks, the polished rocker cover's four top corners (the same footprint as ours) in the
frame of the inner wing top flanges, which run level across the car and fall 0.165 toward the front as ours do;
landmark residuals 5-6 mm, overall about +/-25 mm (the bay is cluttered and the bonnet is open, so it cannot be
cross-checked against the body scan's closed bonnet). Used for appearance and layout only.
"""
from __future__ import annotations

import numpy as np

BODY_SCALE = 1329.15                        # mm per scan unit
BODY_ROT = np.array([[0.918251, 0.018605, -0.395562],
                     [-0.395814, 0.012555, -0.918245],
                     [-0.012118, 0.999748, 0.018893]])
BODY_TRANS = np.array([-1093.24, -64.49, -698.71])

ENGINE_SCALE = 614.49                       # mm per scan unit
ENGINE_ROT = np.array([[-0.955898, 0.0, 0.293697],
                       [0.293697, 0.0, 0.955898],
                       [0.0, 1.0, 0.0]])
ENGINE_TRANS = np.array([242.0, 14.58, -357.68])

# Checks measured in the body scan, car frame (mm)
RIM_CENTRES = {"FL": (162.9, 696.2, -282.3), "FR": (165.5, -696.3, -277.5),
               "RL": (-2155.9, 691.9, -262.5), "RR": (-2164.2, -693.1, -262.3)}
SCAN_GROUND_Z = {"front": -577.0, "rear": -559.0}       # road under the tyres (ours: GROUND_Z -583.21)


def body_to_car(v):
    """Body scan points (n, 3) in scan units to the car frame (mm)."""
    return BODY_SCALE * (np.asarray(v) @ BODY_ROT.T) + BODY_TRANS


def engine_to_car(v):
    """Engine scan points (n, 3) in scan units to the car frame (mm)."""
    return ENGINE_SCALE * (np.asarray(v) @ ENGINE_ROT.T) + ENGINE_TRANS
