"""Front disc brakes, Lockheed two-piston calipers on 10.75 in discs (Haynes Ch 9 Figs 9.6-9.8; Secs 8, 10-12).

Drawn in the left-hand front hub frame of mgb.front_suspension_layout; the right-hand wheel's handed parts
(caliper halves, dust cover, hose bracket) are mirror images, the hose a mirrored variant, and the parts that are
round about their own axis are placed square to the wheel on each side. The hub, swivel axle and the caliper
flange the caliper bolts pass through are P9's (`front_suspension_layout.HUB_FLANGE_*`, `CALIPER_*`).
Explode stages (each side outward), in the Haynes order:
  Sec 10 paras 2-3  the split pins out, the retaining clip off, the pads and shims out        orders 1-3
  Sec 8, Sec 11     the hose off the caliper and out of its bracket; the tab washer knocked
                    back and the two bolts out; the caliper off                               orders 4-6
  Sec 11 para 4     the disc bolts out and the disc off the hub; the dust cover off           orders 7-10
  Sec 12            the caliper dismantled: pistons, dust seals and retainers, fluid seals;
                    the bleed screw and plug                                                  orders 11-13
"""
from build123d import Location, Rot

from mgb import front_suspension_layout as L
from parts.brakes import front as P

ID = "brakes.front"
NAME = "Front disc brakes"
PARENT = "brakes"
HAYNES = {"figures": [{"figure": "9.7"}, {"figure": "9.8"}], "section": 11}

LEFT, RIGHT, FWD, BACK, UP, DOWN = [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]
GROUPS = {}
for k, ax in (("l", LEFT), ("r", RIGHT)):
    GROUPS[f"caliper-{k}"] = {"axis": BACK, "order": 6, "distance_mm": 180}
    GROUPS[f"disc-{k}"] = {"axis": ax, "order": 8, "distance_mm": 160}
    GROUPS[f"cover-{k}"] = {"axis": ax, "order": 10, "distance_mm": 90}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "brakes.front." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


DM = L.DISC_MID_Y
MOUTH = L.BORE_MOUTH
HALF_OUT = P.HALF_OUT
TOWARD_Y = Rot(-90, 0, 0)          # local +z along car +y, local x kept
AGAINST_Y = Rot(90, 0, 0)          # local +z along car -y, local x kept
FH = Location((L.FX, 0.0, L.FZ))
MIRROR_DM = Location((0, DM, 0)) * Rot(180, 0, 0) * Location((0, -DM, 0))   # inboard -> outboard (parts even in z)


def at(side, x, y, z, outward):
    """Car-frame location of a round part on one side: hub-frame point (x, |y|, z), local +z outward (or
    inward), local x kept along the car's x."""
    d = side * (1 if outward else -1)
    return Location(L.car(side, (x, y, z))) * (TOWARD_Y if d > 0 else AGAINST_Y)


def flip_x(x0):
    """Half turn about the vertical line at hub-frame x0, y 0 (for parts even about their own x-z plane)."""
    return Location((x0, 0, 0)) * Rot(0, 0, 180) * Location((-x0, 0, 0))


for s in (1, -1):
    k = "l" if s > 0 else "r"
    hand = "lh" if s > 0 else "rh"
    out = LEFT if s > 0 else RIGHT
    inn = RIGHT if s > 0 else LEFT
    F = FH if s > 0 else FH * Rot(180, 0, 0)          # for parts even in z (pads, clip, tab washer)
    G = [f"caliper-{k}"]
    cx = -L.PISTON_R_AT
    # ---- pads (Sec 10) ----------------------------------------------------------------------------------
    for v in (-L.PIN_V, L.PIN_V):
        add("pad-pin", at(s, -P.PIN_U, DM - HALF_OUT - 1.0, v, True), explode=ex(inn, 1, 160))
    add("pad-clip", F, explode=ex(UP, 2, 70))
    for side_m, d in ((Location((0, 0, 0)), inn), (MIRROR_DM, out)):
        add("pad", F * side_m, explode=ex(BACK, 3, 110))
        add("pad-lining", F * side_m, explode=ex(BACK, 3, 110))
        add("anti-squeal-shim", F * side_m, explode=ex(BACK, 3, 140))
    # ---- hose, bracket (Sec 8) ----------------------------------------------------------------------------
    HF = FH if s > 0 else FH * Rot(0, 0, 180) * flip_x(-(L.HOSE_BRACKET[0] - L.FX))
    add("hose", FH, build={"side": s}, explode=ex(UP, 4, 120))
    xi, zi = P.P(*L.INLET)
    add("hose-copper-washer", FH if s > 0 else FH * Rot(0, 0, 180) * flip_x(-xi), explode=ex(inn, 4, 40))
    add("hose-locknut", HF, explode=ex(UP, 3.9, 60))
    add("hose-lockwasher", HF, explode=ex(UP, 3.9, 40))
    add("locking-plate", HF, explode=ex(DOWN, 4, 50))
    add(f"hose-bracket-{hand}", FH)
    # ---- caliper fixings (Sec 11) -----------------------------------------------------------------------
    add("tab-washer", F, explode=ex(inn, 5, 50))
    ub = L.LUG_U[0] + 8.0
    tw = 0.9
    for v in (-L.LUG_V, L.LUG_V):
        add("caliper-bolt", at(s, -ub, L.CALIPER_MOUNT_FACE_Y - L.SWIVEL_CALIPER_FLANGE_T - tw, v, True),
            explode=ex(inn, 5, 90))
    # ---- caliper (Sec 12) -----------------------------------------------------------------------------
    add(f"caliper-mounting-half-{hand}", FH, groups=G)
    add(f"caliper-rim-half-{hand}", FH, groups=G, explode=ex(out, 13, 70))
    for v in (-P.BBV, P.BBV):
        add("bridge-bolt", at(s, -L.BRIDGE_BOLT_U, DM + HALF_OUT - 6.0, v, False), groups=G, explode=ex(out, 12.5, 140))
    tu, tv = P.TRANSFER
    add("bridge-seal", at(s, -tu, DM - 1.5, tv, True), groups=G, explode=ex(out, 13, 40))
    y_m = DM - MOUTH
    p_open = DM - L.PAD_FACE - L.PAD_LINING_T - L.PAD_BACK_T - L.SHIM_T
    for inboard in (True, False):
        o = inboard                                      # pistons face the disc: inboard ones point outward
        mirror = (lambda y: y) if inboard else (lambda y: 2 * DM - y)
        d = inn if inboard else out
        add("piston", at(s, cx, mirror(p_open - L.PISTON_L) if inboard else mirror(p_open - L.PISTON_L), 0.0, o),
            groups=G, explode=ex(d, 11, 90))
        add("dust-seal-retainer", at(s, cx, mirror(y_m - 5.4) if inboard else mirror(y_m - 5.4), 0.0, o),
            groups=G, explode=ex(d, 11.5, 150))
        add("dust-seal", at(s, cx, mirror(y_m - 5.0), 0.0, o), groups=G, explode=ex(d, 11.5, 130))
        add("fluid-seal", at(s, cx, mirror(y_m - P.SEAL_GROOVE[1] + 0.1), 0.0, o), groups=G, explode=ex(d, 12, 60))
    xb, zb = P.P(118.0, P.BV)
    zt = zb + 7.0
    add("bleed-screw", Location(L.car(s, (xb, L.BLEED_Y, zt))), groups=G, explode=ex(UP, 12, 40))
    add("bleed-cap", Location(L.car(s, (xb, L.BLEED_Y, zt))), groups=G, explode=ex(UP, 11.8, 70))
    add("plug", Location(L.car(s, (xb, L.PLUG_Y, zt))), groups=G, explode=ex(UP, 12, 40))
    # ---- disc and dust cover (Sec 11 para 4) ----------------------------------------------------------
    D = [f"disc-{k}"]
    p0 = L.DISC_FACE_Y - L.DISC_PLATE_T
    sw_t = 0.06 * 0.375 * 25.4 + 0.6
    for a in L.DISC_BOLT_ANGLES:
        x, z = L.ang(L.DISC_BOLT_PCD / 2, a)
        add("disc-bolt", at(s, x, p0, z, True), groups=D, explode=ex(inn, 9, 60))
        add("disc-spring-washer", at(s, x, L.HUB_FLANGE_Y[1], z, True), explode=ex(out, 7, 40))
        add("disc-nut", at(s, x, L.HUB_FLANGE_Y[1] + sw_t, z, True), explode=ex(out, 7, 70))
    add("disc", FH if s > 0 else FH * Rot(0, 0, 180), groups=D)
    sw5 = 0.06 * 0.3125 * 25.4 + 0.6
    for a in L.SHIELD_SCREW_ANGLES:
        x, z = L.ang(L.SHIELD_SCREW_R, a)
        yf = L.SHIELD_FACE_Y + L.SHIELD_T
        add("dust-cover-spring-washer", at(s, x, yf, z, True), groups=[f"cover-{k}"], explode=ex(out, 9.5, 30))
        add("dust-cover-screw", at(s, x, yf + sw5, z, False), groups=[f"cover-{k}"], explode=ex(out, 9.5, 60))
    add(f"dust-cover-{hand}", FH, groups=[f"cover-{k}"])
INSTANCES = I
