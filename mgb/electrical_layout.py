"""Electrical datums on the engine and in the engine bay (P10), car frame (mgb.car_layout):
X forward, Y to the car's left, Z up, origin on the engine centreline at the head joint face.

Body-mounted electrics (lamps, wipers, instruments, battery carriers, the inner wing items)
take their positions from mgb.body_layout, which P11 builds the body around.

What Haynes fixes (Ch 10, printed p161-201; Ch 2 Figs 2.1 and 2.6):
- The generator hangs on two upper pivot bolts and is set by a slotted adjusting link below
  it (Ch 10 Sec 6 para 1: "the two retaining bolts and the nut on the sliding link"; Fig 2.1
  arrows two bolts on top and the link bolt underneath). The front pivot bolt passes through
  an ear on the water pump (Fig 2.6 items 34-36), the rear one through a bracket on the block
  (item 14 and its screw 16), and the link (25) swings on a stud (17) screwed into the engine
  front. The 18ACR is removed "as described in Section 15" (Sec 20 para 2): terminal block off,
  link bolt out, mounting bolts slackened. Alternator mounting bolt 20 lbf ft, pulley nut
  25 lbf ft (p162).
- Starter: Lucas M418G inertia engaged on 18G engines (p162), "mounted on the right-hand
  lower side of the engine, and is held by two bolts" (Sec 23 para 1); 13.3 to 1 gear ratio
  (p162) is 120 / 9, so a 9-tooth pinion on the 120-tooth ring (P2 flywheel); the oil
  filter, the ignition coil and its bracket and the distributor come off before the starter
  (Sec 25 para 2), so they sit above it; mounting bolts 30 lbf ft (p162).
- The coil is on a bracket on the engine (Sec 25 para 2, above).

Published by suppliers (S): the 2 3/4 in alternator pulley (MGOC Spares 12G1054); 5/16 UNF
pivot and link bolts (MGOC Spares, dynamo-alternator fixings GHF104, GHF120); the adjusting
link 12H67 and its pillar 2A128 (MGOC Spares).

Derived (D), each with its method:
- ALT_AXIS: in cooling_layout (P2c set it; P10 moved it out to 200 mm from the water pump
  spindle so the 2 3/4 in pulley clears the fan blades, and the body clears the front plate's
  engine mounting holes); the belt follows it.
- The 18ACR body: stations along the shaft from Fig 10.3 (16AC, the same family) scaled to
  the pulley; the body passes back through a notch in the front plate's right-hand wing.
- Pivot line on the block side of the body, 80 mm from the shaft (lug length from Fig 10.3);
  the adjusting lug below, and the link stud in the engine front just outboard of the
  timing cover (Fig 2.1, photo 3.3: the link runs down and inboard under the pulley).
- Starter axis: P2's starter aperture (parts/engine/block/plates.py STARTER), on the line
  from the crank 164 mm out (ring gear and 9-tooth pinion pitch circles, 10 DP), at 205 deg.
  The motor lies forward of the rear plate beside the sump's rear tail; its commutator end
  stops short of the oil filter canister (P2 lube) so the filter comes off first as Haynes
  says. The sump and the block skirt get a recess for the yoke (STARTER_RECESS_R).
- Coil: vertical on a clamp bracket bolted to the small threaded boss on the right-hand side
  of the block (P2 block, x 67), between the oil filter and the dipstick, above the starter.
"""
from __future__ import annotations

import math
from pathlib import Path

from mgb import block_section as B, cooling_layout as C, engine_layout as E, gearbox_layout as G, spec as S
from mgb import ignition_layout as IG, timing_layout as T

IN = 25.4
ROOT = Path(__file__).resolve().parent.parent
_EP = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "block" / "end-plate.yaml")}
CZ = T.EL.crank_z

# ---- alternator (Lucas 18ACR) ---------------------------------------------------------------------
ALT_AXIS = C.ALTERNATOR_AXIS                         # (y, z) of the shaft
BELT_X = C.BELT_X                                    # pulley groove centre plane
PULLEY_OD = 2.75 * IN                                # S: MGOC Spares 12G1054, "alternator pulley 2 3/4"
# stations along the shaft, local z = car x - BELT_X (forward +)
PULLEY_Z = (-6.0, 6.0)
NUT_Z = (6.0, 13.5)
FAN_Z = (-30.0, -11.0)
DE_FACE_Z = -33.0                                    # drive end bracket front face
DE_Z = (-60.0, DE_FACE_Z)                            # drive end bracket
STATOR_Z = (-86.0, -60.0)                            # laminated stator ring between the brackets
SR_Z = (-136.0, -86.0)                               # slip ring end bracket
COVER_Z = (-166.0, -136.0)                           # moulded end cover
BODY_R = 63.0                                        # stator outside radius
BRACKET_R = 60.0

PIVOT = (-128.0, -66.0)                              # (y, z) of the two pivot bolts' common axis
LINK_LUG = (-160.0, -172.0)                          # (y, z) of the adjusting lug's tapped hole
LINK_STUD = (-86.0, -212.0)                          # (y, z) of the adjusting link stud in the engine front
FRONT_LUG_Z = (-43.0, DE_FACE_Z)                     # front pivot lug on the drive end bracket
REAR_LUG_Z = (-128.0, -116.0)                        # rear pivot lug on the slip ring end bracket
PUMP_EAR_X = (237.0, 247.0)                          # ear on the water pump flange carrying the front pivot
LINK_X = (BELT_X + DE_FACE_Z, BELT_X + DE_FACE_Z + 4.0)   # the link lies on the front face of the adjusting lug
REAR_BRACKET_BOSS = (124.0, -44.0)                   # (x, z) of the block's threaded boss, face at y -69 (P2 block)
BOSS_FACE_Y = B.YR - 7.0
REAR_EAR_X = (BELT_X + REAR_LUG_Z[0] - 8.0, BELT_X + REAR_LUG_Z[0] - 0.5)   # bracket ear behind the rear lug
FRONT_PLATE_NOTCH_R = 68.0                           # notch in the front plate's right wing round the body


def alt_local(lx, ly, lz):
    """Alternator frame -> car frame. Local z forward along the shaft from the belt plane,
    local y = car y about the shaft, local x = car z downward about the shaft."""
    ay, az = ALT_AXIS
    return (BELT_X + lz, ay + ly, az - lx)


def alt_lxly(y, z):
    """Car (y, z) -> alternator local (x, y)."""
    return (ALT_AXIS[1] - z, y - ALT_AXIS[0])


# ---- starter (Lucas M418G inertia engaged) ------------------------------------------------------
REAR_PLATE_FRONT_X = (G.BELL_FACE_X + _EP["engine.block.rear-plate"].nom("thickness"))   # -226.4: block side of the plate
STARTER_YZ = (-148.3, CZ - 70.0)                     # P2 plates.STARTER (aperture centre)
STARTER_ANGLE = math.degrees(math.atan2(STARTER_YZ[1] - CZ, STARTER_YZ[0]))   # about the crank, from +y
RING_TEETH, PINION_TEETH = 120, 9                     # 13.3 : 1 (H p162)
DP = 10.0                                            # diametral pitch (P2 ring gear, 120 teeth on 12 in)
PINION_PITCH_R = PINION_TEETH / DP * IN / 2
YOKE_R = 4.18 * IN / 2                               # D: Lucas M-series type number gives the yoke size (M418)
FLANGE_T = 9.0
STARTER_FRONT_X = -86.0                              # commutator end clear of the oil filter canister (x -77)
YOKE_X = (REAR_PLATE_FRONT_X + FLANGE_T + 6.0, STARTER_FRONT_X - 22.0)
STARTER_BOLT_R = 55.0                                 # two 3/8 in bolts through the flange, plate and bellhousing lobe
STARTER_BOLT_ANGLES = (115.0, 295.0)                  # about the starter axis, from +y toward +z: square to the line
                                                      # from the crank, upper outboard and lower inboard, outside the bell shell
PINION_REST_X = (-246.0, -233.0)                      # out of mesh, ahead of the ring (ring x -262.5..-250.5)
SHAFT_END_X = -292.0                                  # inside the bellhousing pocket (P5a casing, to x -297)
STARTER_RECESS_R = YOKE_R + 4.0                       # relief in the sump and block skirt round the yoke
STARTER_RECESS_X = (REAR_PLATE_FRONT_X - 1.0, STARTER_FRONT_X + 12.0)
TERMINAL_ANGLE = 120.0                                # terminal post on the commutator end bracket, up and outboard


def recess_cylinder(grow=0.0):
    """Solid cylinder along the starter axis that the sump and block skirt are relieved by."""
    from build123d import Cylinder, Location, Rot
    x0, x1 = STARTER_RECESS_X
    return Location(((x0 + x1) / 2, STARTER_YZ[0], STARTER_YZ[1])) * Rot(0, 90, 0) * Cylinder(STARTER_RECESS_R + grow, x1 - x0)


def in_starter_recess(x, y, z, grow=0.0):
    x0, x1 = STARTER_RECESS_X
    return x0 - grow <= x <= x1 + grow and math.hypot(y - STARTER_YZ[0], z - STARTER_YZ[1]) <= STARTER_RECESS_R + grow


def starter_bolt_points():
    sy, sz = STARTER_YZ
    return [(sy + STARTER_BOLT_R * math.cos(math.radians(a)), sz + STARTER_BOLT_R * math.sin(math.radians(a)))
            for a in STARTER_BOLT_ANGLES]


TERMINAL_Z = 78.0                                     # terminal post on the yoke, this far ahead of the plate face
TERMINAL_STACK = 16.0                                 # insulators, washers and nuts on the post above the yoke


def starter_terminal():
    """(x, y, z) of the cable eye's seat on the terminal post."""
    sy, sz = STARTER_YZ
    a = math.radians(TERMINAL_ANGLE)
    r = YOKE_R + TERMINAL_STACK
    return (REAR_PLATE_FRONT_X + TERMINAL_Z, sy + r * math.cos(a), sz + r * math.sin(a))


def starter_local(y, z):
    """Car (y, z) -> starter local (x, y): local z forward along the axis from the plate face,
    local x = car down, local y = car left."""
    return (STARTER_YZ[1] - z, y - STARTER_YZ[0])


# ---- ignition coil (Lucas HA12) ----------------------------------------------------------------
COIL_BOSS = (67.0, -44.0)                             # (x, z) of the block's other threaded boss (P2 block)
COIL_AXIS = (40.0, BOSS_FACE_Y - 8.0 - 32.5)          # (x, y) of the vertical coil axis
COIL_CAN = (-150.0, -22.0)                            # z of the can bottom and the top of the moulded cap seat
CAP_CENTRE = IG.to_engine((0.0, 0.0, IG.CAP_Z + IG.CAP_H))   # distributor cap centre tower (king lead)
_LT = (39.0 * math.cos(math.radians(120.0)), 39.0 * math.sin(math.radians(120.0)), IG.BODY_Z + 26.0)
DIST_LT = IG.to_engine(_LT)                           # distributor low tension terminal stud tip (P3 distributor body)
DIST_AXIS = IG.AXIS                                   # the king lead enters the cap centre along this
COIL_TOP_Z = COIL_CAN[1] + 24.0                       # top of the HT tower
COIL_TERMINALS = {"SW": (COIL_AXIS[0] - 17.0, COIL_AXIS[1] + 10.0), "CB": (COIL_AXIS[0] + 17.0, COIL_AXIS[1] + 10.0)}
COIL_TERMINAL_Z = COIL_CAN[1] + 14.0                  # top of the low tension terminal nuts

# ---- starter solenoid on the right inner wing (mgb.body_layout.SOLENOID) ----------------------
from mgb import body_layout as _BL                    # noqa: E402

SOL_R = 27.0
SOL_C = (_BL.SOLENOID[0], _BL.SOLENOID[1] + 4.0 + SOL_R, _BL.SOLENOID[2])   # vertical body axis through here
SOL_LEN = 64.0


def sol_terminal(which):
    """Top of the battery (+1) or starter (-1) stud on the solenoid cap."""
    cx, cy, cz = SOL_C
    return (cx + which * 15.0, cy, cz + SOL_LEN / 2 + 26.0)


def speedo_cable_end():
    """(point, direction) of the speedometer cable stub's end on the overdrive angle drive
    (P5b gearbox.od-casing.cable-end), in the car frame."""
    import importlib.util
    from build123d import Location, Rot
    spec = importlib.util.spec_from_file_location("_odc", ROOT / "parts" / "gearbox" / "od_casing.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    loc = G.GF * m._speedo_loc() * Rot(0, 0, m.ANGLE_ROT) * Location((-43.0, 0, -m.ANGLE_OUT)) * Rot(0, -90, 0)
    a, b = (loc * Location((0, 0, 0))).position, (loc * Location((0, 0, 70.0))).position
    d = (b - a).normalized()
    return (b.X, b.Y, b.Z), (d.X, d.Y, d.Z)


# ---- gauge connections on the engine (oil pressure pipe, temperature bulb) ----------------------
OIL_UNION = (-200.0, B.YR - 6.0 - 10.0, B.LEDGE_Z - 4.0)   # on the main oil gallery's outer face, near the rear
TEMP_BULB = (205.0, -75.8, 32.0)                       # gland nut on the head's right face, ahead of No 1 plug
