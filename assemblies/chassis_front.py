"""Front suspension: dampers, trunnions, swivel pins and axles, wishbones, springs and pans, steering levers
(Haynes Ch 11 Fig 11.2 items 8-14, 19-63; Secs 4, 5, 9, 14).

Car frame (mgb.front_suspension_layout). Parts drawn for the left-hand corner are built mirrored for the right
(build option side -1); round parts on the king pin are placed in the pin frame of each side. Explode stages
follow the Haynes order for stripping the crossmember assembly (Sec 4 para 1: springs, hubs, swivel axles and
pins, dampers, then the wishbones), each side outward:
  Sec 5 para 2    pan screws out; pan and spring lowered                         orders 20-21
  Sec 14 para 1   steering lever bolts; lever off                                 orders 22-23
                  fulcrum pin nut, pin out; outer pivot bolt out; swivel pin nut   orders 24-26
                  damper arm centre bolt; swivel axle and pin out of the arms      orders 27-28
                  trunnion and thrust washers off the pin; axle off the pin;
                  dust excluders, spring and cork ring                            orders 29-31
  Sec 9 para 1    damper bolts; damper lifted off                                  orders 32-33
  Sec 4 para 1    wishbone pivot bolts; arms off the pivots; nuts, washers, bushes  orders 34-36
"""
from build123d import Location, Rot

from mgb import fasteners as F, front_suspension_layout as L
from mgb.chassis_geom import IN
from parts.chassis import front as P

ID = "chassis.front"
NAME = "Front suspension"
PARENT = "chassis"
HAYNES = {"figures": [{"figure": "11.2"}, {"figure": "11.1"}], "section": 4}

UP, DOWN, FWD, BACK = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0]


def out(s):
    return [0, s, 0]


GROUPS = {}
for s, k in ((1, "l"), (-1, "r")):
    GROUPS[f"spring-{k}"] = {"axis": DOWN, "order": 21, "distance_mm": 260}
    GROUPS[f"swivel-{k}"] = {"axis": out(s), "order": 28, "distance_mm": 260}
    GROUPS[f"swivel-up-{k}"] = {"axis": UP, "order": 29, "distance_mm": 120}
    GROUPS[f"damper-{k}"] = {"axis": UP, "order": 33, "distance_mm": 200}
    GROUPS[f"arm-{k}"] = {"axis": DOWN, "order": 35, "distance_mm": 160}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "chassis.front." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def sided(s, extra=None):
    b = {} if s > 0 else {"side": -1}
    if extra:
        b.update(extra)
    return {"build": b} if b else {}


def P3(s, p):
    return (p[0], s * p[1], p[2])


def along_x(s, p, fwd=True):
    """Location of a fastener drawn along +z, at car point p (left-hand), pointing forward (+x) or back."""
    return Location(P3(s, p)) * Rot(0, 90 if fwd else -90, 0)


ID_ = Location()
NUT12 = F.NUT["1/2"]
for s, k in ((1, "l"), (-1, "r")):
    o = out(s)
    g_sw, g_up, g_d, g_arm = [f"swivel-{k}"], [f"swivel-{k}", f"swivel-up-{k}"], [f"damper-{k}"], [f"arm-{k}"]

    # ---- damper (8), bolts (9, 10), centre bolt ----------------------------------------------------------
    add("damper", ID_, groups=g_d, **sided(s))
    for x, y, z in L.DAMPER_BOLTS:
        add("damper-washer", Location((x, s * y, z + 12.0)), groups=g_d, explode=ex(UP, 32, 60))
        add("damper-bolt", Location((x, s * y, z + 12.0 + 1.6)) * Rot(180, 0, 0), groups=g_d, explode=ex(UP, 32, 110))
    cx, cy, cz = P.CENTRE_BOLT
    x0 = cx - L.DAMPER_ARM_X - 6.0
    add("damper-centre-bolt", along_x(s, (x0, cy, cz)), explode=ex(BACK, 27, 120))
    add("damper-centre-washer", along_x(s, (cx + L.DAMPER_ARM_X + 6.0, cy, cz)), explode=ex(FWD, 27, 60))
    add("damper-centre-nut", along_x(s, (cx + L.DAMPER_ARM_X + 7.3, cy, cz)), explode=ex(FWD, 27, 90))

    # ---- fulcrum pin (11), bearings (12), nut (13), washer, split pin ---------------------------------------
    fx, fy, fz = L.TOP_FULCRUM
    a0, a1 = fx - L.DAMPER_ARM_X - 6.0, fx + L.DAMPER_ARM_X + 6.0
    add("fulcrum-pin", along_x(s, (a0, fy, fz)), explode=ex(BACK, 25, 160))
    add("fulcrum-washer", along_x(s, (a1, fy, fz)), explode=ex(FWD, 24, 50))
    add("fulcrum-nut", along_x(s, (a1 + 2.0, fy, fz)), explode=ex(FWD, 24, 80))
    add("split-pin", Location(P3(s, (a0 + 4.0 * 25.4 - 4.0, fy, fz + 9.0))) * Rot(0, 90, 0), explode=ex(UP, 24, 60))
    for e in (1, -1):
        add("fulcrum-bearing", along_x(s, (fx + e * (L.DAMPER_ARM_X - 6.0), fy, fz), fwd=(e < 0)), groups=g_up,
            explode=ex([e, 0, 0], 30, 50))

    # ---- along the king pin --------------------------------------------------------------------------------
    def kf(h):
        return L.kp_frame(h, s)
    add("trunnion", ID_, groups=g_up, explode=ex(UP, 30, 70), **sided(s))
    add("pin-washer", kf(L.TRUNNION_TOP_H), groups=g_sw, explode=ex(UP, 26, 60))
    add("pin-nut", kf(L.TRUNNION_TOP_H + F.WASHER[L.PIN_THREAD][2] * IN), groups=g_sw, explode=ex(UP, 26, 90))
    add("split-pin", kf(L.PIN_TOP_H - 6.0) * Location((0, -9.0, 0)) * Rot(0, 0, 90), groups=g_sw, explode=ex(UP, 26, 120))
    add("floating-thrust-washer", kf(L.SWIVEL_H[1] + L.THRUST_T), groups=g_up, explode=ex(UP, 30, 40))
    add("thrust-washer", kf(L.SWIVEL_H[1]), groups=g_up, explode=ex(UP, 30, 25))
    add("swivel-axle-lh" if s > 0 else "swivel-axle-rh", ID_, groups=g_sw, explode=ex(UP, 31, 90))
    add("swivel-bush-upper", kf(L.SWIVEL_H[1] - L.BUSH_L), groups=g_sw, explode=ex(UP, 31, 90))
    add("swivel-bush-lower", kf(L.SWIVEL_H[0]), groups=g_sw, explode=ex(UP, 31, 90))
    add("dust-tube-upper", kf(L.DUST_UPPER_H[0]), groups=g_sw, explode=ex(UP, 31, 50))
    add("dust-spring", kf(L.DUST_LOWER_H[0] + 1.0), groups=g_sw, explode=ex(UP, 31, 35))
    add("dust-tube-lower", kf(L.DUST_LOWER_H[0]), groups=g_sw, explode=ex(UP, 31, 20))
    add("cork-ring", kf(L.PIN_BASE_TOP_H), groups=g_sw, explode=ex(UP, 31, 8))
    add("swivel-pin", ID_, groups=g_sw, **sided(s))
    ex_, ey_, ez_ = L.LOWER_PIVOT
    add("lubricator", Location(P3(s, (ex_ + 8.0, ey_, ez_ - 26.0))) * Rot(180, 0, 0), groups=g_sw)
    add("grub-screw", along_x(s, (ex_ - 14.0, ey_, ez_ + 17.0), fwd=True), groups=g_sw)
    from build123d import Vector
    p = L.kp(L.SWIVEL_H[1] - 14.0)
    add("lubricator", Location(P3(s, (p[0] + 30.0, p[1], p[2]))) * Rot(0, 90, 0), groups=g_sw)
    p = L.kp(L.SWIVEL_H[0] + 14.0)
    add("lubricator", Location(P3(s, (p[0], p[1] - 30.0, p[2]))) * Rot(90 * s, 0, 0), groups=g_sw)

    # ---- outer pivot bolt (30-32), distance tube (25), thrust washers (26), seals (27), supports (28) -----------
    h_out = L.WISHBONE_OUT_X + P.ARM_T / 2
    add("outer-pivot-bolt", along_x(s, (ex_ - h_out, ey_, ez_)), explode=ex(BACK, 26, 200))
    add("outer-pivot-washer", along_x(s, (ex_ + h_out, ey_, ez_)), explode=ex(FWD, 26, 60))
    add("outer-pivot-nut", along_x(s, (ex_ + h_out + 3.2, ey_, ez_)), explode=ex(FWD, 26, 90))
    add("distance-tube", along_x(s, (ex_ - 40.25, ey_, ez_)), groups=g_sw)
    for e in (1, -1):
        fwd = e > 0
        add("eye-thrust-washer", along_x(s, (ex_ + e * L.EYE_HALF, ey_, ez_), fwd=fwd), groups=g_sw, explode=ex([e, 0, 0], 30, 30))
        add("eye-seal", along_x(s, (ex_ + e * (L.EYE_HALF + 1.6), ey_, ez_), fwd=fwd), groups=g_sw, explode=ex([e, 0, 0], 30, 50))
        add("seal-support", along_x(s, (ex_ + e * 40.2, ey_, ez_), fwd=not fwd), groups=g_sw, explode=ex([e, 0, 0], 30, 70))

    # ---- steering lever (62), bolts (63) ---------------------------------------------------------------------
    lz = L.FZ + L.ARM_PAD_H - 12.0
    add("steering-lever", ID_, explode=ex(DOWN, 23, 80), **sided(s))
    for x in L.ARM_BOLT_X:
        add("lever-bolt", Location(P3(s, (x, 499.0, lz))), explode=ex(DOWN, 22, 120))

    # ---- spring (14), pan (19), screws (21, 22), nuts (23), washers (24) ----------------------------------------
    add("coil-spring", Location(P3(s, (L.SPRING_X, L.PAN_Y, L.PAN_SEAT_Z))), groups=[f"spring-{k}"],
        build={"length": round(L.SPRING_INSTALLED, 3)})
    add("pan", ID_, groups=[f"spring-{k}"], **sided(s))
    for fore in (1, -1):
        for yy in P.PAN_SCREW_Y:
            xa = L.arm_x(fore, yy)
            zz = L.wishbone_z(yy) + 4.0
            head = xa + fore * P.ARM_T / 2
            add("pan-screw", along_x(s, (head, yy, zz), fwd=fore < 0), explode=ex([fore, 0, 0], 20, 70))
            inner = xa - fore * (P.ARM_T / 2 + 2.5)
            add("pan-washer", along_x(s, (inner, yy, zz), fwd=fore < 0), explode=ex([-fore, 0, 0], 20, 30))
            add("pan-nut", along_x(s, (inner - fore * 1.6, yy, zz), fwd=fore < 0), explode=ex([-fore, 0, 0], 20, 50))

    # ---- wishbone arms (20), pivot (33-36), bushes (37), washers (38), nuts (39) ---------------------------------
    add("wishbone-arm", ID_, groups=g_arm, **sided(s, {"fore": 1}))
    add("wishbone-arm", ID_, groups=g_arm, **sided(s, {"fore": -1}))
    wx, wy, wz = L.WISHBONE_INNER
    add("wishbone-pivot", ID_, explode=ex(DOWN, 34, 60), **sided(s))
    for x in L.WISHBONE_PIVOT_BOLTS:
        add("pivot-bolt-34", Location(P3(s, (x, wy, wz - 11.0))), explode=ex(DOWN, 34, 120))
        add("pivot-washer-36", Location(P3(s, (x, wy, L.XM_BOTTOM_Z + L.XM_T))), explode=ex(UP, 34, 30))
        add("pivot-nut-35", Location(P3(s, (x, wy, L.XM_BOTTOM_Z + L.XM_T + 1.3))), explode=ex(UP, 34, 50))
    for fore in (1, -1):
        xa = wx + fore * L.WISHBONE_ARM_X
        face = xa + fore * 14.0
        add("pivot-bush", along_x(s, (face + fore * 2.5, wy, wz), fwd=fore < 0), groups=g_arm, explode=ex([fore, 0, 0], 36, 60))
        add("pivot-washer", along_x(s, (face + fore * 2.5, wy, wz), fwd=fore > 0), explode=ex([fore, 0, 0], 35, 60))
        add("pivot-nut", along_x(s, (face + fore * 5.0, wy, wz), fwd=fore > 0), explode=ex([fore, 0, 0], 35, 90))
INSTANCES = I
