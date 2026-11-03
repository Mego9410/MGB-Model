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
FAN_Z = (-29.0, -11.0)
DE_FACE_Z = -33.0                                    # drive end bracket front face
DE_Z = (-60.0, DE_FACE_Z)                            # drive end bracket
STATOR_Z = (-86.0, -60.0)                            # laminated stator ring between the brackets
SR_Z = (-136.0, -86.0)                               # slip ring end bracket
COVER_Z = (-166.0, -136.0)                           # moulded end cover
BODY_R = 63.0                                        # stator outside radius
BRACKET_R = 60.0

PIVOT = (-128.0, -66.0)                              # (y, z) of the two pivot bolts' common axis
LINK_LUG = (-160.0, -172.0)                          # (y, z) of the adjusting lug's tapped hole
LINK_STUD = (-93.0, -212.0)                          # (y, z) of the adjusting link stud in the engine front
FRONT_LUG_Z = (-43.0, DE_FACE_Z)                     # front pivot lug on the drive end bracket
REAR_LUG_Z = (-128.0, -116.0)                        # rear pivot lug on the slip ring end bracket
PUMP_EAR_X = (237.0, 247.0)                          # ear on the water pump flange carrying the front pivot
LINK_X = (BELT_X + DE_FACE_Z, BELT_X + DE_FACE_Z + 4.0)   # the link lies on the front face of the adjusting lug
REAR_BRACKET_BOSS = (124.0, -44.0)                   # (x, z) of the block's threaded boss, face at y -69 (P2 block)
BOSS_FACE_Y = B.YR - 7.0
REAR_EAR_X = (BELT_X + REAR_LUG_Z[0] - 8.0, BELT_X + REAR_LUG_Z[0] - 0.5)   # bracket ear behind the rear lug
FRONT_PLATE_NOTCH_R = 70.5                           # notch in the front plate's right wing round the body


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
YOKE_X = (REAR_PLATE_FRONT_X + FLANGE_T + 10.5, STARTER_FRONT_X - 22.0)   # the bolt heads sit on the flange ahead of it
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
TERMINAL_STACK = 16.6                                 # insulator, nut and washer on the post above the yoke: the cable eye's seat


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
COIL_AXIS = (40.0, BOSS_FACE_Y - 8.0 - 45.0)          # (x, y) of the vertical coil axis, clear of the block's bulge below the ledge
COIL_CAN = (-150.0, -22.0)                            # z of the can bottom and the top of the moulded cap seat
CAP_CENTRE = IG.to_engine((0.0, 0.0, IG.CAP_Z + IG.CAP_H))   # distributor cap centre tower (king lead)
_LT = (39.0 * math.cos(math.radians(120.0)), 39.0 * math.sin(math.radians(120.0)), IG.BODY_Z + 26.0)
DIST_LT = IG.to_engine(_LT)                           # distributor low tension terminal stud tip (P3 distributor body)
DIST_LT_OUT = IG.to_engine((52.0 * math.cos(math.radians(120.0)), 52.0 * math.sin(math.radians(120.0)), IG.BODY_Z + 26.0))
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
TEMP_BULB = (205.0, -66.0, 32.0)                       # gland nut on the head's right face, ahead of No 1 plug


# ---- terminals (P10b wiring) -------------------------------------------------------------------
# Every wire end and every terminal it lands on share these records, so the wiring (P10b) and the
# components (P10, P5, P8) agree. Each record: p = the terminal's root point (blade root, stud seat,
# entry of a moulded plug or bulb holder), d = the unit direction the wire leaves along, kind =
# 'lucar' (6.3 mm blade, female Lucar with an insulating sleeve over it), 'pin' (round pin or stud,
# a sleeved bullet-type female on it), 'eye' (ring terminal on a stud: axis = the stud axis), 'plug'
# (the wire enters a moulded plug, grommet or bulb holder directly), 'joint' (soldered joint or snap
# connector in the harness); part = the part id the terminal belongs to; name = the terminal marking.
# Positions follow the components' own geometry (their build code and assembly frames); the
# terminal markings are Haynes Fig 10.26 (printed p190) and Fig 6.19 (printed p131) unless noted.


def _xf(loc, p):
    from build123d import Location
    q = (loc * Location(tuple(float(c) for c in p))).position
    return (q.X, q.Y, q.Z)


def _xd(loc, d):
    a, b = _xf(loc, (0, 0, 0)), _xf(loc, d)
    v = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def _load(rel):
    import importlib.util
    sp = importlib.util.spec_from_file_location("_t_" + rel.replace("/", "_").replace(".", "_"), ROOT / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


_TERMS = None


def terminals():
    """{key: record} for every terminal the wiring lands on (cached)."""
    global _TERMS
    if _TERMS is not None:
        return _TERMS
    from build123d import Location, Rot
    from mgb import body_layout as BL, overdrive_layout as OL
    T = {}

    def t(key, part, name, p, d, kind="lucar", label="", **kw):
        n = math.sqrt(sum(c * c for c in d))
        T[key] = dict(key=key, part=part, name=name, p=tuple(float(c) for c in p), d=tuple(c / n for c in d), kind=kind,
                      label=label, **kw)

    def spec(f, pid):
        return {s.id: s for s in S.load_file(ROOT / "specs" / "electrical" / f)}[pid]

    # alternator plug (18ACR): the leads leave the moulded plug rearward (P10 terminal-plug)
    z0 = COVER_Z[0]
    for name, dx in (("+ (1)", -8.0), ("+ (2)", -3.0), ("IND", 2.0)):
        t("alt." + name.split()[0] + ("" if name == "IND" else name[-2]), "electrical.charging.terminal-plug", name,
          alt_local(dx, -34.0, z0 - 14.0), (-1.0, 0.0, 0.0), "plug", "18ACR alternator plug")
    # starter solenoid: battery and starter studs (eyes under the nuts), switch terminal pin on the cap
    bx, by, bz = sol_terminal(1)
    t("sol.BAT", "electrical.starting.solenoid", "BAT", (bx, by, bz - 3.5), (0.0, 1.0, 0.25), "eye", "Starter solenoid",
      axis=(0.0, 0.0, 1.0), eye_r=4.1)
    sx, sy, sz = sol_terminal(-1)
    t("sol.STA", "electrical.starting.solenoid", "STA", (sx, sy, sz - 10.5), (0.0, 1.0, 0.0), "eye", "Starter solenoid",
      axis=(0.0, 0.0, 1.0), eye_r=4.1)
    cx, cy, cz = SOL_C
    t("sol.SW", "electrical.starting.solenoid", "switch (WR)", (cx, cy + 15.0, cz + SOL_LEN / 2 + 11.0), (0.0, 0.0, 1.0), "pin",
      "Starter solenoid")
    t("starter.post", "electrical.starting.terminal-post", "terminal post", starter_terminal(),
      (0.0, math.cos(math.radians(TERMINAL_ANGLE)), math.sin(math.radians(TERMINAL_ANGLE))), "eye", "Starter motor")
    # coil: SW and CB studs (eyes under the brass nuts); negative earth: CB takes the ignition feed
    for name, (x, y) in COIL_TERMINALS.items():
        t("coil." + name, "electrical.coil.coil", name, (x, y, COIL_TERMINAL_Z - 5.7), (-1.0 if name == "SW" else 1.0, 0.0, 0.0), "eye",
          "Ignition coil",
          axis=(0.0, 0.0, 1.0), eye_r=2.2)
    # distributor low tension terminal blade (P3 distributor body), the lead pushed on along its length
    # the blade stands out radially toward the block, only a few mm from its face, so the lead's female is
    # drawn pushed on from the front, along the gap between the body and the block (as P10's lead ran)
    v = tuple(o - l for o, l in zip(DIST_LT_OUT, DIST_LT))
    ax = DIST_AXIS
    tg = (ax[1] * v[2] - ax[2] * v[1], ax[2] * v[0] - ax[0] * v[2], ax[0] * v[1] - ax[1] * v[0])
    tg = tg if tg[0] > 0 else tuple(-c for c in tg)
    tg = (tg[0], 0.0, tg[2])                       # level with the block face, not into it
    t("dist.LT", "ignition.distributor.body", "LT (CB)", DIST_LT, tg, "lucar", "Distributor", normal=v)

    # inner wing units (frames as assemblies/electrical_control.py)
    RIGHT = Rot(-90, 0, 0) * Rot(0, 0, 180)
    LEFT = Rot(90, 0, 0)
    BULK = Rot(0, 90, 0) * Rot(0, 0, 90)
    fb = Location(BL.FUSE_BOX) * RIGHT
    fw = spec("control.yaml", "electrical.control.fuse-block").nom("width")
    for name, sx_, yy in (("A1", -1, 13.0), ("A2", 1, 13.0), ("A3", -1, -13.0), ("A4", 1, -13.0)):
        t("fuse." + name, "electrical.control.fuse-block", name, _xf(fb, (sx_ * (fw / 2 + 0.5), yy, 3.5)), _xd(fb, (sx_, 0, 0)),
          "lucar", "Fuse block (4FJ)", normal=_xd(fb, (0, 0, 1)))
    fl = Location(BL.FLASHER) * RIGHT
    fsp = spec("control.yaml", "electrical.control.flasher")
    fr_, fL = fsp.nom("diameter") / 2, fsp.nom("length")
    for name, dx in (("B", -7.0), ("L", 0.0), ("P", 7.0)):
        t("flasher." + name, "electrical.control.flasher", name, _xf(fl, (dx, -fL / 2, fr_ + 3.0)), _xd(fl, (0, -1, 0)), "lucar",
          "Flasher unit (FL5)", normal=_xd(fl, (0, 0, 1)))
    rl = Location(BL.OD_RELAY) * LEFT
    rsp = spec("control.yaml", "electrical.control.relay")
    rw, rh, rd = rsp.nom("width"), rsp.nom("height"), rsp.nom("depth")
    for k, name in enumerate(("W1", "W2", "C1", "C2")):
        x = -rw / 2 + 7.0 + k * (rw - 14.0) / 3
        t("relay." + name, "electrical.control.relay", name, _xf(rl, (x, -rh / 2 - 1.5, rd / 2)), _xd(rl, (0, -1, 0)), "lucar",
          "Overdrive relay", normal=_xd(rl, (0, 0, 1)))
    vs = Location(BL.OD_VACUUM_SWITCH) * BULK
    vr = spec("control.yaml", "electrical.control.vacuum-switch").nom("diameter") / 2
    for name, dx in (("1", -6.0), ("2", 6.0)):
        t("vac." + name, "electrical.control.vacuum-switch", name, _xf(vs, (dx, -vr - 5.0, 12.0)), _xd(vs, (0, -1, 0)), "pin",
          "Overdrive throttle (vacuum) switch")
    hsp = spec("control.yaml", "electrical.control.horn")
    hr = hsp.nom("diameter") / 2
    for k, (hx, hy, hz) in enumerate(BL.HORN_POS):
        side = "L" if hy > 0 else "R"
        h = Location((hx, hy, hz + hr + 34.0)) * BULK
        for name, dx in (("1", -8.0 if hy > 0 else 8.0), ("2", 8.0 if hy > 0 else -8.0)):
            t(f"horn.{side}{name}", "electrical.control.horn", f"{'LH' if side == 'L' else 'RH'} horn {name}",
              _xf(h, (dx, 6.0, -3.0)), _xd(h, (0, 0, -1)), "pin", f"{'Left' if side == 'L' else 'Right'}-hand horn")

    # stop lamp switch on the four-way connection (P8): two spades on its moulded head
    lines = _load("parts/brakes/lines.py")
    p, d = lines.four_way_ports()["switch"]
    base = tuple(pp + dd * (lines.SWITCH_WASHER_T + 22.0) for pp, dd in zip(p, d))
    for name, k in (("1", -1), ("2", 1)):
        t("stop." + name, "brakes.lines.stop-switch", name, (base[0] + k * 4.0, base[1], base[2]), d, "lucar", "Stop lamp switch",
          normal=(1.0, 0.0, 0.0))
    # overdrive gearbox (isolation) switch on the remote housing (P5a) and the solenoid (P5b)
    rm = _load("parts/gearbox/remote.py")
    iso = G.GF * Location((rm.SU, rm.SW_L0, rm.SWITCH_D)) * Rot(-90, 0, 0)
    for name, dy in (("1", -4.5), ("2", 4.5)):
        t("iso." + name, "gearbox.remote.isolation-switch", name, _xf(iso, (0.0, dy, -20.0)), _xd(iso, (0, 0, -1)), "lucar",
          "Overdrive gearbox switch", normal=_xd(iso, (0, 1, 0)))
    su, sl = OL.SOL_AXIS
    sol = G.GF * Location((0, 0, OL.Z0)) * Location((su, sl, 0))
    t("odsol.T", "gearbox.overdrive-hydraulics.solenoid", "lead", _xf(sol, (-OL.SOL_R * 0.4, 0.0, OL.SOL_E[1] + 9.0)),
      (-0.35, -1.0, 0.25), "pin", "Overdrive solenoid")      # the lead bends outboard, clear of the speedometer angle drive

    # lamps (frames as assemblies/electrical_lamps.py)
    FRONT, REAR = Rot(0, 90, 0), Rot(0, -90, 0)
    hd = spec("lamps.yaml", "electrical.lamps.headlamp-bowl").nom("depth")
    for s, side in ((-1, "R"), (1, "L")):
        hl = Location((BL.HEADLAMP_RIM_X, s * BL.HEADLAMP_Y, BL.HEADLAMP_Z)) * FRONT
        for name, (dx, dy) in (("main", (-3.0, -3.0)), ("dip", (-3.0, 3.0)), ("earth", (3.0, 0.0))):
            t(f"hl.{side}.{name}", "electrical.lamps.headlamp-bowl", name, _xf(hl, (dx, dy, -14.0 - hd - 6.0)), _xd(hl, (0, 0, -1)),
              "plug", f"{'Right' if s < 0 else 'Left'}-hand headlamp")
        sl_ = Location((BL.SIDELAMP_X, s * BL.SIDELAMP_Y, BL.SIDELAMP_Z)) * FRONT * (Rot(0, 0, 180) if s < 0 else Rot(0, 0, 0))
        for name, dy in (("side", 18.0), ("flasher", -18.0)):          # clear side lamp outboard (local +y), flasher inboard
            t(f"side.{side}.{name}", "electrical.lamps.side-body", name, _xf(sl_, (0.0, dy, -9.0)), _xd(sl_, (0, 0, -1)), "plug",
              f"{'Right' if s < 0 else 'Left'}-hand side and flasher lamp")
        rl_ = Location((BL.REAR_LAMP_X, s * BL.REAR_LAMP_Y, BL.REAR_LAMP_Z)) * Rot(0, BL.REAR_LAMP_RAKE, 0) * REAR
        for name, (dx, dy) in (("tail", (-40.0, -3.0)), ("stop", (-40.0, 3.0)), ("flasher", (40.0, 0.0))):   # flasher on top
            t(f"rear.{side}.{name}", "electrical.lamps.rear-body", name, _xf(rl_, (dx, dy, -8.0)), _xd(rl_, (0, 0, -1)), "plug",
              f"{'Right' if s < 0 else 'Left'}-hand stop, tail and flasher lamp")
        nx, ny, nz = BL.NUMBER_LAMP
        t(f"plate.{side}", "electrical.lamps.plate-lamp", "feed", (nx, s * (ny + 1.0), nz), (0.0, s, 0.0), "plug",
          f"{'Right' if s < 0 else 'Left'}-hand number plate lamp")

    # facia (frame as assemblies/electrical_instruments.py: car = (FACIA_X - lz, y + ly, z + lx))
    def fa(y, z, lx, ly, lz):
        return (BL.FACIA_X - lz, y + ly, z + lx)
    for sw, names in (("lighting", ("4", "7", "8")), ("wiper", ("1", "4", "")), ("heater", ("1", "2", "")),
                      ("overdrive", ("1", "2", ""))):
        y, z = BL.SWITCHES[sw]
        for name, ly in zip(names, (-4.5, 0.0, 4.5)):
            if name:
                t(f"sw.{sw}.{name}", "electrical.instruments.toggle-switch", name, fa(y, z, 0.0, ly, -34.0), (1.0, 0.0, 0.0), "lucar",
                  {"lighting": "Lighting switch", "wiper": "Wiper switch", "heater": "Heater blower switch",
                   "overdrive": "Overdrive switch"}[sw], normal=(0.0, 1.0, 0.0))
    for sw in ("panel-lamp", "map-lamp"):
        y, z = BL.SWITCHES[sw]
        for name, ly in (("1", -4.0), ("2", 4.0)):
            t(f"sw.{sw}.{name}", "electrical.instruments.pull-switch", name, fa(y, z, 0.0, ly, -38.0), (1.0, 0.0, 0.0), "lucar",
              {"panel-lamp": "Panel lamp switch", "map-lamp": "Map lamp switch"}[sw], normal=(0.0, 1.0, 0.0))
    y, z = BL.SWITCHES["ignition"]
    for name, ly in (("1", -6.0), ("2", 0.0), ("3", 6.0)):
        t("ign." + name, "electrical.instruments.ignition-switch", name, fa(y, z, 0.0, ly, -40.0), (1.0, 0.0, 0.0), "lucar",
          "Ignition/starter switch", normal=(0.0, 1.0, 0.0))
    # instruments: bulb holders in the cases (panel lamp, warning lamps), tachometer pulse lead, fuel gauge studs
    for inst, (y, z) in BL.INSTRUMENTS.items():
        big = inst in ("speedometer", "tachometer")
        r, dep = (40.0 if big else 26.0), (72.0 if big else 50.0)
        name = {"speedometer": "Speedometer", "tachometer": "Tachometer", "fuel-gauge": "Fuel gauge",
                "dual-gauge": "Oil pressure and water temperature gauge"}[inst]
        holders = {"panel": BULB_HOLDERS["panel"]}
        if inst in ("tachometer", "speedometer"):
            holders["warning"] = BULB_HOLDERS["warning"]
            holders["arrow"] = BULB_HOLDERS["arrow"]
        for hname, a in holders.items():
            hx, hy = r - 8.0 if big else r - 7.0, 0.0
            hx, hy = (r - 8.0) * math.cos(math.radians(a)), (r - 8.0) * math.sin(math.radians(a))
            for k, wn in ((0, "feed"), (1, "return")):
                t(f"{inst}.{hname}.{wn}", f"electrical.instruments.{inst}-case", f"{hname} lamp {wn}",
                  fa(y, z, hx, hy + (k - 0.5) * 5.0, -dep - 18.0), (1.0, 0.0, 0.0), "plug", name)
        if inst == "tachometer":
            for wn, ly in (("in", -12.0), ("out", 24.0)):
                t(f"tachometer.pulse.{wn}", "electrical.instruments.tachometer-case", f"pulse lead {wn}",
                  fa(y, z, -6.0, ly, -dep - 6.0), (1.0, 0.0, 0.0), "pin", name)
        if inst == "fuel-gauge":
            for wn, ly in (("I", -8.0), ("T", 8.0)):
                t(f"fuel-gauge.{wn}", "electrical.instruments.fuel-gauge-case", wn, fa(y, z, 6.0, ly, -dep - 8.0),
                  (1.0, 0.0, 0.0), "pin", name)
    # wiper motor (DR3A): three Lucar blades on the front of the field yoke (P10 wipers)
    mx, my, mz = BL.WIPER_MOTOR
    for name, ly in (("1", 15.0), ("2", 29.0), ("E", 43.0)):
        t("wiper." + name, "electrical.wipers.motor", name, (mx - 10.0 + 30.0, my + 70.0 + ly, mz + 8.0 - 8.0 - 40.0), (1.0, 0.0, 0.0),
          "lucar", "Wiper motor (DR3A)", normal=(0.0, 0.0, 1.0))
    for key, rec in WIRING_TERMINALS().items():
        T[key] = rec
    _TERMS = T
    return T


# angles of the bulb holders round the instrument cases (deg from up toward the car's left, in the
# facia frame): the panel lamp (P10's upper holder), the warning lamp and the indicator arrow.
BULB_HOLDERS = {"panel": 135.0, "warning": 225.0, "arrow": 180.0}


def WIRING_TERMINALS():
    """Terminals of the parts P10b adds (dip switch, column switch, stabiliser, connectors, earth
    points, joints): defined with those parts in mgb.wiring_layout."""
    from mgb import wiring_layout as WL
    return WL.terminals()
