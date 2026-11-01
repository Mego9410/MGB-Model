"""Distributor housing and drive, Lucas 25D4 distributor, HT leads and plug caps.
Haynes Ch 1 Sec 16/63 (drive and housing), Ch 4 Sec 2, 3, 6 and Fig 4.3 (25D4); specs p94-95.

Distributor parts are built in the distributor frame: z up the leaning axis from the
top face of the block boss, x forward, -y outboard (mgb.ignition_layout). The assembly
places them with one transform. HT leads are built in the engine frame; plug caps
along +Z from the plug terminal.

Shapes follow Fig 4.3: the body is a die-cast cone that narrows from the cap rim to a
waist carrying the vacuum unit spindle, over a plain shank; the clamping plate is a
split ring with a pinch bolt and a slotted tongue; the side-entry cap has its four lead
bosses on the upper wall, a pointed retaining screw for each lead on the shoulder and
the coil lead in the centre.
"""
import math

from build123d import Align, Axis, Box, Circle, Cylinder, FilletPolyline, Location, Part, Plane, Polygon, Rectangle, Rot, \
    extrude, fillet, sweep

from mgb import fasteners as F, ignition_layout as G, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
CAP_R = 33.0                     # cap outside radius (spec "diameter" / 2)
BOSS_OUT = 6.0                   # lead bosses stand this far proud of the cap wall
VAC_Y, VAC_Z = -21.0, G.BODY_Z + 6.0     # vacuum spindle line (frame), tangent to the waist
LT_ANGLE = 120.0                 # low tension terminal, frame angle
CLIP_ANGLES = (0.0, 180.0)


def _l(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def xc(r, x0, x1, y, z):
    return Cylinder(r, x1 - x0, rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def polar(r, deg, z):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a), z)


def _tf(p, edges, r):
    try:
        return fillet(edges, r)
    except Exception:  # noqa: BLE001
        return p


def _rod(points, r, radius):
    path = None
    for rr in (radius, radius * 0.5, radius * 0.25):
        try:
            path = FilletPolyline(*points, radius=rr)
            break
        except ValueError:
            continue
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    return sweep(pl * Circle(r), path=path)


# ---- housing and drive (Haynes Ch 1 Sec 16, 63) ------------------------------------------------
def housing(spec) -> Part:
    """Cast housing in the block boss: spigot into the bore, flange on the boss face with
    the two clamp-plate bolt holes, and the tab for the single retaining bolt (Sec 63 para 5)."""
    h = zc(14.0, -40, 0) + zc(24.0, 0, G.FLANGE_T)
    h = _tf(h, h.edges().group_by(Axis.Z)[-1], 1.5)
    lug_x = G.LUG_X
    tab = Location((lug_x / 2 + 4, 0, G.FLANGE_T / 2)) * Box(lug_x + 8, 18, G.FLANGE_T)
    h = h + _tf(tab, tab.edges().filter_by(Axis.Z), 5.0)
    h = h + zc(8.5, 0, G.FLANGE_T, lug_x, 0)                          # bolt eye
    h = h - zc(spec.nom("bore") / 2, -41, G.FLANGE_T + 1)
    h = h - zc(4.2, -2, G.FLANGE_T + 3, lug_x, 0)
    for sx in (-17.0, 17.0):                                          # clamp plate bolts (Ch 4 Sec 6 para 7)
        h = h + zc(5.5, 0, G.FLANGE_T, sx, 12.0)
        h = h - zc(2.6, G.FLANGE_T - 9, G.FLANGE_T + 1, sx, 12.0)
    return _l(h, spec)


def drive_shaft(spec) -> Part:
    """Driveshaft with its skew gear; the offset slot at the top takes the distributor
    dog (Fig 1.26), and the tapped hole takes the 5/16 UNF bolt used to withdraw it
    (Sec 16 para 3). Its lower end runs on toward the camshaft inside the block."""
    L = spec.nom("length")
    s = zc(7.0, -L, -8) + zc(10.5, -L, -L + 18)
    for k in range(10):                                               # skew teeth
        s = s - (Location((0, 0, -L + 9)) * Rot(0, 0, 36 * k) * Location((10.5, 0, 0)) * Rot(28, 0, 0)
                 * Box(2.6, 3.2, 24))
    s = s + zc(9.5, -10, -1)
    s = s - Location((1.5, 0, -2.5)) * Box(20, 3.2, 5)               # offset slot, large segment one side
    s = s - zc(3.3, -16, -4)
    return _l(s, spec)


# ---- Lucas 25D4 (Fig 4.3) ---------------------------------------------------------------------
def clamp_plate(spec) -> Part:
    """Item 1: split ring round the shank with its pinch bolt lug, and the tongue with the
    two bolt holes onto the housing (one slotted for timing adjustment)."""
    t = spec.nom("thickness")
    z0 = G.CLAMP_Z
    ring = zc(19.0, z0, z0 + t)
    tongue = Location((0, 12.0, z0 + t / 2)) * Box(48, 22, t)
    p = ring + _tf(tongue, tongue.edges().filter_by(Axis.Z), 6.0)
    lug = Location((0, -22.0, z0 + 5)) * Box(16, 10, 10)
    p = p + lug
    p = p - zc(13.6, z0 - 1, z0 + t + 1)
    p = p - Location((0, -22.0, z0 + 5)) * Box(2.0, 14, 12)            # split
    p = p - xc(2.7, -10, 10, -23.0, z0 + 5)                           # pinch bolt
    p = p - Location((17.0, 12.0, z0 + t / 2)) * Box(5.2, 11, t + 2)  # slot
    p = p - zc(2.7, z0 - 1, z0 + t + 1, -17.0, 12.0)
    return _l(p, spec)


def pinch_bolt(spec) -> Part:
    """Clamp plate pinch bolt with its nut, along +Z from the head."""
    L = spec.nom("length")
    return _l(F.hex_bolt("1/4", L / 25.4) + F.hex_nut("1/4").moved(Location((0, 0, L - 7))), spec)


def body(spec) -> Part:
    """Die-cast body: shank, waist and conical bowl with the cap clip pivots, the
    vacuum spindle bracket, the low tension terminal block and the rim lug."""
    z0, z1 = G.BODY_Z, G.CAP_Z
    prof = [(0, G.CLAMP_Z - 38), (13.4, G.CLAMP_Z - 38), (13.4, z0 - 2), (17.0, z0 - 2), (17.0, z0 + 12),
            (21.0, z0 + 16), (29.5, z1 - 7), (31.5, z1 - 6), (31.5, z1), (0, z1)]
    b = Sh.revolved(prof)
    b = b - Sh.revolved([(0, z0 + 13), (17.5, z0 + 13), (27.0, z1 - 6), (28.6, z1 - 3), (28.6, z1 + 1), (0, z1 + 1)])
    b = b - zc(6.5, G.CLAMP_Z - 39, z0 + 14)                        # bush bore
    b = b - Location((0, 0, G.CLAMP_Z - 30)) * Box(40, 3, 1.5)       # oil seal groove line
    # vertical clip channels with the pivot lugs below them (item 15)
    for a in CLIP_ANGLES:
        x, y, _ = polar(31.0, a, 0)
        r = Location((x, y, (z0 + 20 + z1) / 2)) * Rot(0, 0, a) * Box(4, 9, z1 - z0 - 20)
        b = b + r
        lx, ly, _ = polar(24.0, a, 0)
        b = b + Location((lx, ly, z0 + 14)) * Rot(0, 0, a) * Box(10, 10, 8)
        b = b - (Location((lx, ly, z0 + 14)) * Rot(0, 0, a) * Cylinder(1.6, 14, rotation=(90, 0, 0)))
    # vacuum spindle bracket: a tube tangent to the waist, with its web
    b = b + xc(4.6, -12, 12, VAC_Y, VAC_Z) + Location((0, VAC_Y / 2 - 4, VAC_Z)) * Box(16, 14, 7)
    b = b - xc(2.4, -14, 14, VAC_Y, VAC_Z)
    # low tension terminal block through the bowl wall (item 7)
    tx, ty, _ = polar(27.0, LT_ANGLE, 0)
    b = b + Location((tx, ty, z0 + 24)) * Rot(0, 0, LT_ANGLE) * Box(12, 10, 14)
    sx, sy, _ = polar(33.0, LT_ANGLE, 0)
    b = b + Location((sx, sy, z0 + 26)) * Rot(0, 0, LT_ANGLE) * Cylinder(2.4, 12, rotation=(0, 90, 0))
    # lug at the rim (Fig 4.3, right of the bowl)
    ex, ey, _ = polar(35.0, 55.0, 0)
    ear = Location((ex, ey, z1 - 9)) * Rot(0, 0, 55) * Box(14, 12, 6)
    b = b + ear - (Location((ex + 2, ey, z1 - 9)) * Cylinder(2.6, 10))
    return _l(b, spec)


def vacuum_unit(spec) -> Part:
    """Item 16: diaphragm housing with the pipe union, the threaded spindle through the
    body bracket and the knurled micrometer adjusting nut (Sec 6 para 13)."""
    d = spec.nom("diameter")
    x0 = 28.0
    dome = Sh.revolved([(0, 0), (d / 2, 0), (d / 2, 4), (d / 2 - 2, 7), (d / 2 - 8, 14), (8, 20), (5, 21),
                        (0, 21)])
    v = Location((x0, VAC_Y, VAC_Z)) * Rot(0, 90, 0) * dome
    v = v + xc(2.8, x0 + 20, x0 + 28, VAC_Y, VAC_Z)                  # union stub
    v = v + xc(2.3, -44, x0, VAC_Y, VAC_Z)                            # spindle
    nut = xc(8.0, -40, -33, VAC_Y, VAC_Z)
    for k in range(18):                                               # knurl
        a = 20 * k
        nut = nut - (Location((-36.5, VAC_Y + 8 * math.cos(math.radians(a)), VAC_Z + 8 * math.sin(math.radians(a))))
                     * Box(9, 1.0, 1.0))
    v = v + nut + Location((-22, VAC_Y, VAC_Z)) * Rot(0, 90, 0) * Sh.coil_spring(0.7, 7.0, 9, 4).moved(Location((0, 0, -4.5)))
    for x in range(-30, int(x0), 3):                                 # thread on the spindle
        v = v + xc(2.7, x, x + 1.2, VAC_Y, VAC_Z)
    return _l(v, spec)


def cap_clip(spec) -> Part:
    """Item 15: spring clip, from its pivot on the body up the bowl and over the cap rim.
    Built for the clip at frame angle 0 (+X); the assembly turns it to each lug."""
    z0, z1 = G.BODY_Z, G.CAP_Z
    w = spec.nom("width")
    pts = [(24.0, z0 + 14), (33.5, z0 + 22), (35.2, z1 + 1), (35.2, z1 + 6), (32.0, z1 + 7.5)]
    path = FilletPolyline(*[(x, 0, z) for x, z in pts], radius=1.5)
    prof = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0), x_dir=(0, 1, 0)) * Rectangle(w, 1.0)
    c = sweep(prof, path=path)
    c = c + Location((24.0, 0, z0 + 14)) * Cylinder(2.4, w + 2, rotation=(90, 0, 0))
    return _l(c, spec)


def cap(spec) -> Part:
    """Item 2: moulded side-entry cap. Skirt with the clip notches and ribs, four lead
    bosses on the upper wall, a pointed retaining screw for each lead on the shoulder,
    and the coil lead tower in the centre."""
    r = spec.nom("diameter") / 2
    z0, h = G.CAP_Z, G.CAP_H
    c = Sh.revolved([(0, 0), (r + 1.2, 0), (r + 1.2, 8), (r, 9), (r, h - 12), (r - 6, h - 3), (12, h), (0, h)])
    c = c.moved(Location((0, 0, z0)))
    c = c - Sh.revolved([(0, -1), (r - 3.5, -1), (r - 3.5, h - 14), (r - 9, h - 7), (0, h - 6)]).moved(
        Location((0, 0, z0)))
    for k in range(4):
        a = G.tower_angle(k)
        boss = Location((0, 0, G.TOWER_Z)) * Rot(0, 0, a) * xc(7.0, r - 4, r + BOSS_OUT, 0, 0)
        c = c + boss - Location((0, 0, G.TOWER_Z)) * Rot(0, 0, a) * xc(3.6, r - 6, r + BOSS_OUT + 1, 0, 0)
        sx, sy, _ = polar(r - 5.0, a, 0)                              # lead retaining screw head
        c = c + zc(3.0, z0 + h - 9, z0 + h - 5.5, sx, sy) - Location((sx, sy, z0 + h - 4.5)) * Rot(0, 0, a) * \
            Box(6.5, 0.8, 2.0)
    for k in range(8):                                                # skirt ribs
        a = 45.0 * k + 22.5
        x, y, _ = polar(r + 0.6, a, 0)
        c = c + Location((x, y, z0 + 4)) * Rot(0, 0, a) * Box(2.0, 3.0, 8)
    tower = zc(9.0, z0 + h - 2, z0 + h + 10)
    c = c + _tf(tower, tower.edges().group_by(Axis.Z)[-1], 2.5) - zc(3.6, z0 + h - 7, z0 + h + 11)
    for a in CLIP_ANGLES:                                             # clip notches
        x, y, _ = polar(r + 1.0, a, 0)
        c = c - Location((x, y, z0 + 4)) * Rot(0, 0, a) * Box(5, 9, 9)
    return _l(c, spec)


def brush(spec) -> Part:
    """Item 3: carbon brush and spring in the cap centre."""
    return _l(zc(2.4, G.CAP_Z + 4, G.CAP_Z + 16) + Sh.coil_spring(0.5, 4.6, 10, 6).moved(
        Location((0, 0, G.CAP_Z + 14))), spec)


def rotor(spec) -> Part:
    """Item 4: rotor arm on the cam spindle, with its brass blade."""
    z0 = G.CAP_Z
    r = zc(8.0, z0 - 12, z0 + 6) - zc(4.4, z0 - 13, z0 + 2)
    arm = Location((10, 0, z0 + 4)) * Box(24, 9, 4)
    blade = Location((19, 0, z0 + 6.5)) * Box(10, 6, 1.0)
    return _l(r + _tf(arm, arm.edges().filter_by(Axis.Z), 2.0) + blade, spec)


def baseplate(spec) -> Part:
    """Items 5, 8, 9, 10: contact breaker baseplate, moving plate, the contact set on its
    pivot post and the earth lead."""
    z0 = G.BODY_Z + 13.5
    p = zc(19.0, z0, z0 + 1.4) - zc(8.5, z0 - 1, z0 + 3)
    p = p + (zc(17.0, z0 + 1.4, z0 + 2.6) - zc(9.5, z0, z0 + 4))
    for sx, sy in ((-14, -9), (14, 9)):                               # securing screws
        p = p + zc(2.6, z0 + 2.6, z0 + 4.4, sx, sy)
    p = p + Location((-9, 9, z0 + 6)) * Box(14, 4, 7) + zc(1.6, z0 + 2.6, z0 + 11, -15, 11)   # contacts and post
    p = p + Location((-2, 10, z0 + 7)) * Box(3, 5, 5)                 # fixed contact
    return _l(p, spec)


def capacitor(spec) -> Part:
    """Item 6: capacitor on the moving plate."""
    d = spec.nom("diameter")
    z0 = G.BODY_Z + 16.5
    c = Location((10, -12, z0 + d / 2)) * Cylinder(d / 2, 18, rotation=(90, 0, 0))
    return _l(c + Location((10, -2, z0 + 1)) * Box(5, 4, 2), spec)


def cam_shaft(spec) -> Part:
    """Items 11-14, 19: shaft and action plate, centrifugal weights, the four-lobe cam and
    the offset driving dog on the lower end."""
    z0 = G.BODY_Z
    s = zc(6.3, G.CLAMP_Z - 44, z0 + 12)
    s = s + zc(15.0, z0 + 6, z0 + 7.5)                                # action plate
    for k in range(2):                                                # weights and springs
        s = s + Location((0, 0, z0 + 9)) * Rot(0, 0, 180 * k) * Location((7, 6, 0)) * Box(12, 9, 3)
        s = s + Location((0, 0, z0 + 9)) * Rot(0, 0, 180 * k + 90) * Location((11, 0, 0)) * \
            Cylinder(1.2, 9, rotation=(90, 0, 0))
    lobes = [((6.5 + 1.0 * math.cos(4 * math.radians(t))) * math.cos(math.radians(t)),
              (6.5 + 1.0 * math.cos(4 * math.radians(t))) * math.sin(math.radians(t))) for t in range(0, 360, 6)]
    cam = extrude(Polygon(*lobes, align=None), 15).moved(Location((0, 0, z0 + 11)))
    cam = cam + zc(4.3, z0 + 26, G.CAP_Z + 1)                          # rotor spindle, with the cam screw on top
    dog = zc(8.0, G.CLAMP_Z - 52, G.CLAMP_Z - 42) + Location((1.5, 0, G.CLAMP_Z - 54)) * Box(15, 2.8, 4.5)
    dog = dog - Location((0, 0, G.CLAMP_Z - 46)) * Cylinder(1.4, 18, rotation=(90, 0, 0))
    return _l(s + cam + dog, spec)


# ---- HT leads and plug caps -------------------------------------------------------------------------
PLUG_CAP_ALONG = 44.0            # plug cap seats over the terminal, this far along the plug axis from the seat
PLUG_CAP_LEN = 34.0


def _tower_point(k, rad):
    x, y, _ = polar(rad, G.tower_angle(k), 0)
    return G.to_engine((x, y, G.TOWER_Z))


def ht_lead(cyl):
    def build(spec) -> Part:
        """Lead from its cap boss to the plug cap: straight out of the boss, over the cap
        if the boss faces the block, up the right side of the engine and along to drop
        onto the plug cap from above, on the line of the plug."""
        k = G.FIRING.index(cyl)
        a = G.tower_angle(k)
        seat = G.plug_seats()[cyl - 1]
        pts = [_tower_point(k, CAP_R + BOSS_OUT - 2), _tower_point(k, CAP_R + 20)]
        if math.sin(math.radians(a)) > 0:                             # boss faces the block: arc over the cap
            x, _, _ = polar(CAP_R + 6, a, 0)
            pts.append(G.to_engine((x, -10.0, G.CAP_Z + G.CAP_H + 24)))
        bx = G.BOSS_TOP[0] + 30.0 * math.cos(math.radians(a))
        ly, lz = -128.0 - 5.0 * k, 34.0 + 5.0 * k                       # run along under the plug caps
        pts.append((bx, ly, lz))
        if abs(seat[0] - bx) > 30:
            pts.append((seat[0] - math.copysign(24.0, seat[0] - bx), ly, lz))
        pts.append(G.plug_point(seat, PLUG_CAP_ALONG + PLUG_CAP_LEN + 26))
        pts.append(G.plug_point(seat, PLUG_CAP_ALONG + PLUG_CAP_LEN - 4))
        return _l(_rod(pts, spec.nom("diameter") / 2, 16.0), spec)
    return build


def plug_cap(spec) -> Part:
    """Straight moulded suppressor cap over the plug terminal, ribbed for grip; built along
    +Z from the terminal seat."""
    L = PLUG_CAP_LEN
    prof = [(0, 0), (8.0, 0), (8.0, 4), (9.0, 6), (9.0, 9), (8.0, 11), (8.0, L - 12), (6.0, L - 4), (4.5, L),
            (0, L)]
    c = Sh.revolved(prof)
    c = c - zc(4.2, -1, 13)
    for z in (16.0, 20.0, 24.0):
        c = c - (Sh.revolved([(7.2, z), (8.5, z), (8.5, z + 1.6), (7.2, z + 1.6)]))
    return _l(c, spec)


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


PARTS = {
    "ignition.distributor.housing": {"build": housing},
    "ignition.distributor.drive-shaft": {"build": drive_shaft},
    "ignition.distributor.housing-bolt": {"build": bolt("5/16")},
    "ignition.distributor.housing-washer": {"build": washer},
    "ignition.distributor.clamp-plate": {"build": clamp_plate},
    "ignition.distributor.pinch-bolt": {"build": pinch_bolt},
    "ignition.distributor.clamp-bolt": {"build": bolt("1/4")},
    "ignition.distributor.body": {"build": body},
    "ignition.distributor.vacuum-unit": {"build": vacuum_unit},
    "ignition.distributor.cap-clip": {"build": cap_clip},
    "ignition.distributor.cap": {"build": cap},
    "ignition.distributor.brush": {"build": brush},
    "ignition.distributor.rotor": {"build": rotor},
    "ignition.distributor.baseplate": {"build": baseplate},
    "ignition.distributor.capacitor": {"build": capacitor},
    "ignition.distributor.shaft": {"build": cam_shaft},
    "ignition.distributor.ht-lead-1": {"build": ht_lead(1)},
    "ignition.distributor.ht-lead-2": {"build": ht_lead(2)},
    "ignition.distributor.ht-lead-3": {"build": ht_lead(3)},
    "ignition.distributor.ht-lead-4": {"build": ht_lead(4)},
    "ignition.distributor.plug-cap": {"build": plug_cap},
}
