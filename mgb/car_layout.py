"""Where the engine sits in the car, and the car-level datums every chassis, running-gear
and body assembly is placed from.

The engine frame is the car frame: X forward, Y to the car's left (near side), Z up,
origin on the engine centreline at the cylinder head joint face (mgb.engine_layout). The
engine is taken as level and on the car centreline. Everything outside the engine is
positioned from the datums below, so moving the engine in the car is a one-line change.

Published figures (S): wheelbase, tracks, overall length, width, height and ground
clearance from the MGB specification (mgexp.com "Dimensions & Weight"; CAMS historic
data sheet MG MGB 1962-73, motorsport.org.au). Tyre size 5.60-14 and wire wheel rim
4 1/2J x 14 from Haynes Ch 11 specs, printed p203 (early models: 5.60 x 14 tubed crossply).

Derived (D): the fore-aft position of the engine against the front wheels and its
height above the ground are not published. The front wheel axis is set just behind the
front main bearing (cutaway drawings of the MGB put the front hubs level with the front of the
block). Oliver's engine-bay scan puts his engine 95-166 mm further back in the body than this
(the polished rocker cover's top runs x -325..+100 against our -200..+195: 95-125 mm behind ours
with the scan registered on the wings and headlamps, 166 mm against the scan's own scuttle vent).
P12 found that any set-back over 24 mm (88 mm with the pinion flange at the carrier nose)
conflicts with the published propeller shaft (see PLAN.md, "Engine set-back: open conflict"), so
the datum is not moved. The crank height comes from the
wheel centre height plus the sump clearing the ground by a little more than the published 4.2 in
minimum clearance.

Body stations. The body, chassis, suspension and the fittings on them were drawn with the
front wheel axis at x 150 (BODY_STATION_FRONT_AXLE). Their hard-coded fore-aft positions are
written as body stations and turned into car x with bx() (points: bxp(), x-keyed tables:
bxt()), so they follow FRONT_AXLE_X. Engine-mounted parts stay in the engine frame. P12 (work in
progress) converted the layout modules; the part modules and the bridging runs (hoses, cables,
pipes, harness, exhaust, mountings) still have to be audited before FRONT_AXLE_X can be moved.
"""
from __future__ import annotations

from mgb import engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout
from pathlib import Path

IN = 25.4
ROOT = Path(__file__).resolve().parent.parent
_HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
_EL = E.layout(_HL)

# ---- published (S) ---------------------------------------------------------------------------
WHEELBASE = 91.0 * IN                  # 2311.4
TRACK_FRONT = 49.0 * IN                # 1244.6
TRACK_REAR = 49.25 * IN                # 1251.0
LENGTH = 153.2 * IN                    # 3891.3
WIDTH = 59.9 * IN                      # 1521.5
HEIGHT_HOOD_UP = 49.4 * IN             # 1254.8
GROUND_CLEARANCE = 4.2 * IN            # 106.7

# ---- tyres (H Ch 11 specs; section ratio D) -------------------------------------------------
RIM_D = 14.0 * IN
TYRE_SECTION = 5.60 * IN
TYRE_D = RIM_D + 2 * 0.92 * TYRE_SECTION     # 5.60-14 crossply, ~92 % profile (D)
ROLLING_R = TYRE_D / 2 - 8.0                 # laden deflection (D)

# ---- derived datums in the engine frame (D) -----------------------------------------------
FRONT_AXLE_X = 150.0                   # front wheel axis, just behind the front main bearing (x 205); Oliver's scan
                                       # says 245-316 (P12, above), not applied: propeller shaft conflict
BODY_STATION_FRONT_AXLE = 150.0        # the front wheel axis in body stations (the frame the body was drawn in)
BODY_DX = FRONT_AXLE_X - BODY_STATION_FRONT_AXLE     # car x of a body station minus the station


def bx(s):
    """Car x of a body station s (body, chassis and running-gear fore-aft positions)."""
    return s + BODY_DX


def bxp(p):
    """A point (x, ...) given in body stations, in the car frame."""
    return (bx(p[0]),) + tuple(p[1:])


def bxt(table):
    """A table [(station, value...), ...] keyed on body stations, keyed on car x."""
    return [bxp(p) for p in table]


REAR_AXLE_X = FRONT_AXLE_X - WHEELBASE
CRANK_HEIGHT = 330.0                   # crank axis above the ground
GROUND_Z = _EL.crank_z - CRANK_HEIGHT  # road surface
WHEEL_Z = GROUND_Z + ROLLING_R         # wheel centres, front and rear (static laden)
FRONT_OVERHANG = 681.0                 # bumper (overriders) ahead of the front axle (D: profile photo 29 scaled on the
                                       # wheelbase, depth-corrected; the rear overhang, 899, is the rest of the length)
FRONT_X = FRONT_AXLE_X + FRONT_OVERHANG              # front of the bumper
REAR_X = FRONT_X - LENGTH                             # rear of the bumper


def front_wheel(side):
    """Front wheel centre; side +1 = left (near side), -1 = right (off side)."""
    return (FRONT_AXLE_X, side * TRACK_FRONT / 2, WHEEL_Z)


def rear_wheel(side):
    return (REAR_AXLE_X, side * TRACK_REAR / 2, WHEEL_Z)


SUMP_BOTTOM_Z = _EL.sump_z - 118.0     # lowest point of the sump (specs/engine/lube)

# Engine-side face of the bulkhead (dash panel) behind the engine (D). Not published. Set
# 550 mm behind the front wheel axis, 174 mm behind the engine rear plate: room for the
# pedal box and the master cylinders behind the right-hand rear of the cylinder head (Haynes
# Fig 5.3; Ch 5 Sec 5 reaches them from the engine bay), with the gearbox bellhousing
# running back under it into the tunnel. The body phase (P11) builds the bulkhead on it.
BULKHEAD_X = FRONT_AXLE_X - 550.0
