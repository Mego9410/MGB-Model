"""Cockpit trim datums (QA fix round 1, cockpit): door card fittings shared by the trim (parts/body/interior.py) and
the door mechanisms behind the card (parts/body/mechanisms.py). Car frame as mgb.car_layout; heights are above the
road (body_shell_layout.z_of turns them into z).

All D: Oliver's keyframes kf128, kf131, kf137 (the left door, its card seen square on), positions scaled on the door's
length (DOOR_FRONT_X to DOOR_REAR_X) and height (sill to the capping).
"""
from __future__ import annotations

from mgb import body_shell_layout as S

_L = S.DOOR_FRONT_X - S.DOOR_REAR_X          # door length (928)

INNER_HANDLE = (S.DOOR_FRONT_X - 0.16 * _L, 795.0)    # inner release lever's pivot: front top, under the capping
WINDER = (S.DOOR_FRONT_X - 0.14 * _L, 640.0)          # window winder's spindle: front, just below the seam
PULL_HANDLE = (S.DOOR_FRONT_X - 0.52 * _L, 615.0)     # pull handle's centre: mid-door, below the seam
PULL_HANDLE_L = 150.0                                 # between its chrome end bosses' centres
CARD_SEAM_H = 712.0                                   # red-piped seam across the card, about 22 % down it
CARD_STITCH_H = (748.0, 784.0)                        # two stitched lines in the upper panel
