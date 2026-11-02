"""Brake pipes, connections and hoses outside the wheels (Haynes Ch 9 Fig 9.1 items 1, 3-12, printed p147; Sec 8
flexible hoses, Sec 9 metal pipes, p149).

Fig 9.1 (single line system): the pipe from the master cylinder's banjo to the four-way connection (5) on its
spacer (6), the hydraulic stop lamp switch (7) screwed into the connection, pipes from it to the two front hoses
(their ends held by locking plates, 4) and one to the rear hose, the rear hose to the three-way connection (9)
on the axle, and the two axle pipes from it to the wheel cylinders, held by clips (12). The front hoses and their
brackets are parts/brakes/front.py; the master cylinder's banjo parts/brakes/master.py.

Everything is built in the car frame (the axle parts from mgb.rear_axle_layout AF). Routes are derived
(mgb.brake_layout): P11 adds the clips, grommets and the body brackets' panels along them; P9 checks the front
pipes and hoses against the suspension and steering, and the axle pipes against the U-bolts.

Forms: pipes are 3/16 in tube with a 3/8 UNF tube nut at each end screwed into the female port it meets; the
connections are brass-coloured steel forgings with hex bosses round their ports; the stop lamp switch has a hex
body and a moulded head with two spade terminals; the rear hose is as the front ones (crimped ends, the top through
its bracket under a locknut and shakeproof washer, the bottom screwed into the three-way connection).
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot

from mgb import brake_layout as B, car_layout as CL, fasteners as F, front_suspension_layout as FL, \
    rear_axle_layout as A, shapes as Sh
from mgb.brake_parts import (IN, box, chamfered_hex, hexp, lab, mirror_y, ring, rod, spring_washer, tube_rod, xcyl,
                             ycyl, zc)
from parts.brakes import master as M

PIPE_OD = 0.1875 * IN
PIPE_ID = 0.125 * IN
NUT_AF, NUT_L = 0.4375 * IN, 10.0          # 3/8 UNF tube nut
BRK_T = 2.5


def tube_nut(p, d):
    """Tube nut whose seat face is at p, the hex running back along the pipe (direction d away from the port)."""
    n = chamfered_hex(NUT_AF, NUT_L) - zc(PIPE_OD / 2 + 0.3, -1, NUT_L + 1)
    n = n + zc(4.6, -6.0, 0.01) - zc(PIPE_OD / 2 + 0.3, -7, 1)          # thread into the port
    return Plane(origin=p, z_dir=d).location * n


def pipe(points, nut_ends=(True, True), radius=14.0):
    """Pipe along a filleted polyline with tube nuts at the ends (seat faces at the first and last points)."""
    pts = [tuple(map(float, p)) for p in points]
    t = tube_rod(pts, PIPE_OD / 2, PIPE_ID / 2, radius)
    for k, (on, a, b) in enumerate(((nut_ends[0], pts[0], pts[1]), (nut_ends[1], pts[-1], pts[-2]))):
        if on:
            d = [b[i] - a[i] for i in range(3)]
            t = t + tube_nut(a, d)
    return t


def af(p):
    return A.car(p)


def unit(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def along(p, d, s):
    return tuple(p[i] + d[i] * s for i in range(3))


# =================================================================================================
# four-way connection (5), its spacer (6), bolt and the stop lamp switch (7)
# =================================================================================================
FX4, FY4, FZ4 = B.FOUR_WAY
BX, BY, BZ = B.FOUR_WAY_BLOCK
X4 = (FX4 + B.FOUR_WAY_SPACER, FX4 + B.FOUR_WAY_SPACER + BX)        # block faces
XC4 = sum(X4) / 2


def four_way_ports():
    """name -> (port face point, outward direction)."""
    return {"inlet": ((XC4, FY4 - 10.0, FZ4 + BZ / 2 + 4.0), (0, 0, 1)),
            "switch": ((XC4, FY4 + 11.0, FZ4 + BZ / 2 + 4.0), (0, 0, 1)),
            "front-lh": ((XC4, FY4 + BY / 2 + 4.0, FZ4), (0, 1, 0)),
            "front-rh": ((XC4, FY4 - BY / 2 - 4.0, FZ4), (0, -1, 0)),
            "rear": ((XC4, FY4, FZ4 - BZ / 2 - 4.0), (0, 0, -1))}


def four_way(spec) -> Part:
    b = box(X4[0], X4[1], FY4 - BY / 2, FY4 + BY / 2, FZ4 - BZ / 2, FZ4 + BZ / 2)
    for name, (p, d) in four_way_ports().items():
        base = along(p, d, -4.0)
        boss = Plane(origin=base, z_dir=d).location * (chamfered_hex(14.0, 4.0) if name != "switch" else zc(8.0, 0, 4.0))
        b = b + boss
        b = b - Plane(origin=p, z_dir=d).location * zc(4.0, -12.0, 1.0)       # tapped 3/8 UNF port
        b = b - Plane(origin=p, z_dir=d).location * zc(1.2, -20.0, 0.0)
    b = b - xcyl(4.2, X4[0] - 1, X4[1] + 1, FY4, FZ4)                     # bolt hole through the middle
    return lab(b, spec)


def four_way_spacer(spec) -> Part:
    return lab(xcyl(8.0, FX4, FX4 + B.FOUR_WAY_SPACER, FY4, FZ4) - xcyl(4.2, FX4 - 1, X4[0] + 1, FY4, FZ4), spec)


def four_way_bolt(spec) -> Part:
    """5/16 UNF bolt from the front of the block through the spacer and the bulkhead (nut on the footwell side)."""
    sw = spring_washer("5/16")[1]
    return lab(Location((X4[1] + sw, FY4, FZ4)) * Rot(0, -90, 0) * F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def four_way_spring_washer(spec) -> Part:
    return lab(Location((X4[1], FY4, FZ4)) * Rot(0, 90, 0) * spring_washer("5/16")[0], spec)


def four_way_nut(spec) -> Part:
    """On the footwell side of a 1 mm bulkhead panel (P11)."""
    return lab(Location((CL.BULKHEAD_X - 1.0, FY4, FZ4)) * Rot(0, -90, 0) * F.hex_nut("5/16"), spec)


def stop_switch(spec) -> Part:
    """Hydraulic stop lamp switch: threaded stem into the connection, hex, moulded head with two spade terminals."""
    p, d = four_way_ports()["switch"]
    s = zc(4.6, -10.0, 0.01) + chamfered_hex(19.0, 8.0) + Sh.revolved([(0, 8.0), (10.5, 8.0), (10.5, 20.0), (9.5, 22.0), (0, 22.0)])
    for k in (-1, 1):
        s = s + box(k * 4.0 - 0.4, k * 4.0 + 0.4, -3.2, 3.2, 21.9, 31.0) - zc(1.0, 26, 32, k * 4.0, 0)
    s = s - Sh.revolved([(10.6, 14.0), (11.0, 14.0), (11.0, 15.0), (10.6, 15.0)])
    return lab(Plane(origin=p, z_dir=d).location * s, spec)


def switch_washer(spec) -> Part:
    p, d = four_way_ports()["switch"]
    t = spec.nom("thickness")
    return lab(Plane(origin=along(p, d, -t), z_dir=d).location * ring(4.8, 8.0, 0, t), spec)


# =================================================================================================
# pipes (car frame)
# =================================================================================================
def mc_pipe_points():
    """Fig 9.1 item 1: master cylinder banjo down through the box floor, back under the box outboard of the brake
    pedal, then down to the four-way connection's inlet."""
    s = M.stub_end()
    p, d = four_way_ports()["inlet"]
    zf = B.BOX_Z[0]
    yo = B.MC_Y - 16.0
    return [p, (p[0], p[1], p[2] + 22.0), (p[0] - 6.0, yo, zf - 36.0), (s[0] - 40.0, yo, zf - 30.0), (s[0], s[1], zf - 22.0), s]


def mc_pipe(spec) -> Part:
    pts = mc_pipe_points()
    return lab(pipe(pts, (True, False)), spec)


def _front_hose_top(side):
    hx, hy, hz = FL.HOSE_BRACKET
    return (hx, side * hy, hz + BRK_T + 14.0)


def front_pipe_points(side):
    """Four-way connection to a front hose: the right-hand one outboard to the chassis leg; the left-hand one up the
    bulkhead face, over the bellhousing and down to the left leg; then forward along the leg and up and out to the
    hose bracket on the wing valance."""
    p, d = four_way_ports()["front-lh" if side > 0 else "front-rh"]
    top = _front_hose_top(side)
    xb = CL.BULKHEAD_X + 6.0
    leg = side * B.CHASSIS_LEG_Y
    pts = [p, along(p, d, 14.0)]
    if side > 0:
        y_up = B.BOX_Y[1] + 10.0
        pts += [(xb, y_up, FZ4), (xb, y_up, B.HEAT_CROSS_Z), (xb, -y_up, B.HEAT_CROSS_Z), (xb, -y_up, B.LEG_PIPE_Z),
                (xb, leg, B.LEG_PIPE_Z)]
    else:
        pts += [(xb + 10.0, leg, B.LEG_PIPE_Z)]
    pts += [(-120.0, leg, B.LEG_PIPE_Z), (20.0, leg, -150.0), (top[0] - 10.0, side * (abs(top[1]) - 40.0), top[2] + 40.0),
            (top[0], top[1], top[2] + 30.0), top]
    return pts


def front_pipe(side):
    def build(spec) -> Part:
        return lab(pipe(front_pipe_points(side)), spec)
    return build


def _rear_hose_top():
    hx, hy, hz = B.REAR_HOSE_BRACKET
    return (hx, hy, hz + BRK_T + 14.0)


def rear_pipe_points():
    """Four-way connection down the toe board, back under the floor beside the tunnel, rising ahead of the axle to
    the rear hose bracket."""
    p, d = four_way_ports()["rear"]
    fy, fz = B.FLOOR_PIPE
    top = _rear_hose_top()
    return [p, along(p, d, 20.0), (p[0] - 30.0, fy, fz + 40.0), (p[0] - 90.0, fy, fz), (top[0] + 160.0, fy, fz),
            (top[0] + 60.0, top[1] - 20.0, top[2] + 40.0), (top[0], top[1], top[2] + 40.0), top]


def rear_pipe(spec) -> Part:
    return lab(pipe(rear_pipe_points()), spec)


# =================================================================================================
# rear hose, its bracket on the body, and the three-way connection (9) on the axle
# =================================================================================================
U0, U1, UZ0, UZ1 = B.UNION_BODY
UY = B.UNION_Y
UW = 34.0


def union_ports():
    """AF: name -> (port face point, outward direction)."""
    zm = (UZ0 + UZ1) / 2 + 2.0
    return {"hose": ((B.UNION_PORT_X, UY, UZ1 + 3.0), (0, 0, 1)),
            "lh": ((B.UNION_PORT_X, UY + UW / 2 + 3.0, zm), (0, 1, 0)),
            "rh": ((B.UNION_PORT_X, UY - UW / 2 - 3.0, zm), (0, -1, 0))}


def union(spec) -> Part:
    """Three-way connection: body on the axle tab, ear with the bolt hole over the tab's tapped hole, hex bosses
    round the hose port (top) and the two pipe ports (sides)."""
    b = box(U0, U1, UY - UW / 2, UY + UW / 2, UZ0, UZ1)
    ex_ = B.UNION_EAR_X
    b = b + box(U1 - 0.01, ex_ + 8.0, UY - 8.0, UY + 8.0, UZ0, UZ0 + 8.0) + zc(8.0, UZ0, UZ0 + 8.0, ex_, UY)
    for name, (p, d) in union_ports().items():
        b = b + Plane(origin=along(p, d, -3.0), z_dir=d).location * chamfered_hex(14.0, 3.0)
        b = b - Plane(origin=p, z_dir=d).location * zc(4.0, -11.0, 1.0)
        b = b - Plane(origin=p, z_dir=d).location * zc(1.2, -18.0, 0.0)
    b = b - zc(3.3, UZ0 - 1, UZ0 + 9, ex_, UY)
    return lab(A.AF * b, spec)


def union_bolt(spec) -> Part:
    sw = spring_washer("1/4")[1]
    return lab(A.AF * Location((B.UNION_EAR_X, UY, UZ0 + 8.0 + sw)) * Rot(180, 0, 0) * F.hex_bolt("1/4", spec.nom("length") / IN), spec)


def union_spring_washer(spec) -> Part:
    return lab(A.AF * Location((B.UNION_EAR_X, UY, UZ0 + 8.0)) * spring_washer("1/4")[0], spec)


def _rear_bracket_xyz():
    return B.REAR_HOSE_BRACKET


def rear_hose(spec) -> Part:
    """Rear flexible hose: the top end through the body bracket (hex below, threaded neck up through it, female
    for the rear pipe's nut), down and back in a loop to its male end screwed into the three-way connection."""
    hx, hy, hz = _rear_bracket_xyz()
    r = spec.nom("outside_diameter") / 2
    p, d = union_ports()["hose"]
    q = A.car(p)
    top = zc(6.2, hz - 46.0, hz - 21.0, hx, hy) + chamfered_hex(15.9, 13.0, hz - 21.0).moved(Location((hx, hy, 0))) + \
        zc(5.5, hz - 8.01, hz + BRK_T + 14.0, hx, hy)
    top = top - zc(2.6, hz - 10.0, hz + BRK_T + 15.0, hx, hy)
    bot = zc(4.6, q[2] - 10.0, q[2] + 1.2, q[0], q[1]) + chamfered_hex(14.3, 11.0, q[2] + 1.2).moved(Location((q[0], q[1], 0)))
    bot = bot + zc(6.2, q[2] + 12.0, q[2] + 34.0, q[0], q[1])
    pts = [(hx, hy, hz - 45.0), (hx, hy, hz - 90.0), (q[0] + 70.0, q[1], q[2] + 90.0), (q[0], q[1], q[2] + 70.0),
           (q[0], q[1], q[2] + 33.0)]
    h = rod(pts, r, 35.0)
    return lab(h + top + bot, spec)


def rear_hose_copper_washer(spec) -> Part:
    p, d = union_ports()["hose"]
    q = A.car(p)
    t = spec.nom("thickness")
    return lab(zc(7.0, q[2], q[2] + t, q[0], q[1]) - zc(4.7, q[2] - 1, q[2] + t + 1, q[0], q[1]), spec)


def rear_hose_bracket(spec) -> Part:
    """Pressed bracket on the body (P11 builds the panel it is welded to): a shelf the hose end passes through with
    the slot for the locking plate's tongue, and a flange up to the floor."""
    hx, hy, hz = _rear_bracket_xyz()
    b = box(hx - 16.0, hx + 26.0, hy - 14.0, hy + 14.0, hz, hz + BRK_T)
    b = b + box(hx + 26.0 - BRK_T, hx + 26.0, hy - 14.0, hy + 14.0, hz, hz + 34.0)
    for sy in (-1, 1):
        y0 = hy + (12.0 if sy > 0 else -14.0)
        b = b + _gusset(hx, y0, hz)
    b = b - zc(5.7, hz - 1, hz + BRK_T + 1, hx, hy)
    b = b - box(hx - 17.0, hx - 5.0, hy - 2.0, hy + 2.0, hz - 1, hz + BRK_T + 1)
    b = b - xcyl(3.3, hx + 22.0, hx + 27.0, hy, hz + 24.0)
    return lab(b, spec)


def _gusset(hx, y0, hz):
    from build123d import Face, Wire, extrude
    pts = [(hx + 6.0, y0, hz + BRK_T - 0.01), (hx + 26.0 - BRK_T + 0.01, y0, hz + BRK_T - 0.01), (hx + 26.0 - BRK_T + 0.01, y0, hz + 24.0)]
    return extrude(Face(Wire.make_polygon(pts, close=True)), 2.0, dir=(0, 1, 0))


def rear_locking_plate(spec) -> Part:
    hx, hy, hz = _rear_bracket_xyz()
    t = spec.nom("thickness")
    p = box(hx - 11.0, hx + 11.0, hy - 11.0, hy + 11.0, hz - t, hz) - hexp(16.1, t + 2, hz - t - 1).moved(Location((hx, hy, 0)))
    p = p + box(hx - 15.0, hx - 6.0, hy - 2.0, hy + 2.0, hz - t, hz + BRK_T)
    return lab(p, spec)


def rear_hose_locknut(spec) -> Part:
    hx, hy, hz = _rear_bracket_xyz()
    z0 = hz + BRK_T + 1.5
    return lab((chamfered_hex(15.9, 6.4, z0) - zc(5.6, z0 - 1, z0 + 8)).moved(Location((hx, hy, 0))), spec)


def rear_hose_lockwasher(spec) -> Part:
    hx, hy, hz = _rear_bracket_xyz()
    z0 = hz + BRK_T
    w = ring(5.7, 9.5, z0, z0 + 1.5)
    for k in range(10):
        w = w - (Location((0, 0, z0 + 1.2)) * Rot(0, 0, 36 * k) * Location((8.5, 0, 0)) * Sh.cyl(1.0, 1.0).moved(Location((0, 0, -0.5))))
    return lab(w.moved(Location((hx, hy, 0))), spec)


# =================================================================================================
# axle pipes (union to wheel cylinders) and their clips (12)
# =================================================================================================
def _tube_pt(y, r=None, a=None):
    r = B.AXLE_PIPE_R if r is None else r
    a = B.AXLE_PIPE_ANGLE if a is None else a
    return (r * math.sin(math.radians(a)), y, r * math.cos(math.radians(a)))


def axle_pipe_points(side):
    """AF: from the three-way connection's port to the wheel cylinder's inlet (pointing inboard on the neck end):
    the left-hand pipe passes behind the banjo bowl above the filler plug; both run along the rear-upper side of
    the tubes, over the top to the front near the backplate and down in front of the tube to the inlet."""
    p, d = union_ports()["lh" if side > 0 else "rh"]
    inlet = (0.0, side * (B.WC_NECK_END_Y - 4.0), B.WC_INLET_Z)
    pts = [p, along(p, d, 14.0)]
    if side > 0:
        pts += [(-70.0, UY + 40.0, 62.0), (-138.0, -40.0, 48.0), (-138.0, 60.0, 48.0), (-60.0, 150.0, 50.0)]
    y_run = side * 230.0
    pts += [_tube_pt(y_run), _tube_pt(side * 470.0), _tube_pt(side * 500.0, 46.0, 30.0), _tube_pt(side * 515.0, 50.0, 100.0),
            (8.0, side * 526.0, B.WC_INLET_Z + 2.0), (0.0, inlet[1] - side * 12.0, inlet[2]), inlet]
    return pts


def axle_pipe(side):
    def build(spec) -> Part:
        return lab(A.AF * pipe(axle_pipe_points(side), radius=12.0), spec)
    return build


def axle_clip(spec) -> Part:
    """Item 12: steel band round the tube with a loop holding the pipe, at |y| 300 (drawn on the left tube; the
    right-hand one is turned half round z)."""
    y = 300.0
    w = spec.nom("width")
    band = ring(A.TUBE_R, A.TUBE_R + 1.2, -w / 2, w / 2)
    band = Location((0, y, 0)) * Rot(-90, 0, 0) * band
    px, _, pz = _tube_pt(y)
    loop = ycyl(PIPE_OD / 2 + 1.4, y - w / 2, y + w / 2, px, pz) - ycyl(PIPE_OD / 2 + 0.2, y - w / 2 - 1, y + w / 2 + 1, px, pz)
    web = box(px - 2.0, px + 2.0, y - w / 2, y + w / 2, pz - 8.0, pz - 2.0)
    c = band + loop + (web - ycyl(PIPE_OD / 2 + 0.2, y - w, y + w, px, pz) - ycyl(A.TUBE_R + 0.01, y - w, y + w, 0, 0))
    return lab(A.AF * c, spec)


def grommet(spec) -> Part:
    """Rubber grommet in the pedal box floor round the master cylinder pipe."""
    sx, sy, _ = M.stub_end()
    z0 = B.BOX_Z[0]
    g = Sh.revolved([(PIPE_OD / 2 + 0.2, -3.0), (8.5, -3.0), (8.5, -0.01), (6.4, -0.01), (6.4, 1.61), (8.5, 1.61), (8.5, 4.0),
                     (PIPE_OD / 2 + 0.2, 4.0)])
    return lab(g.moved(Location((sx, sy, z0))), spec)


PARTS = {
    "brakes.lines.four-way": {"build": four_way},
    "brakes.lines.four-way-spacer": {"build": four_way_spacer},
    "brakes.lines.four-way-bolt": {"build": four_way_bolt},
    "brakes.lines.four-way-spring-washer": {"build": four_way_spring_washer},
    "brakes.lines.four-way-nut": {"build": four_way_nut},
    "brakes.lines.stop-switch": {"build": stop_switch},
    "brakes.lines.switch-washer": {"build": switch_washer},
    "brakes.lines.mc-pipe": {"build": mc_pipe, "probes": {"outside_diameter": lambda p: 2 * min(
        (v for v in (__import__("mgb.brake_parts", fromlist=["x"]).cyl_radius(f) for f in p.faces()) if v), key=lambda v: abs(v - PIPE_OD / 2))}},
    "brakes.lines.grommet": {"build": grommet},
    "brakes.lines.front-pipe-lh": {"build": front_pipe(1)},
    "brakes.lines.front-pipe-rh": {"build": front_pipe(-1)},
    "brakes.lines.rear-pipe": {"build": rear_pipe},
    "brakes.lines.rear-hose-bracket": {"build": rear_hose_bracket},
    "brakes.lines.rear-locking-plate": {"build": rear_locking_plate},
    "brakes.lines.rear-hose-locknut": {"build": rear_hose_locknut},
    "brakes.lines.rear-hose-lockwasher": {"build": rear_hose_lockwasher},
    "brakes.lines.rear-hose": {"build": rear_hose},
    "brakes.lines.rear-hose-copper-washer": {"build": rear_hose_copper_washer},
    "brakes.lines.union": {"build": union},
    "brakes.lines.union-bolt": {"build": union_bolt},
    "brakes.lines.union-spring-washer": {"build": union_spring_washer},
    "brakes.lines.axle-pipe-lh": {"build": axle_pipe(1)},
    "brakes.lines.axle-pipe-rh": {"build": axle_pipe(-1)},
    "brakes.lines.axle-clip": {"build": axle_clip},
}
