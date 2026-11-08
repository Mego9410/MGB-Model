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

# Seats (QA fix round 1, cockpit): |y| of each seat's centre line, per side (-1 the driver's, right; +1 the passenger's).
# D: Oliver's body scan (mgb.scan_layout.body_to_car), sections. The squab's sides at 850-900 above the road are at
# y -535/-125 (driver) and +105/+500 (passenger), the cushion tops' edges at x -1300..-1150 at -560/-95 and +80/+530:
# centres -330 and +303. P11b had both at 380, which put them 50 and 77 mm outboard. The floor's runner captive nuts
# (parts/body/structure.py floor_half) and the runners stand SEAT_RUNNER_DY either side of each centre line.
SEAT_Y = {-1: 345.0, 1: 340.0}
# Placed 15 (driver) and 37 mm (passenger) outboard of those centres: the cushions' inboard sides stop at the model's
# tunnel carpet (|y| 135 at the cushion's foot) and the handbrake (-142), which stand wider than the scan's tunnel.
SEAT_Y_SCAN = {-1: 330.0, 1: 303.0}
SEAT_RUNNER_DY = 85.0
