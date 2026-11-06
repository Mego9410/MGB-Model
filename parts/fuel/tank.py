"""Early strap-mounted fuel tank and its fittings (Haynes Ch 3 Sec 12, 15, 16; Fig 3.9 items 1-12, 25-33).

Drawn in place in the car frame from mgb.fuel_supply_layout, except the small fixings, which are drawn at the
origin and placed by assemblies/fuel_tank.py.
"""
from __future__ import annotations

import math

from build123d import (Axis, Box, Circle, Cylinder, Location, Part, Plane, Polygon, Rectangle, Rot, SlotCenterToCenter,
                       Spline, extrude, fillet, offset, sweep)

from mgb import fasteners as F, fuel_supply_layout as L, shapes as Sh, underbody_layout as U

IN = 25.4
X0, X1 = L.TANK_X                      # front, rear
Y0, Y1 = L.TANK_Y                      # right, left
TOP = L.TANK_TOP_Z
LEN = X0 - X1


def _l(p, spec):
    p.label = spec.id
    return p


def depth(u):
    """Tank depth below the top at u mm behind the front face (the curved bottom of the wedge)."""
    u = min(max(u, 0.0), LEN)
    a, b = 60.0, LEN - 45.0
    if u <= a:
        return L.DEPTH_FRONT
    if u >= b:
        return L.DEPTH_REAR
    return L.DEPTH_FRONT + (L.DEPTH_REAR - L.DEPTH_FRONT) * math.sin(math.pi / 2 * (u - a) / (b - a))


def profile_pts(grow=0.0):
    """Side profile (u, d) round the tank, u behind the front face, d below the top; grown outward by `grow`."""
    pts = []

    def arc(cu, cd, r, a0, a1, n=10):
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n)
            pts.append((cu + (r + grow) * math.cos(a), cd + (r + grow) * math.sin(a)))
    rf, rr, rb, rfb = 25.0, 20.0, 45.0, 60.0
    arc(rf, rf, rf, 180, 270)                                   # front top corner (d down is +)
    arc(LEN - rr, rr, rr, 270, 360)                             # rear top corner
    arc(LEN - rb, L.DEPTH_REAR - rb, rb, 0, 90)                 # rear bottom corner
    for k in range(1, 24):                                     # the curved bottom
        u = (LEN - rb) - (LEN - rb - rfb) * k / 24
        pts.append((u, depth(u) + grow))
    arc(rfb, L.DEPTH_FRONT - rfb, rfb, 90, 180)                 # front bottom corner
    return pts


def _xz(pts):
    """(u, d) -> car (x, z)."""
    return [(X0 - u, TOP - d) for u, d in pts]


def _slab(pts_xz, y0, y1):
    """Extrude a closed x-z outline across the car from y0 to y1."""
    pl = Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    return extrude(pl * Polygon(*[(x, -z) for x, z in pts_xz], align=None), y1 - y0, dir=(0, 1, 0))


def volume_litres():
    from build123d import Polygon as P
    return P(*_xz(profile_pts()), align=None).area * (Y1 - Y0) / 1e6


def tank(spec) -> Part:
    """Fig 3.9 item 1 (earlier type): a wedge with a flat top and a curved bottom (MGOC), the end plates rolled
    into a seam flange all round, an X-shaped pressed panel in the top, the filler stub on top, the gauge unit's
    six-screw ring and the outlet stub on the right-hand end, the drain plug boss underneath."""
    body = _slab(_xz(profile_pts()), Y0 + 1.0, Y1 - 1.0)
    for ys in (Y0, Y1 - 3.0):                                   # rolled seams round the end plates
        body = body + _slab(_xz(profile_pts(L.SEAM_W)), ys, ys + 3.0)
    # hollow: the inside, 1 mm shell
    body = body - _slab(_xz(profile_pts(-1.0)), Y0 + 2.0, Y1 - 2.0)
    # X-shaped raised panel in the top (Fig 3.9)
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    a = math.degrees(math.atan2(LEN - 120.0, (Y1 - Y0) - 160.0))
    d = math.hypot(LEN - 120.0, (Y1 - Y0) - 160.0)
    for s in (1, -1):
        bead = Location((cx, cy, TOP - 0.5)) * Rot(0, 0, s * (90 - a)) * extrude(SlotCenterToCenter(d, 26.0), 3.0)
        bead = bead - Location((L.FILLER[0], L.FILLER[1], TOP - 2.0)) * Sh.cyl(L.FILLER_OD + 46.0, 8.0)   # flat round the filler
        body = body + bead
    # filler stub with a reinforcing collar
    fx, fy = L.FILLER
    body = body + Location((fx, fy, TOP - 2.0)) * Sh.tube(L.FILLER_OD, L.FILLER_OD - 3.0, L.FILLER_STUB_H + 2.0)
    body = body + Location((fx, fy, TOP - 0.5)) * Sh.tube(L.FILLER_OD + 24.0, L.FILLER_OD - 3.0, 1.0)
    body = body + Location((fx, fy, TOP + L.FILLER_STUB_H - 5.0)) * Sh.tube(L.FILLER_OD + 1.5, L.FILLER_OD - 3.0, 3.0)
    body = body - Location((fx, fy, TOP - 6.0)) * Sh.cyl(L.FILLER_OD - 3.0, 10.0)
    # gauge unit ring on the right-hand end plate: six tapped holes
    sx, sz = L.SENDER
    ring = Location(Plane(origin=(sx, Y0 + 0.5, sz), z_dir=(0, -1, 0))) * Sh.tube(L.SENDER_PCD + 16.0, L.SENDER_BORE, 3.0)
    body = body + ring
    body = body - Location(Plane(origin=(sx, Y0 + 4.0, sz), z_dir=(0, -1, 0))) * Sh.cyl(L.SENDER_BORE, 10.0)
    for k in range(6):
        t = math.radians(30.0 + 60.0 * k)
        body = body - Location(Plane(origin=(sx + L.SENDER_PCD / 2 * math.cos(t), Y0 - 3.0, sz + L.SENDER_PCD / 2 *
                                             math.sin(t)), z_dir=(0, 1, 0))) * Sh.cyl(3.2, 6.0)
    # outlet: stub out of the right-hand end plate turned forward to its union thread
    ox, oz = L.OUTLET
    sp = [(ox, Y0 + 2.0, oz), (ox, L.TANK_STUB_END[1], oz), (L.TANK_STUB_END[0] - 12.0, L.TANK_STUB_END[1], oz)]
    from parts.fuel.exhaust import tube
    body = body + tube(sp, 8.0, None, radius=8.0)
    body = body + Location(Plane(origin=(L.TANK_STUB_END[0] - 13.0, L.TANK_STUB_END[1], oz), z_dir=(1, 0, 0))) * \
        Sh.cyl(10.5, 13.0)
    body = body + Location(Plane(origin=(ox, Y0 + 0.5, oz), z_dir=(0, -1, 0))) * Sh.cyl(16.0, 3.0)      # weld boss
    # drain plug boss underneath
    dx, dy = L.DRAIN
    dz = TOP - depth(X0 - dx)
    body = body + Location((dx, dy, dz - 4.0)) * Sh.cyl(30.0, 6.0)
    body = body - Location((dx, dy, dz - 5.0)) * Sh.cyl(14.0, 10.0)
    return _l(body, spec)


def drain_plug(spec) -> Part:
    """Fig 3.9 item 2: hexagon-headed plug, its washer (item 3) above."""
    h = F.hex_nut("3/8")
    head = h.moved(Location((0, 0, -h.bounding_box().size.Z)))
    shank = Sh.cyl(14.0, 10.0)
    return _l(head + shank, spec)


def drain_washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), 14.2, spec.nom("thickness")), spec)


# ---------------------------------------------------------------------------------------------------------------
# straps, packing strips, hangers
# ---------------------------------------------------------------------------------------------------------------
def strap_path(off):
    """Centre line of a strap (or packing) at offset `off` outside the tank, from the front pin to the rear tab.
    Returns (x, z) points."""
    pts = profile_pts(off)
    # profile_pts runs front-top -> rear-top -> rear-bottom -> bottom -> front-bottom; reorder front face first:
    # start on the front face below the top corner, go down, under, up the rear face.
    fb = [p for p in pts if p[0] <= 60.0 and p[1] >= 30.0]           # front-bottom arc (u small)
    fb = sorted(fb, key=lambda p: p[1])
    bottom = [p for p in pts if 60.0 < p[0] < LEN - 45.0]
    bottom = sorted(bottom, key=lambda p: p[0])
    rb = [p for p in pts if p[0] >= LEN - 45.0 and p[1] >= 30.0]
    rb = sorted(rb, key=lambda p: -p[1])
    return _xz(fb + bottom + rb)


def strap(spec) -> Part:
    """Fig 3.9 item 5: a steel strap from a forked end pinned at the front, down the front face, under the curved
    bottom and up the rear face to an end tab under the rear hanger (nuts at the rear, Sec 12 para 6)."""
    off = L.PACK_T + L.STRAP_T / 2 + 0.4
    path = strap_path(off)
    fx, fz = L.STRAP_PIN_FRONT
    tab_z = L.HANGER_FOOT_Z - 25.0
    pts = ([(fx - 4.0, fz - 7.0), (X0 + off, fz - 22.0), (X0 + off, TOP - 70.0)] + path +
           [(X1 - off, TOP - 100.0), (X1 - off, tab_z - 10.0), (X1 - off - 12.0, tab_z)])
    sp = Spline(*[(x, 0.0, z) for x, z in pts])
    pl = Plane(origin=sp.position_at(0), x_dir=(0, 1, 0), z_dir=sp.tangent_at(0))
    out = sweep(pl * Rectangle(L.STRAP_W, L.STRAP_T), path=sp)
    # rear tab and its bolt hole, front eye round the pin
    tab = Location((X1 - off - 10.0 - 14.0, 0.0, tab_z)) * Box(30.0, L.STRAP_W, L.STRAP_T)
    tab = tab - Location((L.STRAP_BOLT_X, 0.0, tab_z - 3)) * Sh.cyl(7.0, 6.0)
    eye = Location(Plane(origin=(fx, -L.STRAP_W / 2, fz), z_dir=(0, 1, 0))) * Sh.tube(15.0, 7.0, L.STRAP_W)
    eye = eye - Location((fx, 0, fz)) * Box(16.0, 8.0, 16.0)                      # forked: slot for the body tab
    out = out + tab + eye
    return _l(out, spec)


def packing_strip(spec) -> Part:
    """Fig 3.9 item 4: rubber packing strip between each strap and the tank."""
    pts = strap_path(L.PACK_T / 2 + 0.2)
    sp = Spline(*[(x, 0.0, z) for x, z in pts])
    pl = Plane(origin=sp.position_at(0), x_dir=(0, 1, 0), z_dir=sp.tangent_at(0))
    return _l(sweep(pl * Rectangle(L.STRAP_W + 3.0, L.PACK_T), path=sp), spec)


def rear_hanger(spec) -> Part:
    """Fig 3.9 item 6: pressed channel hanging from the body tab on the clevis pin, the strap bolt through its foot."""
    px, pz = L.HANGER_PIN
    fz = L.HANGER_FOOT_Z
    w, t = 26.0, 2.5
    h = None
    for y0 in (-w / 2 - t, w / 2):
        pl = Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        s = extrude(pl * Polygon(*[(x, -z) for x, z in [(px - 12, pz + 10), (px + 12, pz + 10), (px + 14, fz),
                                                        (px - 14, fz)]], align=None), t, dir=(0, 1, 0))
        h = s if h is None else h + s
    foot = Location((px, 0, fz + t / 2)) * Box(28.0, w + 2 * t, t)
    h = h + foot
    h = h - Location(Plane(origin=(px, -w, pz), z_dir=(0, 1, 0))) * Sh.cyl(6.8, 2 * w)
    h = h - Location((px, 0, fz - 1.0)) * Sh.cyl(7.0, t + 2.0)
    return _l(h, spec)


def clevis_pin(spec) -> Part:
    """Fig 3.9 item 7: 1/4 in clevis pin, domed head, split pin hole."""
    L_ = spec.nom("length")
    p = Sh.revolved([(0, 0), (6.35 / 2, 0), (6.35 / 2, L_), (0, L_)]) + Sh.revolved([(0, -2.5), (5.5, -2.5), (5.5, -0.5),
                                                                                    (4.5, 0.2), (0, 0.2)])
    p = p - Location((0, 0, L_ - 3.0)) * Rot(90, 0, 0) * Cylinder(0.85, 10.0)
    return _l(p, spec)


def split_pin(spec) -> Part:
    """1/16 in split pin through the clevis pin, legs opened."""
    r = 0.8
    eye = Location((0, 0, 0)) * Rot(90, 0, 0) * Sh.tube(4.0, 1.6, 2 * r).moved(Location((0, 0, -r)))
    legs = Location((0, 0, -6.5)) * Box(2 * r, 2 * r * 2, 9.0)
    return _l(eye + legs, spec)


def small_washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def nyloc_nut(spec) -> Part:
    n = F.hex_nut("1/4")
    h = n.bounding_box().size.Z
    return _l(n + Location((0, 0, h)) * Sh.tube(9.5, 6.0, 2.5), spec)


def bolt(size, length_in):
    def build(spec) -> Part:
        return _l(F.hex_bolt(size, length_in), spec)
    return build


# ---------------------------------------------------------------------------------------------------------------
# filler
# ---------------------------------------------------------------------------------------------------------------
FX, FY = L.FILLER
STUB_TOP = TOP + L.FILLER_STUB_H
HOSE = (STUB_TOP - 22.0, STUB_TOP + 44.0)             # filler hose 27, z range
ELBOW_Z0 = STUB_TOP + 6.0


def filler_seal(spec) -> Part:
    """Fig 3.9 item 12: rubber seal, tank to boot floor, round the filler stub: a flange squeezed between the
    tank top and the floor, a neck through the floor panel's hole and a lip over it inside the boot."""
    z = U.BOOT_FLOOR_Z
    od, idd = L.FILLER_OD + 36.0, L.FILLER_OD + 0.4
    g = z - TOP                                         # gap between the tank top and the floor
    s = Sh.revolved([(idd / 2, -g + 0.7), (od / 2 - 2, -g + 0.7), (od / 2, -g + 1.5), (od / 2, -0.2),
                     (od / 2 - 14, -0.2), (od / 2 - 14, 1.2), (od / 2 - 6, 1.2), (od / 2 - 6, 5.0), (idd / 2, 6.0)])
    return _l(s.moved(Location((FX, FY, z))), spec)


def filler_hose(spec) -> Part:
    """Fig 3.9 item 27: connection hose from the tank's stub to the filler tube."""
    od, idd = L.FILLER_OD + 12.0, L.FILLER_OD
    return _l(Location((FX, FY, HOSE[0])) * Sh.tube(od, idd, HOSE[1] - HOSE[0]), spec)


def hose_clip(spec) -> Part:
    """Fig 3.9 item 28: worm-drive clip, 2 in (MGOC GHC1622), axis along z at the origin."""
    d, w = spec.nom("diameter"), spec.nom("width")
    c = Sh.tube(d + 1.6, d, w).moved(Location((0, 0, -w / 2)))
    housing = Location((d / 2 + 4.0, 0, 0)) * Box(8.0, 14.0, w + 2.0)
    screw = Location((d / 2 + 6.0, 0, 0)) * Rot(90, 0, 0) * Cylinder(2.6, 22.0)
    return _l(c + housing + screw, spec)


def filler_tube(spec) -> Part:
    """Fig 3.9 item 26: the filler extension, up from the hose and back across the boot to the cap on the rear
    panel right of the number plate (Oliver's photos 11, 18, 21; P11b moved the cap there), a bead at the hose end and
    the cap's neck and body flange at the rear panel."""
    from parts.fuel.exhaust import tube
    zt = L.FILLER_TUBE_TOP_Z
    cx, cy = L.FILLER_CAP_X, L.FILLER_CAP_Y
    pts = [(FX, FY, ELBOW_Z0), (FX, FY, zt), (cx + 150.0, cy, zt), (cx + 18.0, cy, zt)]
    t = tube(pts, L.FILLER_OD - 0.4, 1.2, radius=45.0)
    t = t + Location((FX, FY, ELBOW_Z0 + 6.0)) * Sh.tube(L.FILLER_OD + 1.0, L.FILLER_OD - 3.0, 3.0)     # hose bead
    neck = Location(Plane(origin=(cx + 18.0, cy, zt), z_dir=(-1, 0, 0)))
    t = t + neck * Sh.tube(L.FILLER_OD + 10.0, L.FILLER_OD - 3.0, 18.0)
    t = t + neck * Location((0, 0, 4.0)) * Sh.tube(L.FILLER_OD + 26.0, L.FILLER_OD + 9.0, 2.0)          # body flange
    return _l(t, spec)


def filler_cap(spec) -> Part:
    """Fig 3.9 item 29: Oliver's car has a chrome locking cap (his photo 21; kf173, kf176; QA fix round 1): a shallow
    dome 64 mm across seated in the black rubber ring (filler-ring), a raised flip lever lying from the centre out to
    the rim at the upper right (seen from behind), its end turned down over the rim to lift, and the lock barrel with
    its keyhole below the centre. Local frame (the assembly's): z out of the panel (rearward), x to the car's left,
    y down."""
    d = spec.nom("diameter")
    r = d / 2
    c = Sh.revolved([(0, 2.0), (r - 2.0, 2.0), (r, 4.0), (r, 8.0), (r - 2.5, 12.0), (r - 10.0, 15.5), (0, 17.0)])
    c = c + Location((0, 0, -10.0)) * Sh.tube(L.FILLER_OD - 4.0, L.FILLER_OD - 9.0, 12.0)               # spigot
    a = math.radians(225.0)                                   # up and to the right seen from behind: local -x, -y
    ux, uy = math.cos(a), math.sin(a)
    lever = Box(30.0, 10.0, 6.0)
    lever = Location((ux * 13.0, uy * 13.0, 18.0)) * Rot(0, 0, math.degrees(a)) * fillet(lever.edges().filter_by(Axis.X), 2.8)
    tab = Box(5.0, 10.0, 12.0)
    tab = Location((ux * (r - 1.0), uy * (r - 1.0), 13.0)) * Rot(0, 0, math.degrees(a)) * fillet(tab.edges().filter_by(Axis.Z), 2.0)
    pivot = Location((0, 0, 17.0)) * Rot(0, 0, math.degrees(a) + 90.0) * Rot(0, 90, 0) * Cylinder(4.0, 14.0)
    c = c + lever + tab + pivot
    bx_, by_ = -ux * 13.0, -uy * 13.0                        # the lock barrel, opposite the lever
    c = c + Location((bx_, by_, 14.0)) * Cylinder(7.0, 6.0, align=Sh.ALIGN_BASE)
    c = c - Location((bx_, by_ + 1.0, 18.5)) * Box(1.6, 6.0, 4.0) - Location((bx_, by_ - 1.8, 18.5)) * Cylinder(1.6, 4.0)
    return _l(c, spec)


def filler_ring(spec) -> Part:
    """Black rubber ring round the filler cap on the rear panel (Oliver's photo 21; kf173, kf176: about 12 mm wide,
    80 mm over all, standing proud of the panel), its back following the panel's curve into the lid gap above."""
    od, w = spec.nom("diameter"), spec.nom("width")
    ring = Sh.revolved([(od / 2 - w, -30.0), (od / 2, -30.0), (od / 2, 2.0), (od / 2 - 2.5, 5.0), (od / 2 - w + 2.0, 5.0),
                        (od / 2 - w, 3.0)])
    return _l(ring, spec)


# ---------------------------------------------------------------------------------------------------------------
# gauge unit
# ---------------------------------------------------------------------------------------------------------------
def gauge_unit(spec) -> Part:
    """Fig 3.9 item 30 (early): six-screw flange plate, the resistance housing with two terminals outside, the
    float arm and float inside the tank. Drawn at the origin, flange face on z = 0, outside toward +z."""
    pcd = L.SENDER_PCD
    plate = Sh.washer(pcd + 14.0, 0.1, 1.6)
    for k in range(6):
        t = math.radians(30.0 + 60.0 * k)
        plate = plate - Location((pcd / 2 * math.cos(t), pcd / 2 * math.sin(t), -1.0)) * Sh.cyl(3.6, 4.0)
    housing = Location((0, 0, 1.6)) * Sh.revolved([(0, 0), (24.0, 0), (24.0, 10.0), (20.0, 15.0), (0, 15.0)])
    terms = None
    for dx in (-8.0, 8.0):
        tm = Location((dx, 0, 16.6)) * (Sh.cyl(6.0, 3.0) + Location((0, 0, 3.0)) * Box(1.0, 6.3, 9.0, align=Sh.ALIGN_BASE))
        terms = tm if terms is None else terms + tm
    inner = Location((0, 0, -12.0)) * Sh.cyl(34.0, 12.0)                         # rheostat body inside the tank
    from parts.fuel.exhaust import tube
    arm = tube([(0, 0, -6.0), (0, 0, -24.0), (0, -45.0, -40.0), (0, -64.0, -55.0)], 3.0, None, radius=10.0)
    flt = Location(Plane(origin=(-25.0, -70.0, -55.0), z_dir=(1, 0, 0))) * Sh.cyl(22.0, 50.0)
    return _l(plate + housing + terms + inner + arm + flt, spec)


def gauge_gasket(spec) -> Part:
    """Fig 3.9 item 32: cork gasket, six holes (MGOC 2H1082B)."""
    pcd = L.SENDER_PCD
    g = Sh.washer(pcd + 14.0, L.SENDER_BORE, spec.nom("thickness"))
    for k in range(6):
        t = math.radians(30.0 + 60.0 * k)
        g = g - Location((pcd / 2 * math.cos(t), pcd / 2 * math.sin(t), -1.0)) * Sh.cyl(4.0, 4.0)
    return _l(g, spec)


def gauge_screw(spec) -> Part:
    """Fig 3.9 item 33: pan head screw (MGOC 53K165)."""
    L_ = spec.nom("length")
    s = Sh.revolved([(0, 0), (1.6, 0), (1.6, L_), (0, L_)]) + Location((0, 0, L_)) * Sh.revolved(
        [(0, 0), (3.2, 0), (3.2, 1.2), (2.4, 2.4), (0, 2.6)])
    s = s - Location((0, 0, L_ + 2.0)) * Box(7.0, 0.9, 2.0)
    return _l(s, spec)


PARTS = {
    "fuel.tank.tank": {"build": tank, "probes": {"capacity_litres": lambda p: volume_litres(),
                                                  "length": lambda p: X0 - X1}},
    "fuel.tank.drain-plug": {"build": drain_plug},
    "fuel.tank.drain-washer": {"build": drain_washer},
    "fuel.tank.strap": {"build": strap},
    "fuel.tank.packing-strip": {"build": packing_strip},
    "fuel.tank.rear-hanger": {"build": rear_hanger},
    "fuel.tank.clevis-pin": {"build": clevis_pin},
    "fuel.tank.split-pin": {"build": split_pin},
    "fuel.tank.pin-washer": {"build": small_washer},
    "fuel.tank.strap-bolt": {"build": bolt("1/4", 2.25)},
    "fuel.tank.strap-washer": {"build": small_washer},
    "fuel.tank.strap-nut": {"build": nyloc_nut},
    "fuel.tank.filler-seal": {"build": filler_seal},
    "fuel.tank.filler-hose": {"build": filler_hose},
    "fuel.tank.hose-clip": {"build": hose_clip},
    "fuel.tank.filler-tube": {"build": filler_tube},
    "fuel.tank.filler-cap": {"build": filler_cap},
    "fuel.tank.filler-ring": {"build": filler_ring},
    "fuel.tank.gauge-unit": {"build": gauge_unit},
    "fuel.tank.gauge-gasket": {"build": gauge_gasket},
    "fuel.tank.gauge-screw": {"build": gauge_screw},
}
