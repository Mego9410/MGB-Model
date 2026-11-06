"""Cooling layout: water pump, fan, belt drive, radiator and hoses (engine frame).

Haynes Ch 2: Figs 2.2, 2.4, 2.6; photos 7.6, 9.3, 9.5. The pump bolts to the top of
the block front face in the notch of the front plate; its pulley lines up with the
crankshaft pulley groove (mgb.timing_layout); the radiator sits ahead of the fan.
Positions are derived (D). The radiator is on the body (its x in body stations, car_layout.bx); the pump, fan and
hose spigots are on the engine, so the hoses bridge the two.
"""
from __future__ import annotations

import math

from mgb import car_layout as CL, timing_layout as T

PUMP_FACE_X = T.BLOCK_FRONT                # pump flange on the block front face
PUMP_AXIS = (-8.0, -42.0)                  # (y, z) of the spindle
BELT_X = 291.3                             # crankshaft pulley groove centre plane
PULLEY_PITCH = {"crank": 60.0, "pump": 50.0, "alternator": 32.0}   # alternator: 2 3/4 in pulley (P10)
ALTERNATOR_AXIS = (-198.0, -106.0)         # 18ACR on the right-hand side (P10, mgb.electrical_layout): its 2 3/4 in
                                           # pulley 200 mm from the pump spindle clears the fan blades

RAD_CORE = (CL.bx(362.0), CL.bx(424.0))    # core x from/to (rear and front faces): body-mounted, body stations (car_layout.bx)
RAD_Y = (-215.0, 215.0)
RAD_CORE_Z = (-200.0, 120.0)
RAD_TOP_TANK = (120.0, 178.0)
RAD_BOTTOM_TANK = (-252.0, -200.0)
TOP_INLET = (RAD_CORE[0], -18.0, 150.0)    # top tank inlet stub, rear face (lines up with the thermostat outlet)
BOTTOM_OUTLET = (RAD_CORE[0], -82.0, -228.0)
FILLER = (RAD_CORE[0] + 31.0, 110.0, RAD_TOP_TANK[1])    # filler neck's centre on the top tank's top face
# QA fix round 1 (front finding 9): the cap stood 23 mm through the bonnet (neck top z 201, cap top 221, bonnet skin
# about 197 over it). The real bonnet is clear, so the neck now takes its height from the bonnet's inner face over the
# cap (mgb.body_shell_layout top_h less the 1 mm skin) less BONNET_CLEARANCE and the cap's height: on the present
# bonnet the neck stands in a shallow well in the tank top rather than 23 mm above it. It follows the bonnet if that
# changes.
FILLER_CAP_D = 52.0                        # pressure cap (specs/cooling: diameter)
FILLER_CAP_H = 13.0                        # cap height over the neck's sealing face (a low domed cap with two ears)
BONNET_CLEARANCE = 6.0                     # cap top to the bonnet's inner face
NECK_UP = 23.0                             # neck height above the tank where there is room (P2)


def _bonnet_inner_over(x, y, r):
    """Lowest z of the bonnet's inner face over a disc of radius r at (x, y) (car frame)."""
    from mgb import body_shell_layout as S
    pts = [(x, y)] + [(x + r * math.cos(2 * math.pi * k / 12), y + r * math.sin(2 * math.pi * k / 12)) for k in range(12)]
    return min(S.z_of(S.top_h(px, py)) for px, py in pts) - S.T


BONNET_INNER_AT_FILLER = float(_bonnet_inner_over(FILLER[0], FILLER[1], FILLER_CAP_D / 2 + 2.0))
FILLER_NECK_TOP = min(FILLER[2] + NECK_UP, BONNET_INNER_AT_FILLER - BONNET_CLEARANCE - FILLER_CAP_H)

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
