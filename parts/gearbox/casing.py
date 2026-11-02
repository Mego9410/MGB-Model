"""Gearbox casing and its covers, early three-synchro box for an overdrive car (1963).
Haynes Ch 6: Fig 6.3 (exploded, early type, printed p114-115) items 1-17, 26-29, 156-160;
Sec 4 paras 6-11 and Sec 7 (p113, p119, p123); photos 4.19, 4.20a, 4.22, 7.1, 7.7.

Everything is built in the gearbox frame of mgb.gearbox_layout (GF): local z runs rearward
along the mainshaft from the casing front face (d), local x is up and local y the car's
left. Car datums (rear plate bolt holes, starter aperture, clutch lever, slave pad) are
turned into that frame with G.to_local.

Forms (Fig 6.3 item 1 and the photos; owners' photos of bare B-series cases):
- casing: one casting with the bellhousing. Bell: a deep, nearly cylindrical shell from the
  bolting flange (round, with two ears at the top for the upper bolts and a lobe round the
  starter aperture) to a flat back wall, its top sloping down to the box; a pocket for the
  starter pinion; six external ribs; the right-hand wall drops in to a flat face where the
  withdrawal lever leaves through an oval opening, and carries the slave cylinder pad on a
  web. Box: walls with a machined face and an opening for the side cover on the left, a
  sump under the laygear with the drain plug boss, a dipstick boss, bosses for the front
  cover studs, the layshaft and reverse shaft bores, the selector rod bores, and a rear face
  carrying the centre bearing housing, the selector rod block and the adaptor studs.
- front cover: cast plate over the first motion shaft bearing, the layshaft end (with the
  step that stops the layshaft turning) and the selector rod ends; a sleeve forward with the
  oil seal; an arm on the right with the two lugs the clutch withdrawal lever pivots between.
- side cover: pressed steel plate with a raised panel and a cross swage (photo 4.20a).
- adaptor ("gearbox extension" on overdrive cars, Sec 4 para 4, Sec 11 para 3): short cast
  housing from the casing rear face to the overdrive joint face, open on top for the remote
  control housing, with the eight overdrive studs on its rear flange.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Face, Location, Part, Plane, Polygon, Rot, Wire, extrude, loft

from mgb import fasteners as F, gearbox_layout as G, probes, shapes as Sh
from mgb.poly2d import ccw, along, circle_pts, clip_top, grow, hull, inset, radial, rounded
from parts.engine.block import plates as P

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
IN = 25.4


def _l(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    """Cylinder along local z (fore and aft) at (up x, left y)."""
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def zprism(pts, z0, z1):
    face = Face(Wire.make_polygon([(x, y, 0) for x, y in ccw(pts)], close=True))
    return extrude(face, z1 - z0).moved(Location((0, 0, z0)))


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


# ---- datums in the gearbox frame ---------------------------------------------------------------
BELL_D = G.CASE_FRONT_X - G.BELL_FACE_X          # -160: bell front face (on the rear plate)
FLANGE_T = 12.0
BOSS_L = 18.0                                    # bolt bosses behind the flange (bolt heads seat on their ends)
STARTER_L = (P.STARTER[1] - G.AXIS_Z, P.STARTER[0])           # (up, left) of the starter aperture
STARTER_R = P.STARTER[2]
BELL_HOLES = [(z - G.AXIS_Z, y) for y, z in P._bell_points()]   # (up, left)
PORT = G.to_local(G.LEVER_PORT)                  # lever opening centre (up, left, d)
LDIR = (0.0, G.LEVER_DIR[1], -G.LEVER_DIR[0])    # lever direction in the local frame
PIV = G.to_local(G.PIVOT)
SLAVE = G.to_local((G.SLAVE_PAD_X, G.SLAVE_Y, G.SLAVE_Z))      # pad rear face centre
SLAVE_PAD_T = 16.0
TOP_SLOPE = (118.0, 50.0 / 60.0)                 # bell top: up = 118 - slope * d (d < 0)

# case section (up, left), outside of the walls
CASE_OUTLINE = [(G.CASE_TOP, -58.0), (G.CASE_TOP, 80.0), (G.CASE_TOP - 14.0, G.CASE_LEFT), (-66.0, G.CASE_LEFT),
                (G.CASE_BOTTOM + 12.0, 60.0), (G.CASE_BOTTOM, 44.0), (G.CASE_BOTTOM, -44.0),
                (G.CASE_BOTTOM + 14.0, -60.0), (-62.0, G.CASE_RIGHT), (70.0, G.CASE_RIGHT),
                (G.CASE_TOP - 8.0, -74.0)]
WALL = 7.0
SIDE_FACE = G.CASE_LEFT + 3.0                    # machined face round the side cover opening
SC_OPEN = (G.SIDE_COVER_UP[0], G.SIDE_COVER_UP[1], G.SIDE_COVER_D[0], G.SIDE_COVER_D[1])   # up0, up1, d0, d1
SC_FLANGE = 14.0
DRAIN = (G.CASE_BOTTOM, -20.0, 150.0)            # drain plug: bottom of the sump, ahead of first gear
DIP_HOLE = (G.CASE_TOP, 30.0, 26.0)              # Welch plug (item 5) closing the casting hole in the top, front
LAY_HOLE_R = 8.6
REV_D = G.REV_SHAFT_D                            # reverse shaft: front boss to rear wall
REV_SCREW_D = REV_D[0] + 7.0                             # reverse shaft locating screw (item 91), from above the boss
CTR_HOUSING_R, CTR_FLANGE_R, CTR_FLANGE_T = 46.0, 52.0, 4.0
HOUSING_PEG_R = 48.0
FMS_BRG_R = 40.0


def _rods():
    return [(G.ROD_UP, y) for y in G.ROD_LEFT.values()]


# front cover outline: hull round the bearing, the layshaft end and the selector rod ends, plus
# the arm for the withdrawal lever pivot
FC_CIRCLES = [(0.0, 0.0, 58.0), (G.LAY_UP, 0.0, 22.0)] + [(u, l, 15.0) for u, l in _rods()]
FC_OUTLINE = hull([p for cx, cy, r in FC_CIRCLES for p in circle_pts(cx, cy, r, 36)])
def _fc_studs(n=8):
    """Eight studs round the cover, on a path 9.5 mm in from its edge, kept clear of the
    selector rod bores, the layshaft and the bearing (D)."""
    keep_off = [(u, l, 13.0) for u, l in _rods()] + [(G.LAY_UP, 0.0, 15.0), (0.0, 0.0, 47.0)]
    cand = [p for p in along(inset(FC_OUTLINE, 9.5), [k / 600 for k in range(600)])
            if all(math.dist(p, (u, l)) > r for u, l, r in keep_off)]
    out = []
    step = len(cand) / n
    for k in range(n):
        out.append(cand[int(k * step + step / 2) % len(cand)])
    return out


FC_STUDS = _fc_studs()
FC_T = 10.0
SLEEVE = (-28.0, -FC_T)                          # front cover sleeve, d
SLEEVE_R = (21.5, 27.0)

# rear face of the casing: studs for the adaptor, the detent block dowels
def _rear_studs():
    """Studs round the rear face for the adaptor, clear of the detent block and its screws."""
    pts = along(inset(CASE_OUTLINE, 10.0), [0.06 + k / 9 for k in range(9)])
    u0, u1, l0, l1 = BLOCK
    return [(u, l) for u, l in pts if not (u0 - 12.0 < u < u1 + 14.0 and l0 - 12.0 < l < l1 + 12.0)]

BLOCK = (G.ROD_UP - 14.0, G.ROD_UP + 16.0, min(G.ROD_LEFT.values()) - 13.0, max(G.ROD_LEFT.values()) + 13.0)
BLOCK_T = 18.0
REAR_STUDS = _rear_studs()
BLOCK_DOWELS = [(G.ROD_UP + 9.0, min(G.ROD_LEFT.values()) - 7.0), (G.ROD_UP + 9.0, max(G.ROD_LEFT.values()) + 7.0)]
BLOCK_SCREWS = [(G.ROD_UP + 10.0, (G.ROD_LEFT["first-second"] + G.ROD_LEFT["third-fourth"]) / 2),
                (G.ROD_UP + 10.0, (G.ROD_LEFT["third-fourth"] + G.ROD_LEFT["reverse"]) / 2)]

# side cover bolts: round the opening flange
SC_POLY = [(SC_OPEN[0] - SC_FLANGE, SC_OPEN[2] - SC_FLANGE), (SC_OPEN[1] + SC_FLANGE, SC_OPEN[2] - SC_FLANGE),
           (SC_OPEN[1] + SC_FLANGE, SC_OPEN[3] + SC_FLANGE), (SC_OPEN[0] - SC_FLANGE, SC_OPEN[3] + SC_FLANGE)]
SC_BOLTS = along([(SC_OPEN[0] - 7, SC_OPEN[2] - 7), (SC_OPEN[1] + 7, SC_OPEN[2] - 7),
                  (SC_OPEN[1] + 7, SC_OPEN[3] + 7), (SC_OPEN[0] - 7, SC_OPEN[3] + 7)],
                 [k / 10 for k in range(10)])     # (up, d)
SC_FIBRE = 7                                     # this bolt passes into the case below the oil: fibre washer (item 17)
SC_SCREW = (40.0, 120.0)                         # item 18: screw into the internal web, top middle

# adaptor (overdrive "gearbox extension")
AD_D0, AD_D1 = G.CASE_LEN + G.JOINT_T, G.AD_END
AD_TOP = 100.0                                   # top face the remote control housing bolts to
AD_TOP_OPEN = (-36.0, 76.0, AD_D0 + 8.0, AD_D1 - 18.0)   # left0, left1, d0, d1 of the opening under the remote housing
AD_PAD = (-56.0, 96.0)
AD_REAR_R = 92.0
AD_TOP_BOLTS = [(-47.0, AD_D0 + 10.0), (87.0, AD_D0 + 10.0), (-47.0, AD_D1 - 12.0), (87.0, AD_D1 - 12.0)]   # (left, d)
AD_DOWEL = (60.0, AD_D0 + 10.0)


def _bell_shell():
    d0 = BELL_D
    # the shell stays inside the bolt circle so the bolt heads clear it; ring gear 154 mm radius
    outer = Sh.revolved([(0, d0 + FLANGE_T - 1), (163.0, d0 + FLANGE_T - 1), (162.0, -110.0), (160.0, -60.0),
                         (158.0, -24.0), (157.5, -4.0), (150.0, 9.0), (0, 9.0)])
    inner = Sh.revolved([(0, d0 - 1), (157.0, d0 - 1), (156.5, -115.0), (154.0, -60.0), (151.5, -24.0),
                         (150.5, -6.0), (146.0, 0.0), (0, 0.0)])
    # sloping top: everything above a plane up = 118 - s d
    s = TOP_SLOPE[1]
    ang = math.degrees(math.atan(s))
    cut_o = Location((TOP_SLOPE[0], 0, 0)) * Rot(0, -ang, 0) * Box(1000, 1000, 1000, align=(Align.MIN, Align.CENTER, Align.CENTER))
    cut_i = Location((TOP_SLOPE[0] - WALL / math.cos(math.radians(ang)), 0, 0)) * Rot(0, -ang, 0) * \
        Box(1000, 1000, 1000, align=(Align.MIN, Align.CENTER, Align.CENTER))
    return outer - cut_o, inner - cut_i


def _flange_outline():
    """Bell flange (up, left): round, an ear round each upper bolt, a lobe round the starter."""
    pts = circle_pts(0, 0, 180.0, 90)
    top = [p for p in pts if p[0] < 150.0]
    ears = [p for u, l in BELL_HOLES[-2:] for p in circle_pts(u, l, 15.0, 18)]
    return top, ears


def _starter_pocket():
    u, l = STARTER_L
    o = zc(STARTER_R + 7.0, BELL_D, BELL_D + 66.0, u, l)
    o = Sh.revolved([(0, BELL_D), (STARTER_R + 7.0, BELL_D), (STARTER_R + 7.0, BELL_D + 60.0),
                     (STARTER_R - 4.0, BELL_D + 70.0), (0, BELL_D + 70.0)]).moved(Location((u, l, 0)))
    i = Sh.revolved([(0, BELL_D - 1), (STARTER_R + 0.5, BELL_D - 1), (STARTER_R + 0.5, BELL_D + 58.0),
                     (STARTER_R - 8.0, BELL_D + 64.0), (0, BELL_D + 64.0)]).moved(Location((u, l, 0)))
    return o, i


def _ribs():
    """Six tapering ribs down the bell from the flange to the back wall."""
    out = None
    for a in (20.0, 90.0, 130.0, 165.0, 280.0, 340.0):           # clear of the bolt heads and the starter pocket
        rib = Polygon((150.0, BELL_D + FLANGE_T - 2), (179.0, BELL_D + FLANGE_T - 2), (165.0, -62.0),
                      (157.0, -14.0), (150.0, -14.0), align=None)
        r = extrude(Plane.XZ * rib, 3.0, both=True)
        r = Rot(0, 0, a) * r
        out = r if out is None else out + r
    return out


def _case_body():
    outer = zprism(CASE_OUTLINE, 0.0, G.CASE_LEN)
    inner = zprism(inset(CASE_OUTLINE, WALL), G.FRONT_WALL, G.CASE_LEN - G.REAR_WALL)
    return outer, inner


def _port_cutter(extra=0.0):
    """Oval opening for the withdrawal lever, along the lever direction through the wall."""
    from build123d import Ellipse
    pl = Plane(origin=(PORT[0], PORT[1], PORT[2]), x_dir=(1, 0, 0), z_dir=LDIR)
    return extrude(pl * Ellipse(22.0 + extra, 12.0 + extra), 40.0, both=True)


def _port_pad():
    """Flat face round the opening the dust cover flange seats on (normal along the lever)."""
    pl = Plane(origin=(PORT[0], PORT[1], PORT[2]), x_dir=(1, 0, 0), z_dir=LDIR)
    from build123d import Rectangle
    return extrude(pl * Rectangle(70.0, 42.0), -12.0)


def _port_spotface():
    """Wall standing proud of the dust cover's seat round the opening is faced off flat."""
    from build123d import Rectangle
    pl = Plane(origin=(PORT[0], PORT[1], PORT[2]), x_dir=(1, 0, 0), z_dir=LDIR)
    return extrude(pl * Rectangle(66.0, 40.0), 15.0)


def _slave_pad():
    u, l, d = SLAVE
    t = SLAVE_PAD_T
    dz = G.SLAVE_BOLT_DZ
    prof = [(-dz - 10, l - 16), (dz + 10, l - 16), (dz + 10, l + 14), (18, l + 40), (-18, l + 40), (-dz - 10, l + 14)]
    pad = zprism(prof, d - t, d)
    for s in (-1, 1):
        pad = pad + zc(10.0, d - t, d, s * dz, l)
    # web back to the bell wall, and a rib under it
    for s in (-1, 1):                                                  # webs above and below the cylinder
        pad = pad + box(s * 19.0 - 3.0, s * 19.0 + 3.0, l + 12.0, -150.0, d - t - 22.0, d)
        pad = pad + box(s * 26.0 - 3.0, s * 26.0 + 3.0, l + 6.0, -152.0, d - t, d)
    return pad


def _slave_pad_holes():
    u, l, d = SLAVE
    h = zc(G.SLAVE_BORE_IN_PAD / 2, d - SLAVE_PAD_T - 5, d + 30, 0.0, l)
    for s in (-1, 1):
        h = h + zc(3.98, d - SLAVE_PAD_T - 1, d + 1, s * G.SLAVE_BOLT_DZ, l)    # 5/16 UNF tapped
    return h


def casing(spec) -> Part:
    bell_o, bell_i = _bell_shell()
    top, ears = _flange_outline()
    flange = zprism(top, BELL_D, BELL_D + FLANGE_T)
    for u, l in BELL_HOLES[-2:]:                                 # top ears with their deep bosses
        flange = flange + zprism(hull(circle_pts(u, l, 15.0, 18) + [(u - 40, l * 0.75), (u - 30, l * 0.95)]),
                                 BELL_D, BELL_D + FLANGE_T)
        flange = flange + zc(11.0, BELL_D, BELL_D + 46.0, u, l)
    su, sl = STARTER_L
    flange = flange + zc(STARTER_R + 18.0, BELL_D, BELL_D + FLANGE_T, su, sl)
    for u, l in BELL_HOLES[:-2]:                                 # bolt bosses behind the flange, gusseted to the shell
        flange = flange + zc(11.0, BELL_D, BELL_D + BOSS_L, u, l)
        a = math.atan2(l, u)
        flange = flange + Location((158.5 * math.cos(a), 158.5 * math.sin(a), BELL_D)) * Rot(0, 0, math.degrees(a)) * \
            Box(14.0, 6.0, BOSS_L, align=(Align.MIN, Align.CENTER, Align.MIN))
    pk_o, pk_i = _starter_pocket()
    case_o, case_i = _case_body()
    c = bell_o + flange + pk_o + _ribs() + case_o + _port_pad() + _slave_pad()
    # dipstick boss and Welch plug boss on top, drain boss under, front cover stud bosses inside the bell
    c = c + Location((DIP_HOLE[0] - 2, DIP_HOLE[1], DIP_HOLE[2])) * Rot(0, 90, 0) * Cylinder(17.0, 10.0)
    c = c + Location((DRAIN[0] + 3, DRAIN[1], DRAIN[2])) * Rot(0, 90, 0) * Cylinder(16.0, 12.0)
    # side cover machined face, its flange round the opening
    sc = [(u, l) for u, l in SC_POLY]
    c = c + extrude(Plane.XZ.offset(-SIDE_FACE) * Polygon(*[(u, d) for u, d in sc], align=None), SIDE_FACE - G.CASE_LEFT + 2)
    # external stiffening ribs on the right-hand wall and the sump
    for d in (60.0, 120.0, 180.0):
        c = c + box(-58.0, 66.0, G.CASE_RIGHT - 4.0, G.CASE_RIGHT + 1.0, d - 3.0, d + 3.0)
        c = c + box(G.CASE_BOTTOM - 4.0, G.CASE_BOTTOM + 1.0, -40.0, 40.0, d - 3.0, d + 3.0)
    # rear face flange (machined face for the adaptor)
    c = c + zprism(grow(CASE_OUTLINE, 6.0), G.CASE_LEN - 12.0, G.CASE_LEN)
    # ---- cavities ----
    c = c - bell_i - pk_i - case_i
    # side cover opening
    c = c - box(SC_OPEN[0], SC_OPEN[1], G.CASE_LEFT - WALL - 2, SIDE_FACE + 5, SC_OPEN[2], SC_OPEN[3])
    # front wall: bearing bore, layshaft, rod bores; rear wall: bearing housing, layshaft, rods, reverse shaft
    c = c - zc(FMS_BRG_R, -5.0, G.FRONT_WALL + 1)
    c = c - zc(LAY_HOLE_R, -5.0, G.CASE_LEN + 5, G.LAY_UP, 0.0)
    for u, l in _rods():
        c = c - zc(G.ROD_D / 2 + 0.1, -5.0, G.CASE_LEN + 5, u, l)
    c = c + zc(CTR_FLANGE_R - 4.0, G.CTR_BRG[0] + 0.5, G.CASE_LEN - 1.0)          # boss for the bearing housing
    c = c + zc(14.0, G.LAY_ENDS[1] + 4.1, G.CASE_LEN - 1.0, G.LAY_UP, 0.0)       # layshaft rear boss
    c = c - zc(LAY_HOLE_R, G.LAY_ENDS[1], G.CASE_LEN + 5, G.LAY_UP, 0.0)
    c = c - zc(CTR_HOUSING_R, G.CTR_BRG[0] - 1.0, G.CASE_LEN + 1)
    c = c - zc(CTR_FLANGE_R + 0.5, G.CASE_LEN - CTR_FLANGE_T, G.CASE_LEN + 1)
    c = c - zc(2.05, G.CASE_LEN - 8.5, G.CASE_LEN + 1, HOUSING_PEG_R, 0.0)         # hole for the housing peg
    c = c - box(G.LAY_UP + 15.5, G.LAY_UP + 20.5, -2.5, 2.5, G.FRONT_WALL - 4.0, G.FRONT_WALL + 1.0)   # front thrust washer tag
    rv = 0.625 * IN / 2
    c = c + zc(14.0, REV_D[0], REV_D[0] + 14.0, G.REV_UP, G.REV_LEFT)       # reverse shaft front boss
    c = c + box(G.REV_UP - 4.0, G.REV_UP + 4.0, G.REV_LEFT, G.CASE_LEFT - 3, REV_D[0], REV_D[0] + 14.0)
    c = c + box(G.CASE_BOTTOM + 2.0, G.REV_UP, G.REV_LEFT - 7.0, G.REV_LEFT + 7.0, REV_D[0] + 2.0, REV_D[0] + 12.0)
    c = c - zc(rv + 0.05, REV_D[0] - 1, G.CASE_LEN + 2, G.REV_UP, G.REV_LEFT)
    c = c - Location((G.REV_UP + 10.0, G.REV_LEFT, REV_SCREW_D)) * Rot(0, 90, 0) * Cylinder(3.2, 22.0)
    # bell holes, starter aperture, lever opening, slave pad
    for u, l in BELL_HOLES:
        c = c - zc(5.2, BELL_D - 1, BELL_D + 60.0, u, l)
    from mgb import electrical_layout as EZ
    for y, z in EZ.starter_bolt_points():                    # P10: tapped holes for the starter's two 3/8 in bolts
        c = c + zc(10.0, BELL_D, BELL_D + FLANGE_T + 4.0, z - G.AXIS_Z, y)
        c = c - zc(4.76, BELL_D - 1, BELL_D + FLANGE_T + 2.0, z - G.AXIS_Z, y)
    c = c - zc(STARTER_R + 7.0, BELL_D - 1, BELL_D + 2.5, su, sl)               # relief for the plate's lip round the aperture
    for y, z in P.REAR_SCREWS_5_16 + P.REAR_SCREWS_3_8:                          # pockets for the plate screw heads
        u, l = z - G.AXIS_Z, y
        if 140.0 < math.hypot(u, l) < 200.0:
            c = c - zc(12.5, BELL_D - 1, BELL_D + 11.0, u, l)
    c = c - _port_cutter() - _slave_pad_holes() - _port_spotface()
    # front cover stud holes (5/16 UNF), rear face studs, detent block dowels and screws
    for u, l in FC_STUDS:                                                        # tapped: drawn at the major diameter
        c = c - zc(3.98, -1.0, 16.0, u, l)
    for u, l in REAR_STUDS:
        c = c - zc(3.98, G.CASE_LEN - 16.0, G.CASE_LEN + 1, u, l)
    for u, l in BLOCK_DOWELS:
        c = c - zc(3.0, G.CASE_LEN - 10.0, G.CASE_LEN + 1, u, l)
    for u, l in BLOCK_SCREWS:
        c = c - zc(3.2, G.CASE_LEN - 14.0, G.CASE_LEN + 1, u, l)
    # side cover tapped holes
    for u, d in SC_BOLTS:
        c = c - Location((u, SIDE_FACE - 14.0, d)) * Rot(-90, 0, 0) * Cylinder(3.2, 26.0, align=BASE)
    # drain plug and plug 5 holes, dipstick-free top on an overdrive car (the dipstick is in the remote)
    c = c - Location((DRAIN[0] - 10, DRAIN[1], DRAIN[2])) * Rot(0, 90, 0) * Cylinder(9.0, 30.0, align=BASE)
    c = c - Location((DIP_HOLE[0] - 20, DIP_HOLE[1], DIP_HOLE[2])) * Rot(0, 90, 0) * Cylinder(11.0, 40.0, align=BASE)
    # machined pad on the left of the case, ahead of the side cover, where the gearbox number is stamped
    c = c + box(56.0, 80.0, G.CASE_LEFT - 1.0, G.CASE_LEFT + 2.0, 6.0, 22.0)
    return _l(c, spec)


# ---- front cover (items 7-11) ------------------------------------------------------------------
def front_cover(spec) -> Part:
    pu, pl, pd = PIV
    c = zprism(FC_OUTLINE, -FC_T, 0.0)
    c = c + zc(SLEEVE_R[1], SLEEVE[0], SLEEVE[1])
    c = c + Sh.revolved([(SLEEVE_R[1] - 0.1, -FC_T - 7.0), (36.0, -FC_T - 7.0), (40.0, -FC_T + 0.1), (SLEEVE_R[1] - 0.1, -FC_T + 0.1)])
    c = c + Sh.revolved([(SLEEVE_R[1], -FC_T - 0.1), (SLEEVE_R[1] + 9.0, -FC_T - 0.1), (SLEEVE_R[1], -FC_T - 9.0)])
    # stud bosses
    for u, l in FC_STUDS:
        c = c + zc(8.0, -FC_T - 2.0, 0.0, u, l)
    # pivot lugs: two horizontal plates joined to the cover by a web on the right
    z0, z1 = G.PIVOT_LUG_Z, G.PIVOT_LUG_Z + G.PIVOT_LUG_T
    for lo, hi in ((z0, z1), (-z1, -z0)):
        lug = box(lo, hi, pl - 14.0, pl + 14.0, pd - 14.0, -FC_T + 1.0) + \
            Location((lo, pl, pd)) * Rot(0, 90, 0) * Cylinder(14.0, hi - lo, align=BASE)
        c = c + lug
    c = c + box(-z1, z1, pl - 14.0, pl - 6.0, pd + 2.0, -FC_T + 1.0)          # web down the outer edge
    c = c + box(-z1, z1, pl - 14.0, pl + 18.0, -FC_T - 6.0, -FC_T + 1.0)     # root on the flange
    # holes
    c = c - zc(SLEEVE_R[0], SLEEVE[0] - 1, 1.0)                               # bore and oil seal recess
    c = c - zc(spec.nom("seal_bore") / 2, SLEEVE[0] - 1, SLEEVE[0] + 9.0)
    c = c - zc(FMS_BRG_R + 4.0, -4.0, 1.0)                                    # recess over the bearing, its ring and shims
    c = c - zc(29.0, -FC_T - 6.0, 0.5)                                        # room for the shaft nut
    for u, l in FC_STUDS:
        c = c - zc(4.2, -FC_T - 3, 1.0, u, l)
    c = c - Location((pu - 40, pl, pd)) * Rot(0, 90, 0) * Cylinder(5.4, 80.0, align=BASE)      # pivot bolt hole
    c = c - box(-z0, z0, pl - 20.0, pl + 30.0, pd - 20.0, pd + 20.0)          # gap for the lever boss
    # step that holds the layshaft from turning: a half-moon land behind the shaft end
    c = c - zc(LAY_HOLE_R + 0.6, -2.5, 1.0, G.LAY_UP, 0.0)
    c = c + box(G.LAY_UP - LAY_HOLE_R, G.LAY_UP - 1.5, -LAY_HOLE_R, LAY_HOLE_R, -2.5, -0.01)
    return _l(c, spec)


def front_cover_gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = zprism(FC_OUTLINE, 0.0, t)
    g = g - zc(FMS_BRG_R + 4.0, -1, t + 1)
    g = g - zc(LAY_HOLE_R, -1, t + 1, G.LAY_UP, 0.0)
    for u, l in FC_STUDS:
        g = g - zc(4.2, -1, t + 1, u, l)
    return _l(g, spec)


def oil_seal(spec) -> Part:
    od, id_, w = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("width")
    s = Sh.revolved([(od / 2 - 2.0, 0), (od / 2, 0), (od / 2, w), (id_ / 2 + 3.0, w), (id_ / 2 + 3.0, w - 1.2),
                     (od / 2 - 2.0, w - 1.2)])
    s = s + Sh.revolved([(id_ / 2, 1.5), (id_ / 2 + 4.0, 0.8), (od / 2 - 2.0, 0.8), (od / 2 - 2.0, w - 1.2),
                         (id_ / 2 + 4.0, w - 1.2), (id_ / 2 + 1.0, 5.0)])
    s = s + Sh.revolved([(id_ / 2 + 4.2, 3.0), (id_ / 2 + 6.4, 3.0), (id_ / 2 + 6.4, 5.2), (id_ / 2 + 4.2, 5.2)])  # garter spring
    return _l(s, spec)


def stud(size, length_in, thread_in=None):
    d = F.THREADS[size][0] * IN
    L = length_in * IN
    s = Sh.chamfered_cyl(d, L, 0.6)
    s = s - Location((0, 0, L * 0.5)) * Box(d * 2, d * 2, 0.4)  # thread run-out line
    return s


def front_stud(spec):
    return _l(stud("5/16", spec.nom("length") / IN), spec)


def rear_stud(spec):
    return _l(stud("5/16", spec.nom("length") / IN), spec)


def od_stud(spec):
    return _l(stud("1/4", spec.nom("length") / IN), spec)


def nut(size):
    def b(spec):
        return _l(F.hex_nut(size), spec)
    return b


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) - Location(((od + id_) / 4, 0, t / 2)) * Rot(0, 0, 20) * Box(od, 1.2, t + 1)
    return _l(w, spec)


def plain_washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def bolt(size, series="UNF"):
    def b(spec):
        return _l(F.hex_bolt(size, spec.nom("length") / IN, series=series), spec)
    return b


# ---- side cover (items 12-19) --------------------------------------------------------------------
def side_cover(spec) -> Part:
    """Pressed plate, built lying on the casing's left machined face (local y outward)."""
    t = spec.nom("thickness")
    u0, u1, d0, d1 = SC_OPEN
    out = [(u0 - SC_FLANGE + 2, d0 - SC_FLANGE + 2), (u1 + SC_FLANGE - 2, d0 - SC_FLANGE + 2),
           (u1 + SC_FLANGE - 2, d1 + SC_FLANGE - 2), (u0 - SC_FLANGE + 2, d1 + SC_FLANGE - 2)]
    out = grow(inset(out, 8.0), 8.0)

    def slab(poly, y0, y1):
        return Location((0, y0, 0)) * extrude(Plane.XZ * Polygon(*poly, align=None), -(y1 - y0))
    pl = slab(out, SIDE_FACE, SIDE_FACE + t)
    raised = grow(inset([(u0 + 4, d0 + 4), (u1 - 4, d0 + 4), (u1 - 4, d1 - 4), (u0 + 4, d1 - 4)], 10.0), 10.0)
    pl = pl + slab(raised, SIDE_FACE + t - 0.01, SIDE_FACE + t + 4.0)
    # cross swage on the raised panel
    for a in (1, -1):
        L = math.hypot(u1 - u0 - 20, d1 - d0 - 20)
        ang = math.degrees(math.atan2(a * (u1 - u0 - 20), d1 - d0 - 20))
        sw = Location(((u0 + u1) / 2, SIDE_FACE + t + 4.0, (d0 + d1) / 2)) * Rot(0, ang, 0) * \
            Box(5.0, 3.0, L - 10, align=(Align.CENTER, Align.MIN, Align.CENTER))
        pl = pl + sw
    for u, d in SC_BOLTS:
        pl = pl - Location((u, SIDE_FACE - 1, d)) * Rot(-90, 0, 0) * Cylinder(4.2, t + 3, align=BASE)
    u, d = SC_SCREW
    pl = pl - Location((u, SIDE_FACE - 1, d)) * Rot(-90, 0, 0) * Cylinder(4.2, t + 8, align=BASE)
    return _l(pl, spec)


def side_cover_gasket(spec) -> Part:
    t = spec.nom("thickness")
    u0, u1, d0, d1 = SC_OPEN
    out = grow(inset(SC_POLY, 8.0), 6.0)
    g = Location((0, SIDE_FACE, 0)) * extrude(Plane.XZ * Polygon(*out, align=None), -t)
    g = g - box(u0, u1, SIDE_FACE - 1, SIDE_FACE + t + 1, d0, d1)
    for u, d in SC_BOLTS:
        g = g - Location((u, SIDE_FACE - 1, d)) * Rot(-90, 0, 0) * Cylinder(4.2, t + 3, align=BASE)
    return _l(g, spec)


def fibre_washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def slotted_screw(spec) -> Part:
    d = 5 / 16 * IN
    L = spec.nom("length")
    s = Sh.revolved([(0, -4.0), (d * 0.85, -4.0), (d * 0.95, -1.5), (d * 0.85, 0.0), (d / 2, 0.0), (d / 2, L), (0, L)])
    s = s - Location((0, 0, -4.0)) * Box(1.6, 20, 3.0)
    return _l(s, spec)


# ---- plugs (items 5, 6) ---------------------------------------------------------------------------
def welch_plug(spec) -> Part:
    d = spec.nom("diameter")
    p = Sh.revolved([(0, 0), (d / 2, 0), (d / 2, 1.5), (d / 2 - 2.0, 2.2), (0, 3.2)])
    return _l(p, spec)


def drain_plug(spec) -> Part:
    """Taper plug with a hex socket (MGOC 2K5830), threaded into the sump boss."""
    d = spec.nom("thread_diameter")
    L = spec.nom("length")
    p = Sh.revolved([(0, -3.0), (d / 2 + 3.0, -3.0), (d / 2 + 3.0, -0.6), (d / 2 + 2.4, 0), (d / 2, 0), (d / 2 - 0.4, L),
                     (0, L)])
    from build123d import RegularPolygon
    sock = extrude(RegularPolygon(5.0, 6), 8.0).moved(Location((0, 0, -3.5)))
    return _l(p - sock, spec)


def dowel(spec) -> Part:
    return _l(Sh.chamfered_cyl(spec.nom("diameter"), spec.nom("length"), 0.5), spec)


# ---- adaptor (overdrive gearbox extension) and its fixings -------------------------------------
def adaptor(spec) -> Part:
    front = clip_top(inset(CASE_OUTLINE, 1.0), AD_TOP)
    waist = clip_top(hull(inset(CASE_OUTLINE, 10.0) + circle_pts(0, 0, AD_REAR_R - 2.0, 48)), AD_TOP)
    rear = clip_top(hull(circle_pts(0, 0, AD_REAR_R - 6.0, 48) + [(AD_TOP, -48.0), (AD_TOP, 96.0), (40.0, 96.0)]), AD_TOP)
    secs = [Plane.XY.offset(d) * Polygon(*radial(sh, 72), align=None)
            for d, sh in ((AD_D0 + 11.0, front), (AD_D0 + 40.0, waist), (AD_D1 - 9.0, rear))]
    body = loft(secs, ruled=True)
    # front flange on the casing face, rear flange for the overdrive, top pad
    body = body + zprism(grow(CASE_OUTLINE, 5.0), AD_D0, AD_D0 + 12.0)
    body = body + zc(AD_REAR_R + 8.0, AD_D1 - 10.0, AD_D1)
    for a in G.OD_STUD_ANGLES:
        x, y = G.OD_STUD_R * math.cos(math.radians(a)), G.OD_STUD_R * math.sin(math.radians(a))
        body = body + zc(8.0, AD_D1 - 24.0, AD_D1, x, y)
    body = body + box(AD_TOP - 14.0, AD_TOP, AD_PAD[0], AD_PAD[1], AD_D0 + 2.0, AD_D1 - 4.0)
    # interior
    cav = zprism(inset(CASE_OUTLINE, 8.0), AD_D0 - 1, AD_D0 + 30.0)
    cav = cav + zc(AD_REAR_R - 14.0, AD_D0 + 20.0, AD_D1 - 9.0)
    cav = cav + box(-60.0, AD_TOP - 18.0, -40.0, 80.0, AD_D0 - 1, AD_D1 - 9.0)
    body = body - cav
    body = body - zc(G.OD_SPIGOT_R, AD_D1 - 10.0, AD_D1 + 1)                    # overdrive register
    body = body - box(AD_TOP - 30.0, AD_TOP + 1, AD_TOP_OPEN[0], AD_TOP_OPEN[1], AD_TOP_OPEN[2], AD_TOP_OPEN[3])
    # stud holes: casing studs through the front flange, overdrive studs tapped in the rear bosses
    for u, l in REAR_STUDS:
        body = body - zc(4.2, AD_D0 - 1, AD_D0 + 13.0, u, l)
        body = body - zc(9.5, AD_D0 + 12.0, AD_D0 + 40.0, u, l)                  # spot faces for the nuts
    for a in G.OD_STUD_ANGLES:
        x, y = G.OD_STUD_R * math.cos(math.radians(a)), G.OD_STUD_R * math.sin(math.radians(a))
        body = body - zc(3.18, AD_D1 - 22.0, AD_D1 + 1, x, y)
    for l, d in AD_TOP_BOLTS:
        body = body - Location((AD_TOP - 20.0, l, d)) * Rot(0, 90, 0) * Cylinder(3.98, 22.0, align=BASE)
    l, d = AD_DOWEL
    body = body - Location((AD_TOP - 8.0, l, d)) * Rot(0, 90, 0) * Cylinder(3.0, 10.0, align=BASE)
    # oil way to the overdrive pump at the bottom of the rear face
    ou, ol, od = G.to_local(G.OD_OIL_PORT)
    body = body - zc(6.0, AD_D1 - 40.0, AD_D1 + 1, ou, ol)
    return _l(body, spec)


def adaptor_gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = zprism(grow(CASE_OUTLINE, 4.0), 0.0, t)
    g = g - zc(CTR_FLANGE_R - 6.0, -1, t + 1)
    g = g - box(G.ROD_UP - 16.0, G.ROD_UP + 18.0, BLOCK[2] - 2.0, BLOCK[3] + 2.0, -1, t + 1)
    g = g - zc(LAY_HOLE_R + 2, -1, t + 1, G.LAY_UP, 0.0)
    for u, l in REAR_STUDS:
        g = g - zc(4.2, -1, t + 1, u, l)
    return _l(g, spec)


def od_gasket(spec) -> Part:
    """Joint between the adaptor and the overdrive main casing (MGOC 37H1901)."""
    t = spec.nom("thickness")
    g = zc(AD_REAR_R + 6.0, 0.0, t) - zc(G.OD_SPIGOT_R + 1.0, -1, t + 1)
    for a in G.OD_STUD_ANGLES:
        x, y = G.OD_STUD_R * math.cos(math.radians(a)), G.OD_STUD_R * math.sin(math.radians(a))
        g = g - zc(3.6, -1, t + 1, x, y)
    ou, ol, od = G.to_local(G.OD_OIL_PORT)
    g = g - zc(6.5, -1, t + 1, ou, ol)
    return _l(g, spec)


WASHER = {"outside_diameter": lambda p: probes.bbox_size(p, "y"), "thickness": lambda p: probes.bbox_size(p, "z")}   # y: clear of the split

PARTS = {
    "gearbox.casing.casing": {"build": casing},
    "gearbox.casing.front-cover": {"build": front_cover},
    "gearbox.casing.front-cover-gasket": {"build": front_cover_gasket, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.casing.front-oil-seal": {"build": oil_seal, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.casing.front-stud": {"build": front_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.casing.front-nut": {"build": nut("5/16")},
    "gearbox.casing.front-washer": {"build": spring_washer, "probes": WASHER},
    "gearbox.casing.side-cover": {"build": side_cover},
    "gearbox.casing.side-cover-gasket": {"build": side_cover_gasket},
    "gearbox.casing.side-cover-bolt": {"build": bolt("1/4"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.casing.side-cover-washer": {"build": spring_washer, "probes": WASHER},
    "gearbox.casing.plain-washer": {"build": plain_washer, "probes": WASHER},
    "gearbox.casing.fibre-washer": {"build": fibre_washer, "probes": WASHER},
    "gearbox.casing.side-cover-screw": {"build": slotted_screw},
    "gearbox.casing.side-cover-screw-washer": {"build": spring_washer},
    "gearbox.casing.welch-plug": {"build": welch_plug, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.casing.drain-plug": {"build": drain_plug},
    "gearbox.casing.block-dowel": {"build": dowel, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.casing.rear-stud": {"build": rear_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.casing.adaptor": {"build": adaptor},
    "gearbox.casing.adaptor-gasket": {"build": adaptor_gasket},
    "gearbox.casing.adaptor-nut": {"build": nut("5/16")},
    "gearbox.casing.adaptor-washer": {"build": spring_washer, "probes": WASHER},
    "gearbox.casing.od-stud": {"build": od_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.casing.od-stud-long": {"build": od_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.casing.od-gasket": {"build": od_gasket},
    "gearbox.casing.bell-bolt-short": {"build": bolt("3/8"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.casing.bell-bolt-medium": {"build": bolt("3/8"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.casing.bell-bolt-long": {"build": bolt("3/8"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.casing.bell-nut": {"build": nut("3/8")},
    "gearbox.casing.bell-washer": {"build": spring_washer, "probes": WASHER},
}
