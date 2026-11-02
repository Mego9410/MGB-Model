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
BELL_MAX_R = 172.0                                   # outside of the wall round the ring gear, clear of the slave (D)

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
