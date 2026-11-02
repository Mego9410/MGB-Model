"""Cooling layout: water pump, fan, belt drive, radiator and hoses (engine frame).

Haynes Ch 2: Figs 2.2, 2.4, 2.6; photos 7.6, 9.3, 9.5. The pump bolts to the top of
the block front face in the notch of the front plate; its pulley lines up with the
crankshaft pulley groove (mgb.timing_layout); the radiator sits ahead of the fan.
Positions are derived (D).
"""
from __future__ import annotations

import math

from mgb import timing_layout as T

PUMP_FACE_X = T.BLOCK_FRONT                # pump flange on the block front face
PUMP_AXIS = (-8.0, -42.0)                  # (y, z) of the spindle
BELT_X = 291.3                             # crankshaft pulley groove centre plane
PULLEY_PITCH = {"crank": 60.0, "pump": 50.0, "alternator": 32.0}   # alternator: 2 3/4 in pulley (P10)
ALTERNATOR_AXIS = (-198.0, -106.0)         # 18ACR on the right-hand side (P10, mgb.electrical_layout): its 2 3/4 in
                                           # pulley 200 mm from the pump spindle clears the fan blades

RAD_CORE = (362.0, 424.0)                  # core x from/to (rear and front faces)
RAD_Y = (-215.0, 215.0)
RAD_CORE_Z = (-200.0, 120.0)
RAD_TOP_TANK = (120.0, 178.0)
RAD_BOTTOM_TANK = (-252.0, -200.0)
TOP_INLET = (RAD_CORE[0], -18.0, 150.0)    # top tank inlet stub, rear face (lines up with the thermostat outlet)
BOTTOM_OUTLET = (RAD_CORE[0], -82.0, -228.0)
FILLER = (RAD_CORE[0] + 31.0, 110.0, RAD_TOP_TANK[1])

ELBOW_OUTLET = (265.0, -18.0, 139.8)       # end of the thermostat outlet elbow spigot (head assembly)
ELBOW_DIR = (0.904, 0.0, 0.428)
PUMP_INLET = (262.0, -64.0, -100.0)        # end of the pump inlet spigot
PUMP_INLET_DIR = (0.0, -0.55, -0.835)


def belt_loop(grow: float, samples: int = 72):
    """Convex outline (y, z) the belt wraps: the three pulley pitch circles grown by `grow`."""
    circles = [((0.0, T.CRANK[1]), PULLEY_PITCH["crank"]), (PUMP_AXIS, PULLEY_PITCH["pump"]),
               (ALTERNATOR_AXIS, PULLEY_PITCH["alternator"])]
    pts = []
    for (cy, cz), r in circles:
        for k in range(samples):
            a = 2 * math.pi * k / samples
            pts.append((round(cy + (r + grow) * math.cos(a), 3), round(cz + (r + grow) * math.sin(a), 3)))
    return T._hull(pts)
