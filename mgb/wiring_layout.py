"""Wiring harness layout (P10b): the harness paths, the joints and connectors, the terminals of the
parts P10b adds, and the route of every wire, car frame (mgb.car_layout: X forward, Y to the car's
left, Z up, origin on the engine centreline at the head joint face).

How a wire is laid out: each wire's spec (specs/electrical/wiring-*.yaml) names its two terminals
(mgb.electrical_layout.terminals()). Every terminal hangs off a node of the harness graph below. The
wire leaves its terminal along the terminal's direction, runs to the node, follows the harness
along the shortest path through the graph to the other terminal's node, and goes out to that
terminal. Along each harness path the wires lie side by side in a tight bundle: each wire on a path
gets its own slot in hexagonal rings round the path's centre line (in a frame carried along the
path), so wires do not run through one another; they cross over at the nodes where they change
paths, as real harness wires do.

Sources:
- Cable sizes (S): Lucas strand counts as used on BMC harnesses; nominal outside diameters from
  Auto Electric Supplies, "Standard cable" table (9/0.30 2.3 mm, 14/0.30 2.6, 28/0.30 3.3, 44/0.30
  3.7, 65/0.30 5.0 mm), current ratings from Autosparks "PVC cable".
- Circuit topology and colours (H): Haynes Fig 10.26 (wiring diagram, models up to 1967, printed
  p190, key printed p189) and Fig 6.19 (overdrive circuit, printed p131).
- Harness routes, joint and connector positions (D): the P10 loom's routes (engine bay along the right
  inner wing top, across behind the grille, back along the left wing; the facia harness behind the
  instruments; the rear harness down the right-hand sill and over the arch to the boot), set so they
  clear the engine, gearbox, brakes and body datums (interference check, PLAN.md).
"""
from __future__ import annotations

import heapq
import math
from functools import lru_cache
from pathlib import Path

from mgb import body_layout as BL, brake_layout as BRK, car_layout as CL, spec as S

ROOT = Path(__file__).resolve().parent.parent
IN = 25.4

# ---- cables ----------------------------------------------------------------------------------------
CABLE_OD = {"9/0.30": 2.3, "14/0.30": 2.6, "28/0.30": 3.3, "44/0.30": 3.7, "65/0.30": 5.0}   # S, see above
CABLE_REF = "Auto Electric Supplies, standard cable: nominal outside diameter"
SIDES = 8                                           # cross-section of the drawn cables (octagon)

# ---- fittings (D: sizes of the common Lucas parts, drawn from catalogue photographs) --------------
LUCAR_SLEEVE = (16.0, 8.4, 4.6)                     # female Lucar with its PVC sleeve: length, width, thickness
PIN_SLEEVE = (14.0, 3.0)                            # sleeved bullet-type female: length, radius
EYE_OUT = 3.6                                       # ring terminal: eye outside radius beyond the hole
EXIT = 10.0                                         # straight run of cable behind each fitting

# ---- optional P11a datums (fuel pump and tank unit) -------------------------------------------------
from mgb import fuel_supply_layout as FS, steering_layout as SL, underbody_layout as U   # noqa: E402  (P11a: pump, tank, floor, heelboard)


def _add(a, b, k=1.0):
    return tuple(x + k * y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(v):
    n = math.sqrt(_dot(v, v))
    return tuple(c / n for c in v) if n > 1e-12 else (1.0, 0.0, 0.0)


def _neg(v):
    return tuple(-c for c in v)


def _perp(d):
    ref = (0.0, 0.0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0.0, 0.0)
    return _unit(_cross(_cross(d, ref), d))


# ---- harness graph (D) -------------------------------------------------------------------------------
RY = -BL.INNER_WING_Y + 25.0                        # run along the top of the right-hand inner wing
LY = BL.INNER_WING_Y - 25.0
RZ = 118.0
GX, GY, GZ = BL.HARNESS_GROMMET
FX = BL.FACIA_X + 120.0                             # facia harness: behind the instruments and switches
FZ = BL.IP_Z + 30.0
FRONT_X = BL.HORN_PANEL_X - 30.0                    # across behind the grille, ahead of the radiator
SILL_Y = -(BL.HALF_W - 170.0)
SILL_Z = -350.0
ARCH = (-480.0, -90.0)                              # over the rear wheel arch, clear of the axle and springs
RLX = BL.REAR_LAMP_X + 30.0
PUMP_X = FS.PUMP_X
TANK_X = FS.SENDER[0]
HEEL_X = U.HEELBOARD_X + 30.0                       # up the cockpit face of the heelboard to the tonneau floor
TONNEAU_RUN_Z = U.HEEL_STEP_Z + 10.0                # back over the heelboard's step under the squabs' feet (QA fix round 1,
                                                     # cockpit: the shelf rose; through a grommet in its riser)

# direction indicator switch: clamped on P9's outer column tube just below the wheel
COL_AXIS = SL.COLUMN_DIR                                       # up the column, toward the wheel
COLUMN_SWITCH = SL.col(SL.OUTER_TUBE_T[1] - 56.0)            # switch body centre on the column axis, just below the tube's
                                                               # swaged top for the upper bearing (P9) (D)
COL_X = _unit(_add((0.0, 1.0, 0.0), COL_AXIS, -COL_AXIS[1]))  # switch frame: x across the car, square to the column
COL_Y = _cross(COL_AXIS, COL_X)                                # y: down and forward (the switch's lower face)
COL_TOP = _add(COLUMN_SWITCH, _cross(COL_AXIS, COL_X), -60.0)  # above the column, for the horn push lead
TOE_TILT_DEG = math.degrees(math.atan2(U.TOE_TOP[1] - U.TOE_FOOT[1], U.TOE_TOP[0] - U.TOE_FOOT[0]))
DIP_X = -445.0                                      # on the toe board, left of the clutch pedal (P8: y -215)
DIP_SWITCH = (DIP_X - 1.0, -165.0, U.toe_z(DIP_X) + 1.6)     # base centre on the toe board's cabin face (D)
DIP_TILT = math.radians(TOE_TILT_DEG)
DIP_N = (-math.sin(DIP_TILT), 0.0, math.cos(DIP_TILT))          # outward normal of the toe board (up and back)
DIP_U = (math.cos(DIP_TILT), 0.0, math.sin(DIP_TILT))           # up the slope (forward and up)

NODES = {
    # engine bay, right
    "gr.bay": (GX + 12.0, GY, GZ), "bay.flasher": (BL.FLASHER[0], RY, RZ), "bay.fuse": (BL.FUSE_BOX[0], RY, RZ),
    "bay.cb": (BL.CONTROL_BOX[0], RY, RZ), "bay.sol": (BL.SOLENOID[0], RY, RZ), "bay.eng": (-5.0, RY, RZ),
    "bay.fr": (BL.INNER_WING_X[1] - 20.0, RY, RZ), "bay.corner.R": (470.0, -330.0, 30.0),
    "bay.front.R": (FRONT_X, -300.0, -40.0), "bay.front.M": (FRONT_X, 0.0, -40.0), "bay.front.L": (FRONT_X, 300.0, -40.0),
    "bay.corner.L": (470.0, 330.0, 30.0), "bay.fl": (BL.INNER_WING_X[1] - 60.0, LY, RZ - 10.0),
    "bay.relay": (BL.OD_RELAY[0], LY, RZ - 10.0), "bay.vac": (BL.BULKHEAD_X + 40.0, LY - 60.0, 80.0),
    # engine bay branches
    "fl.n": (BL.FLASHER[0] - 2.0, RY + 26.0, -45.0), "fuse.n": (BL.FUSE_BOX[0] + 4.0, RY + 20.0, -12.0),
    "cb.n": (BL.CONTROL_BOX[0], RY + 34.0, -32.0), "sol.n": (BL.SOLENOID[0] - 6.0, RY + 40.0, 20.0),
    "eng.up": (-15.0, -305.0, 45.0), "eng.alt": (40.0, -246.0, -70.0), "eng.coil": (88.0, -165.0, 5.0),
    "eng.dist": (-38.0, -74.0, -20.0), "stop.n": (BRK.FOUR_WAY[0] + 46.0, -251.0, -150.0),
    "heater.n": (BL.HEATER_CONNECTOR[0] + 6.0, BL.HEATER_CONNECTOR[1] - 30.0, BL.HEATER_CONNECTOR[2] - 4.0),
    "hl.R.n": (BL.HEADLAMP_RIM_X - 175.0, -520.0, BL.HEADLAMP_Z + 10.0), "hl.L.n": (BL.HEADLAMP_RIM_X - 175.0, 520.0, BL.HEADLAMP_Z + 10.0),
    "side.R.n": (BL.SIDELAMP_X - 65.0, -555.0, BL.SIDELAMP_Z + 25.0), "side.L.n": (BL.SIDELAMP_X - 65.0, 555.0, BL.SIDELAMP_Z + 25.0),
    "horn.R.n": (FRONT_X + 6.0, -300.0, -92.0), "horn.L.n": (FRONT_X + 6.0, 300.0, -92.0),
    "relay.n": (BL.OD_RELAY[0] + 6.0, LY - 12.0, -36.0), "vac.n": (BL.BULKHEAD_X + 22.0, BL.OD_VACUUM_SWITCH[1], 2.0),
    "od.0": (BL.OD_RELAY[0] - 40.0, LY - 25.0, -70.0), "od.1": (BL.BULKHEAD_X + 30.0, 215.0, -35.0),
    "od.2": (BL.BULKHEAD_X - 30.0, 120.0, -120.0), "od.3": (-651.0, -60.0, -110.0), "iso.n": (-756.0, -62.0, -122.0),
    "od.4": (-815.0, -112.0, -190.0), "odsol.n": (-885.0, -160.0, -250.0),
    # cabin: through the grommet to the facia
    "gr.cab": (GX - 12.0, GY, GZ), "fa.in": (GX - 120.0, -345.0, 200.0),
    # facia run, right to left along the instruments and switches (P11b moved them to Oliver's facia layout)
    "fa.R": (FX, -600.0, FZ), "fa.fuel": (FX, BL.INSTRUMENTS["fuel-gauge"][0] + 30.0, FZ),
    "fa.tach": (FX, BL.INSTRUMENTS["tachometer"][0], FZ), "fa.drv": (FX, BL.DRIVER_Y, FZ),
    "fa.speedo": (FX, BL.INSTRUMENTS["speedometer"][0] - 36.0, FZ),
    "fa.speedo.n": (BL.FACIA_X + 107.0, BL.INSTRUMENTS["speedometer"][0] - 26.0, BL.BINNACLE_Z - 42.0),
    "fa.dual": (FX, BL.INSTRUMENTS["dual-gauge"][0] - 26.0, FZ), "fa.map": (FX, BL.SWITCHES["map-lamp"][0] + 14.0, FZ),
    "fa.panel": (FX, BL.SWITCHES["panel-lamp"][0], FZ), "fa.ign": (FX, BL.SWITCHES["ignition"][0], FZ),
    "fa.heat": (FX, BL.SWITCHES["heater"][0], FZ), "fa.light": (FX, BL.SWITCHES["lighting"][0], FZ),
    "fa.L": (FX + 60.0, 300.0, 150.0),
    "wiper.n": (BL.WIPER_MOTOR[0] + 55.0, BL.WIPER_MOTOR[1] + 82.0, 60.0),
    "dip.n": _add(_add(DIP_SWITCH, DIP_U, 62.0), DIP_N, 26.0),
    "col.n": _add(_add(COLUMN_SWITCH, COL_Y, 60.0), COL_AXIS, -30.0), "col.top": _add(COL_TOP, COL_AXIS, 30.0),
    "fa.earth.n": (BL.FACIA_X + 95.0, -215.0, BL.IP_Z - 105.0),
    # rear harness
    "re.0": (BL.FACIA_X + 60.0, SILL_Y, 0.0), "re.sill": (BL.FACIA_X - 80.0, SILL_Y, SILL_Z),
    "re.pump": (HEEL_X, SILL_Y, SILL_Z), "pump.n": (PUMP_X + 8.0, -400.0, -330.0), "re.heel": (HEEL_X, SILL_Y, TONNEAU_RUN_Z),
    "re.arch": (-1640.0, ARCH[0], ARCH[1]), "re.tank": (TANK_X, ARCH[0], ARCH[1]), "tank.n": (TANK_X + 30.0, -420.0, -200.0),
    "re.boot": (BL.REAR_X + 400.0, ARCH[0], ARCH[1]), "re.corner.R": (RLX + 60.0, -560.0, BL.REAR_LAMP_Z - 100.0),
    "re.M": (RLX + 40.0, 0.0, BL.REAR_LAMP_Z - 120.0), "re.corner.L": (RLX + 60.0, 560.0, BL.REAR_LAMP_Z - 100.0),
    "rear.R.n": (RLX + 10.0, -BL.REAR_LAMP_Y + 6.0, BL.REAR_LAMP_Z - 40.0), "rear.L.n": (RLX + 10.0, BL.REAR_LAMP_Y - 6.0, BL.REAR_LAMP_Z - 40.0),
    "plate.R.n": (BL.NUMBER_LAMP[0] + 60.0, -BL.NUMBER_LAMP[1] - 20.0, BL.NUMBER_LAMP[2] + 60.0),
    "plate.L.n": (BL.NUMBER_LAMP[0] + 60.0, BL.NUMBER_LAMP[1] + 20.0, BL.NUMBER_LAMP[2] + 60.0),
    "boot.earth.n": (BL.EARTH_POINTS["boot"][0][0] + 40.0, BL.EARTH_POINTS["boot"][0][1] + 40.0, BL.EARTH_POINTS["boot"][0][2] + 20.0),
}

# (a, b, intermediate points, sleeved) - sleeved paths are the braided main runs of the harness
EDGES = [
    ("gr.bay", "bay.flasher", [(GX + 24.0, -412.0, GZ - 4.0), (GX + 40.0, RY + 8.0, RZ)], True),   # over P11a's fuel pipe
    ("bay.flasher", "bay.fuse", [], True), ("bay.fuse", "bay.cb", [], True), ("bay.cb", "bay.sol", [], True),
    ("bay.sol", "bay.eng", [], True), ("bay.eng", "bay.fr", [], True),
    ("bay.fr", "bay.corner.R", [(400.0, RY + 20.0, 90.0)], True), ("bay.corner.R", "bay.front.R", [], True),
    ("bay.front.R", "bay.front.M", [], True), ("bay.front.M", "bay.front.L", [], True), ("bay.front.L", "bay.corner.L", [], True),
    ("bay.corner.L", "bay.fl", [(400.0, LY - 20.0, 85.0)], True), ("bay.fl", "bay.relay", [], True),
    ("bay.relay", "bay.vac", [], True),
    ("bay.flasher", "fl.n", [(BL.FLASHER[0] + 24.0, RY + 26.0, 60.0)], False),
    ("bay.fuse", "fuse.n", [(BL.FUSE_BOX[0] + 4.0, RY + 20.0, 70.0)], False),
    ("bay.cb", "cb.n", [(BL.CONTROL_BOX[0] + 66.0, RY + 34.0, 90.0), (BL.CONTROL_BOX[0] + 66.0, RY + 34.0, -10.0)], False),
    ("bay.sol", "sol.n", [], False),
    ("bay.eng", "eng.up", [(-10.0, -360.0, 90.0)], False), ("eng.up", "eng.alt", [(20.0, -255.0, -20.0)], False),
    ("eng.up", "eng.coil", [(40.0, -228.0, 45.0)], False),
    ("gr.bay", "stop.n", [(BL.BULKHEAD_X + 20.0, -385.0, 150.0), (BL.BULKHEAD_X + 30.0, -385.0, -40.0),   # between the
                          (BL.BULKHEAD_X + 30.0, -362.0, -150.0),          # pedal box (moved out) and the valance fittings
                          (BL.BULKHEAD_X + 55.0, -362.0, -178.0), (BL.BULKHEAD_X + 55.0, -290.0, -178.0)], False),
    # down off the bulkhead face outboard of P11a's fuel pipe and the pedal box, under P9's column and P8's
    # master cylinder pipe, then up to the stop lamp switch from ahead of it
    ("gr.bay", "heater.n", [(BL.BULKHEAD_X + 18.0, -220.0, 175.0)], False),
    ("bay.corner.R", "hl.R.n", [], False), ("hl.R.n", "side.R.n", [(BL.HEADLAMP_RIM_X - 110.0, -545.0, BL.SIDELAMP_Z + 70.0)], False),
    ("bay.corner.L", "hl.L.n", [], False), ("hl.L.n", "side.L.n", [(BL.HEADLAMP_RIM_X - 110.0, 545.0, BL.SIDELAMP_Z + 70.0)], False),
    ("bay.front.R", "horn.R.n", [], False), ("bay.front.L", "horn.L.n", [], False),
    ("bay.relay", "relay.n", [(BL.OD_RELAY[0] + 34.0, LY - 12.0, 40.0)], False),
    ("bay.vac", "vac.n", [], False),
    ("relay.n", "od.0", [], True), ("od.0", "od.1", [], True), ("od.1", "od.2", [], True), ("od.2", "od.3", [], True),
    ("od.3", "iso.n", [], False), ("iso.n", "od.4", [], True), ("od.4", "odsol.n", [], True),
    # through the bulkhead grommet
    ("gr.bay", "gr.cab", [], True), ("gr.cab", "fa.in", [], True), ("fa.in", "fa.drv", [(-600.0, -350.0, 262.0)], True),
    ("fa.R", "fa.fuel", [], True), ("fa.fuel", "fa.tach", [], True), ("fa.tach", "fa.drv", [], True),
    ("fa.drv", "fa.speedo", [], True), ("fa.speedo", "fa.dual", [], True), ("fa.dual", "fa.map", [], True),
    ("fa.map", "fa.ign", [], True), ("fa.drv", "fa.panel", [], True), ("fa.ign", "fa.heat", [], True),
    ("fa.heat", "fa.light", [], True), ("fa.light", "fa.L", [(FX + 30.0, 220.0, FZ - 40.0)], True),
    ("fa.L", "wiper.n", [(BL.WIPER_MOTOR[0] + 60.0, BL.WIPER_MOTOR[1] + 40.0, 110.0)], True),
    ("fa.drv", "dip.n", [(FX + 70.0, BL.DRIVER_Y + 60.0, 120.0), (-470.0, DIP_SWITCH[1] + 6.0, -60.0)], True),
    ("fa.drv", "col.n", [(FX - 20.0, BL.DRIVER_Y - 50.0, FZ - 150.0), (BL.FACIA_X - 20.0, BL.DRIVER_Y - 60.0, 40.0),
                         (BL.FACIA_X - 75.0, BL.DRIVER_Y - 60.0, -70.0)], True),   # down outboard of the column, under it
    ("fa.tach", "fa.earth.n", [(FX + 10.0, -250.0, BL.IP_Z - 60.0)], False),
    ("fa.speedo", "fa.speedo.n", [(FX, BL.INSTRUMENTS["speedometer"][0] - 36.0, BL.BINNACLE_Z - 10.0)], False),   # below and outboard of the speedometer cable
    # rear harness
    ("fa.R", "re.0", [(FX - 20.0, -610.0, 150.0)], True), ("re.0", "re.sill", [], True), ("re.sill", "re.pump", [], True),
    ("re.pump", "re.heel", [], True), ("re.heel", "re.arch", [(HEEL_X - 40.0, SILL_Y + 40.0, TONNEAU_RUN_Z),
                                                                           (U.SHELF_FRONT_X + 30.0, ARCH[0] - 20.0, TONNEAU_RUN_Z)], True),
    ("re.arch", "re.tank", [], True), ("re.tank", "re.boot", [], True), ("re.boot", "re.corner.R", [], True),
    ("re.corner.R", "re.M", [], True), ("re.M", "re.corner.L", [], True),
    ("re.pump", "pump.n", [(U.HEELBOARD_X + 10.0, -430.0, -345.0)], False), ("re.tank", "tank.n", [], False),
    ("re.corner.R", "rear.R.n", [], False), ("re.corner.L", "rear.L.n", [], False),
    ("re.M", "plate.R.n", [(RLX + 40.0, -120.0, BL.REAR_LAMP_Z - 120.0)], False),
    ("re.M", "plate.L.n", [(RLX + 40.0, 120.0, BL.REAR_LAMP_Z - 120.0)], False),
    ("re.boot", "boot.earth.n", [], False),
]

# ---- joints and connectors in the harness (D: positions; H: the joints Fig 10.26 draws) -----------------
# name -> (node it hangs off, offset from the node, kind, label). Wires end in a joint from the node's side.
JOINTS = {
    "b-connector": ("cb.n", (12.0, 4.0, -26.0), "snap", "Charging junction (snap connector at the control box)"),
    "ind-connector": ("cb.n", (-14.0, 4.0, -24.0), "bullet", "Warning lamp connector (at the control box)"),
    "g-joint-bay": ("fuse.n", (-14.0, 6.0, -26.0), "splice", "Green joint (fuse A4 supply, engine bay)"),
    "uw-joint": ("bay.corner.R", (18.0, 18.0, -22.0), "splice", "Blue/white joint (main beams)"),
    "ur-joint": ("bay.corner.R", (-18.0, 18.0, -22.0), "splice", "Blue/red joint (dipped beams)"),
    "r-joint-front": ("bay.corner.R", (0.0, 24.0, -26.0), "splice", "Red joint (side lamps)"),
    "p-joint": ("bay.front.M", (8.0, 18.0, -22.0), "splice", "Purple joint (horn feed)"),
    "pb-joint": ("bay.front.M", (8.0, -18.0, -22.0), "splice", "Purple/black joint (horn push)"),
    "w-joint": ("fa.ign", (-24.0, 6.0, -26.0), "splice", "White joint (ignition supply, behind the facia)"),
    "g-joint-facia": ("fa.heat", (-24.0, 0.0, -26.0), "splice", "Green joint (fused supply, behind the facia)"),
    "r-joint-facia": ("fa.light", (-24.0, 0.0, -26.0), "splice", "Red joint (side and tail lamps, behind the facia)"),
    "rw-joint": ("fa.tach", (-24.0, -14.0, -30.0), "splice", "Red/white joint (panel lamps)"),
    "lgp-joint": ("fa.drv", (-24.0, -20.0, -30.0), "splice", "Light green/purple joint (indicator warning lamps)"),
    "gr-joint": ("fa.drv", (-20.0, 22.0, -26.0), "splice", "Green/red joint (left-hand flashers)"),
    "gw-joint": ("fa.drv", (-20.0, -22.0, -26.0), "splice", "Green/white joint (right-hand flashers)"),
    "r-joint-rear": ("re.corner.R", (-10.0, 20.0, -22.0), "splice", "Red joint (tail and number plate lamps, boot)"),
    "gp-joint-rear": ("re.corner.R", (-10.0, -2.0, -26.0), "splice", "Green/purple joint (stop lamps, boot)"),
    "heater-connector": ("heater.n", None, "bullet", "Heater blower motor connector"),
    "map-connector": ("fa.map", None, "bullet", "Map lamp connector"),
}
JOINT_AT = {"heater-connector": BL.HEATER_CONNECTOR, "map-connector": BL.MAP_LAMP_CONNECTOR}

# which node each component terminal hangs off (by key prefix; first match wins)
TERM_NODE = [
    ("alt.", "eng.alt"), ("sol.", "sol.n"), ("starter.", "sol.n"), ("coil.SW", "eng.dist"), ("coil.", "eng.coil"), ("dist.", "eng.dist"),
    ("fuse.", "fuse.n"), ("flasher.", "fl.n"), ("relay.", "relay.n"), ("vac.", "vac.n"), ("horn.L", "horn.L.n"),
    ("horn.R", "horn.R.n"), ("stop.", "stop.n"), ("iso.", "iso.n"), ("odsol.", "odsol.n"),
    ("hl.R", "hl.R.n"), ("hl.L", "hl.L.n"), ("side.R", "side.R.n"), ("side.L", "side.L.n"),
    ("rear.R", "rear.R.n"), ("rear.L", "rear.L.n"), ("plate.R", "plate.R.n"), ("plate.L", "plate.L.n"),
    ("sw.lighting", "fa.light"), ("sw.wiper", "fa.light"), ("sw.heater", "fa.heat"), ("sw.panel-lamp", "fa.panel"),
    ("sw.map-lamp", "fa.map"), ("sw.overdrive", "fa.R"), ("ign.", "fa.ign"),
    ("speedometer.", "fa.speedo.n"), ("tachometer.", "fa.tach"), ("fuel-gauge.", "fa.fuel"), ("dual-gauge.", "fa.dual"),
    ("wiper.", "wiper.n"), ("dip.", "dip.n"), ("ind.horn", "col.top"), ("hornpush.", "col.top"), ("ind.", "col.n"), ("stab.", "fa.earth.n"),
    ("pump.", "pump.n"), ("tank.", "tank.n"),
    ("earth.headlamp-right", "hl.R.n"), ("earth.headlamp-left", "hl.L.n"), ("earth.relay", "relay.n"),
    ("earth.facia", "fa.earth.n"), ("earth.scuttle", "wiper.n"), ("earth.boot", "boot.earth.n"), ("earth.fuel-pump", "pump.n"),
]


def term_node(key):
    if key.startswith("joint."):
        return JOINTS[key[6:]][0]
    for pre, node in TERM_NODE:
        if key.startswith(pre):
            return node
    raise KeyError(f"no harness node for terminal {key}")


# ---- parts P10b adds: their datums and terminals ---------------------------------------------------------
STAB_SIZE = (38.0, 26.0, 20.0)                                 # can: length (y), height (z), depth (x) (D: Smiths BHA4637 photos)
EYE_SCREW = 10                                                 # No 10 self-tapping earth screws


def joint_point(name):
    node, off, kind, label = JOINTS[name]
    if off is None:
        return JOINT_AT[name]
    return _add(NODES[node], off)


def joint_axis(name):
    """Unit vector from the joint toward its harness node (the side every wire enters by)."""
    node = JOINTS[name][0]
    return _unit(_sub(NODES[node], joint_point(name)))


JOINT_LEN = {"splice": 16.0, "snap": 30.0, "bullet": 26.0}


def terminals():
    """Terminals of the parts P10b adds: the dip switch, the column switch, the voltage stabiliser,
    the fuel pump and tank unit leads, the earth points and the harness joints and connectors."""
    T = {}

    def t(key, part, name, p, d, kind, label, **kw):
        T[key] = dict(key=key, part=part, name=name, p=tuple(float(c) for c in p), d=_unit(d), kind=kind, label=label, **kw)

    # dip switch: three Lucar blades out of the back of the base, pointing down the toe board
    for name, dy in (("feed", -9.0), ("main", 0.0), ("dip", 9.0)):
        p = _add(_add(DIP_SWITCH, DIP_N, 9.0), (0.0, dy, 0.0))
        p = _add(p, DIP_U, 22.0)
        t("dip." + name, "electrical.wiring-lighting.dip-switch", {"feed": "feed (U)", "main": "main (UW)", "dip": "dip (UR)"}[name],
          p, DIP_U, "lucar", "Headlamp dip switch", normal=DIP_N)
    # direction indicator switch on the column: a row of Lucar blades out of its lower face; the horn push
    # lead leaves its top for the push in the wheel (P9 chassis.steering.horn-push)
    names = ["LGN", "GR", "GW", "LGY", "LGW", "B", "PB"]
    for k, name in enumerate(names):
        dy = (k - (len(names) - 1) / 2) * 7.5
        p = _add(_add(_add(COLUMN_SWITCH, COL_X, dy), COL_Y, 26.0), COL_AXIS, -10.0)
        t("ind." + name, "electrical.wiring-indicators.indicator-switch", {"PB": "horn push (PB)", "B": "warning lamp earth (B)"}.get(name, name),
          p, COL_Y, "lucar", "Direction indicator switch", normal=COL_AXIS)
    t("ind.horn", "electrical.wiring-indicators.indicator-switch", "horn push contact",
      _add(_add(COLUMN_SWITCH, COL_Y, -22.0), COL_AXIS, 22.0), COL_AXIS, "plug", "Direction indicator switch")
    hub = _add(SL.WHEEL_CENTRE, COL_AXIS, -40.0)
    t("hornpush.lead", "chassis.steering.horn-push", "contact", _add(hub, COL_Y, -(SL.OUTER_TUBE_R + 5.0)), _neg(COL_AXIS), "plug",
      "Horn push (steering wheel)")
    # voltage stabiliser: B, I and E blades along its bottom edge
    sx, sy, sz = BL.STABILISER
    for name, dy in (("B", -11.0), ("I", 0.0), ("E", 11.0)):
        t("stab." + name, "electrical.wiring-instruments.stabiliser", name, (sx + STAB_SIZE[2] / 2, sy + dy, sz - STAB_SIZE[1] / 2),
          (0.0, 0.0, -1.0), "lucar", "Voltage stabiliser", normal=(1.0, 0.0, 0.0))
    # fuel pump (P11a, SU HP, frame as assemblies/fuel_pump.py: local z out along -y, local y up): the
    # terminal stud on the end cover (Fig 3.3 items 29-32); the earth lead from a screw low on the coil housing
    p = (FS.PUMP_X, FS.PUMP_Y0 - FS.COVER_S[1] - 10.0, FS.PUMP_Z - 10.0)
    t("pump.feed", "fuel.pump.end-cover", "terminal stud", p, (0.0, -1.0, 0.0), "pin", "Fuel pump (SU)")
    ep = FS.pump_pt(FS.COVER_S[0] + 16.0, dz=-31.0)
    t("pump.earth", "fuel.pump.end-cover", "earth terminal", ep, (0.0, -0.5, -1.0), "pin", "Fuel pump (SU)")
    # tank gauge unit (P11a, frame as assemblies/fuel_tank.py): two blades out of its housing, outboard
    face = FS.TANK_Y[0] - 0.5 - 3.0 - 1.5
    for name, dx in (("T", -8.0), ("E", 8.0)):
        t("tank." + name, "fuel.tank.gauge-unit", {"T": "terminal", "E": "earth terminal"}[name],
          (FS.SENDER[0] + dx, face - 19.6, FS.SENDER[1]), (0.0, -1.0, 0.0), "lucar", "Fuel tank gauge unit", normal=(1.0, 0.0, 0.0))
    # earth points: eyelets under a self-tapping screw head
    for name, (p, n) in earth_points().items():
        to = _sub(NODES[term_node("earth." + name)], p)
        to = _add(to, n, -_dot(to, n))
        t("earth." + name, "electrical.wiring-earths.earth-" + name, "earth screw", p, to if _dot(to, to) > 1.0 else _perp(n), "eye",
          "Earth point (" + name.replace("-", " ") + ")", axis=n, eye_r=2.6)
    # joints and connectors
    for name, (node, off, kind, label) in JOINTS.items():
        a = joint_axis(name)
        circuit = JOINT_ASSEMBLY[name]
        t("joint." + name, f"electrical.{circuit}.{name}", "", _add(joint_point(name), a, JOINT_LEN[kind] / 2), a, "joint", label)
    return T


def earth_points():
    pts = dict(BL.EARTH_POINTS)
    # fuel pump earth: on the heelboard's rear face outboard of the pump (P11a)
    pts["fuel-pump"] = ((U.HEELBOARD_X, FS.PUMP_Y0 - FS.COVER_S[1] - 45.0, FS.PUMP_Z - 38.0), (-1.0, 0.0, 0.0))
    return pts


JOINT_ASSEMBLY = {
    "b-connector": "wiring-charging", "ind-connector": "wiring-charging", "g-joint-bay": "wiring-starting",
    "uw-joint": "wiring-lighting", "ur-joint": "wiring-lighting", "r-joint-front": "wiring-lighting", "p-joint": "wiring-wipers-horn",
    "pb-joint": "wiring-wipers-horn", "w-joint": "wiring-starting", "g-joint-facia": "wiring-starting", "r-joint-facia": "wiring-lighting",
    "rw-joint": "wiring-lighting", "lgp-joint": "wiring-indicators", "gr-joint": "wiring-indicators", "gw-joint": "wiring-indicators",
    "r-joint-rear": "wiring-lighting", "gp-joint-rear": "wiring-indicators", "heater-connector": "wiring-wipers-horn",
    "map-connector": "wiring-lighting",
}


# ---- routing ------------------------------------------------------------------------------------------
def _edge_pts(a, b, mid):
    return [NODES[a]] + [tuple(m) for m in mid] + [NODES[b]]


def _graph():
    g = {}
    for a, b, mid, _ in EDGES:
        pts = _edge_pts(a, b, mid)
        L = sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
        g.setdefault(a, []).append((b, L, (a, b)))
        g.setdefault(b, []).append((a, L, (a, b)))
    return g


def shortest(a, b):
    """Node path from a to b through the harness graph."""
    if a == b:
        return [a]
    g = _graph()
    dist, prev, q = {a: 0.0}, {}, [(0.0, a)]
    while q:
        d, n = heapq.heappop(q)
        if n == b:
            break
        if d > dist.get(n, 1e18):
            continue
        for m, L, _ in g.get(n, []):
            nd = d + L
            if nd < dist.get(m, 1e18):
                dist[m], prev[m] = nd, n
                heapq.heappush(q, (nd, m))
    if b not in dist:
        raise ValueError(f"no harness path {a} -> {b}")
    path = [b]
    while path[-1] != a:
        path.append(prev[path[-1]])
    return path[::-1]


def all_specs():
    out = []
    for f in sorted((ROOT / "specs" / "electrical").glob("wiring-*.yaml")):
        out += S.load_file(f)
    return out


def wire_specs():
    out = []
    for f in sorted((ROOT / "specs" / "electrical").glob("wiring-*.yaml")):
        for sp in S.load_file(f):
            if sp.data.get("route"):
                out.append(sp)
    return out


def od_of(sp):
    r = sp.data["route"]
    if r.get("od"):
        return float(r["od"])
    return CABLE_OD[sp.data["wire"]["size"]]


def _frames(pts):
    """Parallel-transport frames (t, n, b) at each vertex of a polyline."""
    ts = []
    for k in range(len(pts)):
        if k == 0:
            t = _unit(_sub(pts[1], pts[0]))
        elif k == len(pts) - 1:
            t = _unit(_sub(pts[-1], pts[-2]))
        else:
            t = _unit(_add(_unit(_sub(pts[k], pts[k - 1])), _unit(_sub(pts[k + 1], pts[k]))))
        ts.append(t)
    n = _perp(ts[0])
    out = []
    for t in ts:
        n = _unit(_add(n, t, -_dot(n, t)))
        out.append((t, n, _cross(t, n)))
    return out


def _slots(count, pitch):
    """Offsets (u, v) of `count` cables packed round a centre: centre, then hexagonal rings."""
    out = [(0.0, 0.0)]
    ring = 1
    while len(out) < count:
        r = ring * pitch
        m = 6 * ring
        for k in range(m):
            a = 2 * math.pi * k / m + (ring % 2) * math.pi / m
            out.append((r * math.cos(a), r * math.sin(a)))
        ring += 1
    return out[:count]


@lru_cache(maxsize=1)
def layout():
    """Route every wire. Returns {'wires': {id: dict(points, od, ...)}, 'edges': {(a,b): dict(points, radius, count)}}."""
    from mgb import electrical_layout as E
    T = E.terminals()
    specs = wire_specs()
    routes, users = {}, {}
    for k, sp in enumerate(specs):
        r = sp.data["route"]
        ta, tb = T[r["from"]], T[r["to"]]
        na, nb = term_node(r["from"]), term_node(r["to"])
        path = shortest(na, nb)
        edges = []
        for p, q in zip(path, path[1:]):
            key = (p, q) if any(e[0] == p and e[1] == q for e in EDGES) else (q, p)
            edges.append((key, key[0] == p))
            users.setdefault(key, []).append(sp.id)
        routes[sp.id] = (k, sp, ta, tb, path, edges)
    # bundle slots on each harness path
    epts = {(a, b): _edge_pts(a, b, mid) for a, b, mid, _ in EDGES}
    edata = {}
    for key, ids in users.items():
        ids = sorted(ids, key=lambda i: routes[i][0])
        pitch = max(od_of(routes[i][1]) for i in ids) + 0.25
        sl = _slots(len(ids), pitch)
        rad = max(math.hypot(*s) for s in sl) + pitch / 2
        edata[key] = dict(points=epts[key], frames=_frames(epts[key]), slot={i: s for i, s in zip(ids, sl)}, radius=rad,
                          count=len(ids), sleeved=next(e[3] for e in EDGES if (e[0], e[1]) == key))
    # terminals shared by several wires: spread the fittings
    share = {}
    for wid, (k, sp, ta, tb, path, edges) in routes.items():
        for end, tt in (("from", ta), ("to", tb)):
            share.setdefault(tt["key"], []).append((wid, end))
    wires = {}
    for wid, (k, sp, ta, tb, path, edges) in routes.items():
        od = od_of(sp)
        pts = []
        ends = {}
        for end, tt in (("from", ta), ("to", tb)):
            lst = share[tt["key"]]
            idx = lst.index((wid, end))
            ends[end] = end_geometry(tt, od, idx, len(lst))
        pts += ends["from"]["path"]
        for key, fwd in edges:
            e = edata[key]
            u, v = e["slot"][wid]
            seq = list(zip(e["points"], e["frames"]))
            if not fwd:
                seq = seq[::-1]
            for p, (t, n, b) in seq:
                pts.append(_add(_add(p, n, u), b, v))
        pts += ends["to"]["path"][::-1]
        wires[wid] = dict(points=_clean(pts), od=od, ends=ends, spec=sp, path=path)
    return dict(wires=wires, edges=edata)


def end_geometry(tt, od, idx, n):
    """Where the cable leaves a terminal: the fitting (if any) and the first points of the path,
    from the terminal outward. Several wires on one terminal stack side by side."""
    p, d, kind = tt["p"], tt["d"], tt["kind"]
    nrm = tt.get("normal") or _perp(d)
    side = _unit(_cross(d, nrm))
    off = (idx - (n - 1) / 2)
    if kind == "lucar":
        p0 = _add(p, nrm, off * (LUCAR_SLEEVE[2] + 0.4))
        tail = _add(p0, d, LUCAR_SLEEVE[0])
    elif kind == "pin":
        p0 = _add(p, side, off * (2 * PIN_SLEEVE[1] + 0.4))
        tail = _add(p0, d, PIN_SLEEVE[0])
    elif kind == "eye":
        ax = tt.get("axis", nrm)
        d = _unit(_add(d, ax, -_dot(d, ax)))       # the eye lies flat on its seat: tongue and barrel in its plane
        p0 = _add(p, ax, off * 1.3)
        tail = _add(p0, d, tt.get("eye_r", 3.0) + EYE_OUT + 9.0)
    elif kind == "joint":
        a = d
        q = _perp(a)
        r = _cross(a, q)
        ang = 2 * math.pi * idx / max(n, 1)
        rr = 0.0 if n == 1 else min(2.6, 0.9 * od)
        p0 = _add(_add(p, q, rr * math.cos(ang)), r, rr * math.sin(ang))
        tail = _add(p0, a, -6.0)          # start inside the joint sleeve
        return dict(p=p0, d=d, kind=kind, path=[tail, _add(p0, d, 2.0), _add(p0, d, EXIT)])
    else:                                    # plug, grommet, bulb holder: the cable starts inside it
        p0 = _add(p, side, off * (od + 0.3))
        tail = _add(p0, d, -3.0)
        return dict(p=p0, d=d, kind=kind, path=[tail, _add(p0, d, EXIT)])
    return dict(p=p0, d=d, kind=kind, normal=nrm, axis=tt.get("axis"), eye_r=tt.get("eye_r", 3.0),
                path=[_add(tail, d, -1.0), _add(tail, d, EXIT)])


def share_count(key):
    """How many wire ends land on a terminal."""
    n = 0
    for sp in wire_specs():
        r = sp.data["route"]
        n += (r["from"] == key) + (r["to"] == key)
    return n


def _clean(pts, tol=0.4):
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > tol:
            out.append(p)
    return out


def smooth(pts, od):
    """Round each corner with an arc (radius from the cable size, limited by the segments) sampled
    every 15 deg, so the swept cable never folds back on itself."""
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[k], pts[k + 1]
        u, v = _sub(a, b), _sub(c, b)
        la, lc = math.sqrt(_dot(u, u)), math.sqrt(_dot(v, v))
        if la < 1e-6 or lc < 1e-6:
            continue
        u, v = _unit(u), _unit(v)
        cosang = max(-1.0, min(1.0, _dot(u, v)))
        ang = math.acos(cosang)                      # interior angle at b
        if ang > math.radians(176.0):
            out.append(b)
            continue
        if ang < 1e-3:                               # the route folds straight back: keep the corner point
            out.append(b)
            continue
        turn = math.pi - ang
        r = min(8.0 * od, 40.0)
        tlen = r / math.tan(ang / 2)
        lim = min(la, lc) * 0.48
        if tlen > lim:
            tlen = lim
            r = tlen * math.tan(ang / 2)
        p0, p1 = _add(b, u, tlen), _add(b, v, tlen)
        bis = _unit(_add(u, v))
        ctr = _add(b, bis, r / math.sin(ang / 2))
        n = max(2, int(math.ceil(math.degrees(turn) / 15.0)))
        e0, e1 = _unit(_sub(p0, ctr)), _unit(_sub(p1, ctr))
        for i in range(n + 1):
            s = i / n
            w0 = math.sin((1 - s) * turn) / math.sin(turn) if turn > 1e-6 else 1 - s
            w1 = math.sin(s * turn) / math.sin(turn) if turn > 1e-6 else s
            dvec = _unit(_add(_add((0, 0, 0), e0, w0), e1, w1))
            out.append(_add(ctr, dvec, r))
    out.append(pts[-1])
    return _clean(out, 0.3)
