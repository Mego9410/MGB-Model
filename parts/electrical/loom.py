"""Wiring loom: the main harness in the engine bay with its branches to every unit, the facia
harness behind the instruments and switches, the rear harness to the rear and number plate
lamps, and the overdrive leads. Haynes Fig 10.26 (wiring diagram, models up to 1967; key
printed p189), Sec 33, 42, 45; Ch 6 Sec 16.

Built in the car frame. The routes are derived (D): the main harness enters the engine bay
through the bulkhead grommet on the right (mgb.body_layout.HARNESS_GROMMET), runs forward along
the top of the right inner wing past the control box and fuse block, across the front panel
behind the grille to the left-hand lamps, with branches off it at the units; the facia harness
runs behind the facia; the rear harness runs back along the right sill inside the body to the
boot and across the rear panel. Bundles are drawn as sleeved round bundles taped at intervals,
the branches as thinner bundles or single leads.
"""
import math

from build123d import Compound, Location, Part

from mgb import body_layout as BL, electrical_layout as E, elec_shapes as X
from mgb.elec_shapes import label

WY = BL.INNER_WING_Y
RUN_Z = 118.0                                   # height of the run along the inner wing tops
RUN_Y = WY - 22.0                               # just inboard of the valance face


def _union(parts):
    out = None
    for p in parts:
        if p is None:
            continue
        out = p if out is None else out + p
    return out


def _bundle(trunk, d, branches, band_every=140.0):
    """Trunk bundle with taped bands, and branches [(points, d)] leaving it."""
    parts = [X.cable(trunk, d, 60.0)]
    bands = X.sleeve_bands(trunk, d, band_every, 9.0, 1.0)
    if bands is not None:
        parts.append(bands)
    for pts, bd in branches:
        parts.append(X.cable(pts, bd, 25.0))
    return _union(parts)


# ---- unit connection points ---------------------------------------------------------------------
def _cb_terms():
    x, y, z = BL.CONTROL_BOX
    return (x, y + 9.0, z - 41.0 - 10.0)


def _fuse_terms():
    x, y, z = BL.FUSE_BOX
    return (x, y + 9.0, z - 14.0)


def _flasher_terms():
    x, y, z = BL.FLASHER
    return (x, y + 20.0, z - 37.0)


def _horn_terms(k):
    x, y, z = BL.HORN_POS[k]
    return (x - 9.0, y, z + 51.0 + 34.0 + 6.0)


def _headlamp_back(s):
    return (BL.HEADLAMP_RIM_X - 140.0, s * BL.HEADLAMP_Y, BL.HEADLAMP_Z)


def _sidelamp_back(s):
    return (BL.SIDELAMP_X - 28.0, s * BL.SIDELAMP_Y, BL.SIDELAMP_Z)


def _alt_plug():
    return E.alt_local(-3.0, -60.0, E.COVER_Z[0] - 40.0)


def _sol_switch():
    cx, cy, cz = E.SOL_C
    return (cx, cy + 15.0, cz + E.SOL_LEN / 2 + 20.0)


def _coil_sw():
    x, y = E.COIL_TERMINALS["SW"]
    return (x, y, E.COIL_TERMINAL_Z + 1.0)


def engine_bay(spec) -> Part:
    """Main harness in the engine bay (Fig 10.26): bulkhead grommet, along the right inner
    wing past the fuse block, flasher and control box, across the front panel to the left-hand
    lamps; branches to the control box, fuse block, flasher, solenoid, alternator, coil, both
    horns, both headlamps and side/flasher lamps, the overdrive relay and vacuum switch."""
    d = spec.nom("diameter")
    gx, gy, gz = BL.HARNESS_GROMMET
    front_x = BL.HORN_PANEL_X - 30.0
    cross_z = -40.0
    trunk = [(gx + 1.0, gy, gz), (gx + 10.0, gy, gz), (gx + 60.0, -RUN_Y, RUN_Z), (BL.INNER_WING_X[1] - 20.0, -RUN_Y, RUN_Z),
             (front_x - 60.0, -RUN_Y + 40.0, 40.0), (front_x, -RUN_Y + 120.0, cross_z), (front_x, RUN_Y - 120.0, cross_z),
             (front_x - 60.0, RUN_Y - 40.0, 40.0), (BL.INNER_WING_X[1] - 60.0, RUN_Y, RUN_Z - 10.0), (BL.OD_RELAY[0], RUN_Y, RUN_Z - 10.0),
             (BL.BULKHEAD_X + 40.0, RUN_Y - 60.0, 80.0), (BL.BULKHEAD_X + 14.0, BL.OD_VACUUM_SWITCH[1] + 30.0, BL.OD_VACUUM_SWITCH[2] + 10.0)]
    br = []
    for (tx, ty, tz), dd, depth in ((_fuse_terms(), 7.0, 21.0), (_flasher_terms(), 4.5, 40.0), (_cb_terms(), 8.0, 54.0)):
        fy = -WY + depth + 12.0                                     # down in front of the unit, then under it to the terminals
        br.append(([(tx, -RUN_Y, RUN_Z), (tx + 30.0, fy, RUN_Z - 30.0), (tx + 30.0, fy, tz - 22.0), (tx, ty + 2.0, tz - 22.0),
                    (tx, ty + 2.0, tz - 10.0)], dd))
    sx, sy, sz = _sol_switch()
    br.append(([(sx - 30.0, -RUN_Y, RUN_Z), (sx, sy + 30.0, sz + 40.0), (sx, sy, sz + 2.0)], 3.2))
    ax, ay, az = _alt_plug()
    cx, cy, cz = _coil_sw()
    eng = (-60.0, -RUN_Y, RUN_Z)
    br.append(([eng, (-20.0, -300.0, 60.0), (ax, ay - 10.0, az + 50.0), (ax, ay, az + 6.0)], 6.0))
    br.append(([(0.0, -300.0, 60.0), (cx - 40.0, cy - 60.0, cz + 6.0), (cx - 30.0, cy, E.COIL_TERMINAL_Z - 4.85),
                (cx - 4.0, cy, E.COIL_TERMINAL_Z - 4.85)], 3.2))
    for k, s in ((1, -1), (0, 1)):
        hx, hy, hz = _horn_terms(k)
        br.append(([(front_x, s * (RUN_Y - 140.0), cross_z), (hx - 20.0, hy, cross_z), (hx, hy, hz + 20.0), (hx, hy, hz)], 4.0))
        lx, ly, lz = _headlamp_back(s)
        px, py, pz = _sidelamp_back(s)
        br.append(([(front_x - 60.0, s * (RUN_Y - 40.0), 40.0), (lx - 30.0, s * (BL.HEADLAMP_Y - 60.0), lz - 30.0), (lx, ly, lz)], 6.0))
        br.append(([(lx - 30.0, s * (BL.HEADLAMP_Y - 60.0), lz - 30.0), (px - 40.0, s * (BL.SIDELAMP_Y - 50.0), pz), (px, py, pz)], 4.0))
    rx, ry, rz = BL.OD_RELAY
    br.append(([(rx, RUN_Y, RUN_Z - 10.0), (rx + 30.0, WY - 45.0, RUN_Z - 40.0), (rx + 30.0, WY - 45.0, rz - 45.0),
                (rx, ry - 15.0, rz - 45.0), (rx, ry - 15.0, rz - 36.0)], 4.5))
    return label(_bundle(trunk, d, br), spec)


def facia(spec) -> Part:
    """Facia harness: through the bulkhead grommet, along behind the facia to the instruments,
    warning lamps and switches, and over to the wiper motor."""
    d = spec.nom("diameter")
    gx, gy, gz = BL.HARNESS_GROMMET
    back = BL.FACIA_X + 122.0
    zr = BL.IP_Z + 25.0
    trunk = [(gx - 1.0, gy, gz), (gx - 60.0, gy, gz + 20.0), (back + 40.0, BL.DRIVER_Y - 220.0, zr), (back, BL.DRIVER_Y, zr),
             (back, 0.0, zr - 30.0), (back + 60.0, 300.0, 140.0), (BL.WIPER_MOTOR[0] - 10.0, BL.WIPER_MOTOR[1] + 60.0, BL.WIPER_MOTOR[2] - 140.0),
             (BL.WIPER_MOTOR[0] - 10.0, BL.WIPER_MOTOR[1] + 99.0, BL.WIPER_MOTOR[2] - 125.0),
             (BL.WIPER_MOTOR[0] - 10.0, BL.WIPER_MOTOR[1] + 99.0, BL.WIPER_MOTOR[2] - 106.0)]
    br = []
    for name, (y, z) in BL.INSTRUMENTS.items():
        depth = 72.0 if name in ("speedometer", "tachometer") else 50.0
        if name == "speedometer":
            continue
        br.append(([(back, y, zr if y < 0 else zr - 30.0), (BL.FACIA_X + depth + 30.0, y + 10.0, z + 30.0), (BL.FACIA_X + depth + 12.0, y + 6.0, z - 8.0)], 3.5))
    for name, (y, z) in BL.SWITCHES.items():
        zz = zr if y < 0 else zr - 30.0
        br.append(([(back, y, zz), (BL.FACIA_X + 70.0, y, z + 20.0), (BL.FACIA_X + 50.0, y, z)], 3.5))
    for name, (y, z) in BL.WARNING_LAMPS.items():
        br.append(([(back, y, zr), (BL.FACIA_X + 40.0, y, z + 4.0), (BL.FACIA_X + 31.0, y, z)], 2.5))
    return label(_bundle(trunk, d, br, 120.0), spec)


def rear(spec) -> Part:
    """Rear harness: from behind the facia down the right-hand side of the body inside the
    sill to the boot, across the rear panel to both rear lamps and number plate lamps."""
    d = spec.nom("diameter")
    sill_y = BL.HALF_W - 170.0
    floor_z = -350.0                                # along the inside of the sill, just above the cockpit floor
    arch_y, arch_z = 480.0, -90.0                   # inboard of and over the rear wheel arch, clear of the axle and springs
    rl_x = BL.REAR_LAMP_X + 30.0
    trunk = [(BL.FACIA_X + 100.0, BL.DRIVER_Y - 220.0, BL.IP_Z + 60.0), (BL.FACIA_X + 60.0, -sill_y, 0.0), (BL.FACIA_X - 80.0, -sill_y, floor_z),
             (-1500.0, -sill_y, floor_z), (-1640.0, -arch_y, arch_z), (BL.REAR_X + 400.0, -arch_y, arch_z), (rl_x + 60.0, -sill_y, BL.REAR_LAMP_Z - 80.0),
             (rl_x + 40.0, -BL.REAR_LAMP_Y + 40.0, BL.REAR_LAMP_Z - 120.0), (rl_x + 40.0, BL.REAR_LAMP_Y - 40.0, BL.REAR_LAMP_Z - 120.0),
             (rl_x + 10.0, BL.REAR_LAMP_Y, BL.REAR_LAMP_Z - 30.0)]
    br = [([(rl_x + 40.0, -BL.REAR_LAMP_Y + 40.0, BL.REAR_LAMP_Z - 120.0), (rl_x + 10.0, -BL.REAR_LAMP_Y, BL.REAR_LAMP_Z - 30.0)], 5.0)]
    nx, ny, nz = BL.NUMBER_LAMP
    for s in (-1, 1):
        br.append(([(rl_x + 40.0, s * 120.0, BL.REAR_LAMP_Z - 120.0), (nx + 40.0, s * (ny - 30.0), nz + 30.0), (nx + 6.0, s * (ny - 30.0), nz + 6.0)], 3.0))
    return label(_bundle(trunk, d, br, 180.0), spec)


def overdrive(spec) -> Part:
    """Overdrive leads (Ch 6 Sec 16; Fig 10.26 items 68, 71, 73): from the relay through the
    bulkhead, down the tunnel to the gearbox (isolation) switch on the remote control housing
    and on to the solenoid at the back of the overdrive's right side."""
    d = spec.nom("diameter")
    rx, ry, rz = BL.OD_RELAY
    iso = (-751.0, -26.0, -135.0)                 # terminals of the isolation switch (P5a remote housing)
    sol = (-906.0, -119.0, -269.0)                # lead leaves the back of the overdrive solenoid (P5b)
    pts = [(rx - 25.0, ry - 12.0, rz - 36.0), (rx - 40.0, ry - 30.0, rz - 90.0), (BL.BULKHEAD_X + 30.0, 215.0, -35.0), (BL.BULKHEAD_X - 30.0, 120.0, -120.0),
           (iso[0] + 100.0, -60.0, -110.0), (iso[0] + 10.0, iso[1] - 20.0, iso[2] + 10.0), (iso[0], iso[1] - 2.0, iso[2])]
    c = X.cable(pts, d, 40.0)
    c = c + X.cable([(iso[0] - 4.0, iso[1] - 20.0, iso[2] + 4.0), (iso[0] - 60.0, -90.0, -180.0), (sol[0] + 30.0, -150.0, sol[2] + 10.0),
                     (sol[0] - 16.0, sol[1] - 10.0, sol[2]), (sol[0] + 1.0, sol[1], sol[2])], d, 30.0)
    return label(c, spec)


PARTS = {
    "electrical.loom.engine-bay": {"build": engine_bay},
    "electrical.loom.facia": {"build": facia},
    "electrical.loom.rear": {"build": rear},
    "electrical.loom.overdrive": {"build": overdrive},
}
