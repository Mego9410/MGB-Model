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

Engine scan: first registered on landmarks (the polished rocker cover's four top corners onto our cover), which put the
bay's body 160 mm too far forward: its headlamps came out at x 780-820 against 622-626 in the body scan, its grille
at 1000 against 774. Re-registered (engine-bay QA, 5 Nov) by a similarity ICP of the engine scan's outer wings, wing
tops and headlamp nacelles (|y| 560-820, body red, the bonnet and bay left out) onto the body scan: scale 0.985,
rotations 1.5 deg roll and 1.6 deg pitch, shift -161 mm in x; median surface distance 22 mm (both scans' wing tops are
glossy), headlamps then within 5 mm in x of the body scan's, the scuttle 21 mm closer than before. The engine itself
(the rocker cover) then sits about 160 mm further back in the body than the model's engine (PLAN: Differences seen
in Oliver's scans). Used for the body's engine-bay panels (sections) and for appearance; parts are not moved to it.
"""
from __future__ import annotations

import numpy as np

BODY_SCALE = 1329.15                        # mm per scan unit
BODY_ROT = np.array([[0.918251, 0.018605, -0.395562],
                     [-0.395814, 0.012555, -0.918245],
                     [-0.012118, 0.999748, 0.018893]])
BODY_TRANS = np.array([-1093.24, -64.49, -698.71])

ENGINE_SCALE = 605.122                      # mm per scan unit
ENGINE_ROT = np.array([[-0.952188, 0.027029, 0.304312],
                       [0.303641, -0.026275, 0.952423],
                       [0.033739, 0.999289, 0.016812]])
ENGINE_TRANS = np.array([72.64, 27.77, -352.95])

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
