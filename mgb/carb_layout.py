"""Twin SU HS4 carburettors and air cleaners on the inlet manifold (engine frame).

Haynes Ch 3: Fig 3.1 (air cleaner), Figs 3.10-3.12 (HS4), photos 17.1, 18.2-18.5.
Each carburettor's air passage runs along +Y from the inlet manifold flange; the
piston and jet axis is vertical. Float chambers sit outboard of each instrument
(front body and rear body are handed, Fig 3.10 items 1 and 2), the linkage between
them. Stack-up and sizes are derived (D) except the published bore and jet.
"""
from __future__ import annotations

from pathlib import Path

from mgb import spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parent.parent
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))

MANIFOLD_FACE_Y = 176.0                    # carburettor flanges of the inlet manifold (parts/engine/manifolds)
AXIS_Z = 48.0
CARB_X = [p[0] * 0.95 for p in HL.inlet_ports]   # front (+) and rear (-) instruments
STUD_DX = 24.0                             # flange studs either side of the bore (manifold holes)
GASKET = 0.8
SHIELD_T = 1.6
DISTANCE_T = 12.7
BODY_Y = MANIFOLD_FACE_Y + GASKET + SHIELD_T + GASKET + DISTANCE_T + GASKET   # carburettor flange face
BODY_LEN = 86.0
PISTON_Y = BODY_Y + 44.0                   # vertical axis of the piston, needle and jet
SPINDLE_Y = BODY_Y + 16.0
CHAMBER_BASE_Z = AXIS_Z + 42.0
INTAKE_Y = BODY_Y + BODY_LEN               # air intake flange face
CLEANER_BOLT_DX = 28.0                     # air cleaner bolts either side of the intake (horizontal pair)
CHAMBER_SCREW_R = 37.0
FLOAT_DX = 58.0                            # float chamber axis outboard of the jet
FUEL_SPIGOT = 22.0                         # float lid inlet spigot, toward the engine (-Y) from the lid axis
BREATHER_SPIGOT = (0.0, 30.0)              # on top of the front air cleaner case, case-local (x, y)


def side(x):
    """Outboard direction along X for the instrument at x (front +1, rear -1)."""
    return 1.0 if x > 0 else -1.0


def float_inlet(x, chamber_height):
    """End of the float chamber lid inlet spigot for the instrument at x (engine frame)."""
    cx = x + side(x) * FLOAT_DX
    return (cx, PISTON_Y - FUEL_SPIGOT, AXIS_Z - 50 + chamber_height * 0.5 + 12)


def breather_spigot_top(depth_offset=4.8, case_d=150.0):
    """Top of the breather spigot on the front air cleaner case (engine frame)."""
    bx, by = BREATHER_SPIGOT
    return (CARB_X[0] + bx, INTAKE_Y + depth_offset + by, AXIS_Z + case_d / 2 + 16)
