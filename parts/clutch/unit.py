"""Borg & Beck 8 in diaphragm spring clutch, early type with the release plate and graphite
bearing: cover assembly, pressure plate, driven plate and their fixings.
Haynes Ch 5: specs printed p106, Sec 4, Fig 5.1 (exploded, early models, p107), Fig 5.2
(section, p108), photos 4.3, 4.11 and 4.12.

Built in the clutch frame (mgb.clutch_layout): local z runs rearward along the crank axis
from the flywheel friction face, local x is up and local y is the car's left. The assembly
places every part with one transform. Angles round the axis are measured from +y (car left)
toward +x (up), the way the flywheel drills its clutch bolts and dowels.

Forms (from Figs 5.1/5.2 and photos 4.3/4.11):
- cover: deep pressed dish with three bolting lobes (two bolts and a dowel each), a skirt
  with windows the pressure plate lugs pass through, a pressed bead on the back wall that
  carries the nine shouldered fulcrum rivets and their two wire rings, the three drive straps
  riveted outside on raised pads, balance holes and the central opening.
- pressure plate: cast ring with its friction face, a fulcrum ridge on the back for the
  diaphragm's outer edge, three drilled lugs for the strap bolts and cast balance lugs.
- diaphragm: dished spring with eighteen fingers; the slots end in round holes on the
  pivot circle where every other one takes a fulcrum rivet.
- release plate: cast disc riding on the finger tips, spigot through the diaphragm with its
  circlip (early models only, Sec 4 para 5), three ears for its retracting straps.
- driven plate: splined hub with its flange, front and rear side plates riveted through
  stop pins, six damper springs in pressed windows, twelve cushion segments and two
  riveted facings, the hub's short end toward the flywheel (Sec 4 para 10).
"""
import math

from build123d import Align, Box, Cylinder, FilletPolyline, Location, Part, Plane, Polygon, Rectangle, Rot, \
    extrude, sweep

from mgb import clutch_layout as K, fasteners as F, probes, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)

# depths in the clutch frame (local z, rearward from the flywheel face)
Z_PP = K.FACE_X - K.PP_FACE                      # 8.0   pressure plate friction face
Z_PP_BACK = Z_PP + K.PP_T                        # 23.5
Z_DIA_OUT = K.FACE_X - K.DIA_X_OUT               # diaphragm mid-plane at its rim
Z_DIA_PIV = K.FACE_X - K.DIA_X_PIVOT
Z_DIA_TIP = K.FACE_X - K.DIA_X_TIP
Z_BACK = K.COVER_DEPTH                           # inside of the cover back wall
T = K.COVER_T
Z_BEAD = Z_BACK - 4.5                            # inside of the pressed bead that carries the rivets
Z_RP0, Z_RP1 = K.FACE_X - K.RP_FRONT, K.FACE_X - K.RP_BACK
Z_MID = K.FACE_X - K.PLATE_MID                   # driven plate mid-plane (4.0)

LUG_ANGLES = [90.0, 210.0, 330.0]                # pressure plate lugs, midway between the cover lobes
LUG_R = 124.0                                    # strap bolt radius
LUG_Z0, LUG_Z1 = 11.5, 20.5                      # lug front and rear faces
STRAP_SWEEP = 15.0                               # drive strap runs back from the lug to its rivet
STRAP_ANCHOR_R = 116.0
CLIP_T, STRAP_T, TAB_T = 1.0, 2.4, 1.0
RIVET_ANGLES = [10.0 + 40.0 * k for k in range(9)]   # fulcrum rivets in every other slot hole
SLOT_ANGLES = [10.0 + 20.0 * k for k in range(18)]
RP_EAR_ANGLES = [30.0, 150.0, 270.0]
RP_STRAP_SWEEP = 0.0                             # radial, between two fulcrum rivets
RP_STRAP_R0, RP_STRAP_R1 = 49.0, 70.0
SPRING_R = 40.0                                   # damper spring pitch radius
SPRING_ANGLES = [60.0 * k for k in range(6)]
STOP_ANGLES = [30.0 + 60.0 * k for k in range(6)]  # stop pins between the springs
STOP_R = 56.0
SEGMENTS = 12
SKIRT_R = 107.5                                   # inside of the cover skirt


def _l(p, spec):
    p.label = spec.id
    return p


def lp(r, deg, z=0.0):
    """Clutch-frame point at radius r and angle deg (from +y toward +x)."""
    a = math.radians(deg)
    return (r * math.sin(a), r * math.cos(a), z)


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def at(r, deg, z, spin=True):
    """Location at a ring point, turned so local +x points radially outward."""
    x, y, _ = lp(r, deg)
    return Location((x, y, z)) * (Rot(0, 0, 90 - deg) if spin else Rot())


def sector(deg, half, z0, z1, r=220.0):
    """Wedge about the axis, centred on deg, +/- half degrees."""
    pts = [(0.0, 0.0)] + [lp(r, deg - half + 2 * half * k / 12)[:2] for k in range(13)]
    return extrude(Polygon(*pts, align=None), z1 - z0, dir=(0, 0, 1)).moved(Location((0, 0, z0)))


def strip(p0, p1, w, t, z):
    """Flat strip of width w and thickness t from p0 to p1 (xy points) lying at depth z."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    c = Location(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z + t / 2)) * Rot(0, 0, math.degrees(math.atan2(dy, dx)))
    end = zc(w / 2, -t / 2, t / 2)
    return c * (Box(L, w, t) + end.moved(Location((L / 2, 0, 0))) + end.moved(Location((-L / 2, 0, 0))))


# ---- cover (Fig 5.1 item 2, Fig 5.2 items 1, 5) -----------------------------------------------------
def cover(spec) -> Part:
    """Pressed cover with the straps, fulcrum rivets and rings (permanent parts of item 2)."""
    hole_r = K.COVER_HOLE_R
    # dish, profile round the sheet: skirt, cone, back wall, pressed bead, central lip
    outer = [(SKIRT_R + T, 0.0), (SKIRT_R + T, 26.0), (100.5, Z_BACK + T), (80.0, Z_BACK + T), (76.0, Z_BEAD + T),
             (hole_r, Z_BEAD + T)]
    inner = [(hole_r, Z_BEAD), (77.0, Z_BEAD), (80.8, Z_BACK), (98.5, Z_BACK), (SKIRT_R, 25.3), (SKIRT_R, 0.0)]
    c = Sh.revolved(outer + inner)
    # three bolting lobes, each a pressed sector: flange on the flywheel, a ramp up to the skirt
    lobe_rev = Sh.revolved([(SKIRT_R + 0.2, 0.0), (138.0, 0.0), (138.0, T + 2.0), (136.0, T + 2.0), (135.5, T),
                            (SKIRT_R + T + 1.5, T), (SKIRT_R + T + 0.2, T + 1.3), (SKIRT_R + 0.2, T + 1.3)])
    for d in K.DOWEL_ANGLES:
        lobe = lobe_rev & sector(d, 33.0, -1, 20)
        c = c + lobe
        for s in (-30.0, 30.0):                                     # cover bolt holes
            x, y, _ = lp(K.BOLT_R, d + s)
            c = c - zc(4.4, -1, 8, x, y)
        x, y, _ = lp(K.BOLT_R, d)                                   # dowel hole
        c = c - zc(3.4, -1, 6, x, y)
        for s in (-15.0, 15.0):                                     # stiffening dimples on the lobe
            x, y, _ = lp(129.0, d + s)
            c = c + zc(2.2, T - 0.1, T + 0.8, x, y)
    # windows for the pressure plate lugs
    for g in LUG_ANGLES:
        c = c - (at(SKIRT_R + 1.0, g, 4.0) * Box(14.0, 30.0, 24.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        # drive strap: raised pad on the skirt, riveted strap out to the lug's bolt
        a_anchor = g - STRAP_SWEEP
        pad = at((SKIRT_R + STRAP_ANCHOR_R + 6.0) / 2, a_anchor, 14.0) * \
            Box(STRAP_ANCHOR_R + 6.0 - SKIRT_R - 0.5, 14.0, LUG_Z1 + CLIP_T - 14.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c = c + pad
        p0, p1 = lp(STRAP_ANCHOR_R, a_anchor)[:2], lp(LUG_R, g)[:2]
        st = strip(p0, p1, 12.0, STRAP_T, LUG_Z1 + CLIP_T)
        st = st - zc(4.2, 0, 40, *p1)                               # strap bolt hole
        c = c + st
        c = c + zc(4.0, LUG_Z1 + CLIP_T + STRAP_T - 0.05, LUG_Z1 + CLIP_T + STRAP_T + 1.6, *p0)   # rivet head
        # oval ventilation slot beside each window, on the side away from the strap
        for s in (22.0,):
            x, y, _ = lp(SKIRT_R, g + s)
            c = c - (Location((x, y, 21.0)) * Rot(0, 0, 90 - g - s) * Rot(0, 90, 0) * Sh.slot_plate(12.0, 6.0, 30.0)
                     .moved(Location((0, 0, -15.0))))
    # balance holes in the back wall (Fig 5.1)
    for k in range(6):
        x, y, _ = lp(92.0, 60.0 * k + 30.0)
        c = c - zc(2.6, Z_BACK - 1, Z_BACK + T + 1, x, y)
    # fulcrum rivets with their buttons on the back, and the two fulcrum rings
    piv_front = Z_DIA_PIV - K.DIA_T / 2
    piv_back = Z_DIA_PIV + K.DIA_T / 2
    for a in RIVET_ANGLES:
        x, y, _ = lp(K.DIA_PIVOT_R, a)
        c = c + zc(3.0, piv_front - 4.6, Z_BEAD + 0.1, x, y)                   # shouldered shank
        c = c + zc(4.4, piv_front - 5.8, piv_front - 3.9, x, y)                 # formed head in front
        c = c + Sh.revolved([(0, 0), (6.0, 0), (5.2, 1.6), (3.0, 2.6), (0, 2.8)]).moved(
            Location((x, y, Z_BEAD + T - 0.1)))                                  # button on the back
    c = c + Sh.revolved([(K.DIA_PIVOT_R - 2.0, piv_back + 0.45), (K.DIA_PIVOT_R + 2.0, piv_back + 0.45),
                         (K.DIA_PIVOT_R + 2.0, Z_BEAD + 0.05), (K.DIA_PIVOT_R - 2.0, Z_BEAD + 0.05)])
    c = c + Sh.revolved([(K.DIA_PIVOT_R - 2.0, piv_front - 3.9), (K.DIA_PIVOT_R + 2.0, piv_front - 3.9),
                         (K.DIA_PIVOT_R + 2.0, piv_front - 0.45), (K.DIA_PIVOT_R - 2.0, piv_front - 0.45)])
    return _l(c, spec)


def diaphragm(spec) -> Part:
    """Fig 5.2 item 9: dished diaphragm spring, eighteen fingers, slot holes on the pivot circle."""
    t = K.DIA_T
    ro, rp, ri = K.DIA_OUT_R, K.DIA_PIVOT_R, K.DIA_IN_R
    mid = [(ro, Z_DIA_OUT), (rp, Z_DIA_PIV), (ri, Z_DIA_TIP)]
    prof = [(r, z - t / 2) for r, z in mid] + [(r, z + t / 2) for r, z in reversed(mid)]
    d = Sh.revolved(prof)
    for a in SLOT_ANGLES:
        d = d - (at(0.0, a, Z_DIA_PIV - 10) * Location(((rp + ri) / 2 - 1.0, 0, 0)) *
                 Box(rp - ri + 2.0, 2.6, 25.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        x, y, _ = lp(rp, a)
        d = d - zc(4.0, Z_DIA_PIV - 10, Z_DIA_PIV + 10, x, y)
        # finger tips rounded off
        for s in (-1, 1):
            x, y, _ = lp(ri + 1.0, a + s * 4.6)
            d = d - zc(1.4, Z_DIA_TIP - 5, Z_DIA_TIP + 5, x, y)
    return _l(d, spec)


def release_plate(spec) -> Part:
    """Fig 5.2 item 7: release plate on the finger tips, the face the graphite bearing runs on,
    spigot through the diaphragm with its circlip groove, and three strap ears."""
    tip_front = Z_DIA_TIP - K.DIA_T / 2
    p = Sh.revolved([(15.5, tip_front - 3.6), (18.6, tip_front - 3.6), (18.6, Z_RP0), (40.0, Z_RP0),
                     (42.0, Z_RP0 + 2.0), (42.0, Z_RP1 - 1.5), (40.5, Z_RP1), (15.5, Z_RP1)])
    p = p - ring(18.0, 19.0, tip_front - 2.6, tip_front - 1.4)       # circlip groove
    p = p - ring(26.0, 34.0, Z_RP1 - 0.6, Z_RP1 + 1)                 # oil groove in the track
    for a in RP_EAR_ANGLES:
        p = p + strip(lp(38.0, a)[:2], lp(RP_STRAP_R0, a)[:2], 12.0, 3.0, Z_BEAD + T + 1.2) - zc(2.0, Z_BEAD, Z_RP1 + 2, *lp(RP_STRAP_R0, a)[:2])
    return _l(p, spec)


def release_plate_circlip(spec) -> Part:
    tip_front = Z_DIA_TIP - K.DIA_T / 2
    c = ring(18.2, 23.0, tip_front - 2.4, tip_front - 1.4) - (at(20.0, 0.0, tip_front - 3) * Box(10, 3.0, 4))
    for s in (-1, 1):                                                # lug holes at the gap
        x, y, _ = lp(22.5, s * 9.0)
        c = c + zc(2.6, tip_front - 2.4, tip_front - 1.4, x, y) - zc(0.9, tip_front - 3, tip_front, x, y)
    return _l(c, spec)


def release_plate_strap(spec) -> Part:
    """Fig 5.2 item 8: spring strap from a release plate ear to the cover bead (built at ear 0)."""
    a = RP_EAR_ANGLES[0]
    p0, p1 = lp(RP_STRAP_R0, a)[:2], lp(RP_STRAP_R1, a + RP_STRAP_SWEEP)[:2]
    z0 = Z_BEAD + T + 0.3
    s = strip(p0, p1, 9.0, 0.8, z0)
    s = s + zc(1.9, z0 + 0.8, Z_BEAD + T + 4.2, *p0) + zc(3.0, Z_BEAD + T + 4.2, Z_BEAD + T + 5.0, *p0)   # through the ear
    s = s + zc(3.0, z0 + 0.8, z0 + 1.6, *p1)                                                        # into the bead
    return _l(s, spec)


# ---- pressure plate and its fixings (Fig 5.1 items 3-6) ---------------------------------------
def pressure_plate(spec) -> Part:
    ro, ri = spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2
    p = Sh.revolved([(ri + 1.0, Z_PP), (ro - 1.0, Z_PP), (ro, Z_PP + 1.0), (ro, Z_PP_BACK - 1.5), (ro - 1.5, Z_PP_BACK),
                     (ri + 3.0, Z_PP_BACK), (ri, Z_PP_BACK - 3.0), (ri, Z_PP + 1.0)])
    rr = K.PP_RIDGE_R
    p = p + Sh.revolved([(rr - 4.5, Z_PP_BACK - 0.1), (rr + 4.5, Z_PP_BACK - 0.1), (rr + 1.6, Z_PP_BACK + K.PP_RIDGE),
                         (rr - 1.6, Z_PP_BACK + K.PP_RIDGE)])
    for g in LUG_ANGLES:                                             # strap bolt lugs
        lug = at(0.0, g, LUG_Z0) * Location(((ro - 4.0 + LUG_R + 8.0) / 2, 0, 0)) * \
            Box(LUG_R + 8.0 - ro + 4.0, 22.0, LUG_Z1 - LUG_Z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        x, y, _ = lp(LUG_R, g)
        p = p + lug + zc(11.0, LUG_Z0, LUG_Z1, x, y)
        p = p - zc(4.0, LUG_Z0 - 1, LUG_Z1 + 1, x, y)
    for k in range(12):                                              # cast balance lugs on the back rim
        a = 15.0 + 30.0 * k
        if any(abs(((a - g + 180) % 360) - 180) < 20 for g in LUG_ANGLES):
            continue
        p = p + at(ro - 5.5, a, Z_PP_BACK - 0.1) * Box(9.0, 13.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return _l(p, spec)


def pressure_plate_clip(spec) -> Part:
    """Fig 5.1 item 5 (Fig 5.2 item 4): retracting clip under the strap bolt, hooked over the
    diaphragm's rim so the plate follows it back. Built at the lug at angle 0 (+y)."""
    z_hook = Z_DIA_OUT + K.DIA_T / 2 + 1.3
    pts = [(LUG_R + 6, LUG_Z1 + CLIP_T / 2), (109.0, LUG_Z1 + CLIP_T / 2), (105.5, Z_PP_BACK + 1.5),
           (97.0, Z_PP_BACK + 1.5), (95.5, z_hook), (88.0, z_hook)]
    path = None
    for rad in (2.0, 1.0, 0.5):
        try:
            path = FilletPolyline(*[(0.0, r, z) for r, z in pts], radius=rad)
            break
        except ValueError:
            continue
    prof = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0), x_dir=(1, 0, 0)) * Rectangle(12.0, CLIP_T)
    c = sweep(prof, path=path)
    c = c - zc(4.2, LUG_Z1 - 1, LUG_Z1 + 3, 0.0, LUG_R)
    return _l(c, spec)


def strap_bolt(spec) -> Part:
    return _l(F.hex_bolt("5/16", spec.nom("length") / 25.4), spec)


def tab_washer(spec) -> Part:
    """Fig 5.1 item 6: tab washer, a tab bent up against a flat of the bolt head and one down
    over the strap edge. Washer face at z = 0, tabs toward +z (the bolt head side)."""
    w = Sh.washer(17.0, 8.4, TAB_T)
    w = w + Location((10.0, 0, TAB_T / 2)) * Box(5.0, 7.0, TAB_T) + Location((7.9, 0, TAB_T + 2.5)) * Box(TAB_T, 7.0, 5.0)
    w = w + Location((0, -7.5, TAB_T / 2)) * Box(6.0, 3.0, TAB_T) + Location((0, -8.6, -1.2)) * Box(6.0, TAB_T, 2.4)
    return _l(w, spec)


def cover_screw(spec) -> Part:
    return _l(F.hex_bolt("5/16", spec.nom("length") / 25.4), spec)


def spring_washer(spec) -> Part:
    """Single-coil spring washer: a split ring with its ends sprung apart."""
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) - Location(((od + id_) / 4, 0, t / 2)) * Rot(0, 0, 20) * Box(od, 1.2, t + 1)
    return _l(w, spec)


# ---- driven plate (Fig 5.1 item 7) -------------------------------------------------------------
def _spline_bore(major_r, minor_r, n, z0, z1):
    pts = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        da = 2 * math.pi / n
        for f, r in ((0.0, minor_r), (0.22, minor_r), (0.3, major_r), (0.7, major_r), (0.78, minor_r)):
            pts.append((r * math.cos(a0 + da * f), r * math.sin(a0 + da * f)))
    return extrude(Polygon(*pts, align=None), z1 - z0, dir=(0, 0, 1)).moved(Location((0, 0, z0)))


def hub(spec) -> Part:
    """Splined hub with its flange; the short end faces the flywheel (Sec 4 para 10)."""
    z0, z1 = K.FACE_X - K.HUB_FRONT, K.FACE_X - K.HUB_REAR
    zf0, zf1 = Z_MID - 0.2, Z_MID + 2.8
    h = Sh.revolved([(10.0, z0), (17.0, z0), (19.0, z0 + 2), (19.0, zf0), (52.0, zf0), (52.0, zf1), (21.0, zf1),
                     (19.0, zf1 + 4), (19.0, z1 - 2), (17.0, z1), (10.0, z1)])
    h = h - _spline_bore(spec.nom("spline_major_diameter") / 2, spec.nom("spline_major_diameter") / 2 - 1.6,
                         int(spec.nom("splines")), z0 - 1, z1 + 1)
    for a in SPRING_ANGLES:                                          # spring windows
        h = h - (at(SPRING_R, a, zf0 - 1) * Box(13.6, 27.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for a in STOP_ANGLES:                                            # notches for the stop pins
        x, y, _ = lp(STOP_R - 3.0, a)
        h = h - zc(5.5, zf0 - 1, zf1 + 1, x, y)
    return _l(h, spec)


def damper_spring(spec) -> Part:
    """One of six damper springs, built along local x (tangential) at the window at angle 0."""
    L, od = spec.nom("length"), spec.nom("outside_diameter")
    s = Sh.coil_spring(spec.nom("wire_diameter"), od, L, 6)
    x, y, _ = lp(SPRING_R, 0.0)
    return _l(Location((x - L / 2, y, Z_MID + 1.3)) * Rot(0, 90, 0) * s, spec)


def _side_plate(r0, r1, z0, t, louver_dir):
    p = ring(r0, r1, z0, z0 + t)
    for a in SPRING_ANGLES:
        win = at(SPRING_R, a, z0 - 1) * Box(13.6, 26.0, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        p = p - win
        # pressed louvres either side of the window, standing out over the spring
        for s in (-1, 1):
            lz = z0 + t if louver_dir > 0 else z0 - 3.0
            p = p + (at(SPRING_R + s * 8.4, a, lz) * Box(3.0, 24.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return p


def carrier(spec) -> Part:
    """Driven plate centre: front side plate with the twelve cushion segments, rear side plate,
    and the stop pins and segment rivets that hold them together."""
    zf0, zf1 = Z_MID - 0.2, Z_MID + 2.8
    front = _side_plate(26.0, 66.0, zf0 - 1.6, 1.6, -1)
    rear = _side_plate(26.0, 60.0, zf1, 1.6, +1)
    c = front + rear
    for a in STOP_ANGLES:                                            # stop pins through the hub notches
        x, y, _ = lp(STOP_R, a)
        c = c + zc(3.0, zf0 - 1.6, zf1 + 1.6, x, y) + zc(4.2, zf0 - 2.6, zf0 - 1.6, x, y) + zc(4.2, zf1 + 1.6, zf1 + 2.6, x, y)
    seg_w = 2 * math.pi * 84.0 / SEGMENTS - 4.0
    for k in range(SEGMENTS):                                       # cushion segments, waved alternately
        a = 360.0 * k / SEGMENTS
        seg = at(0.0, a, Z_MID - 0.4) * Location((83.0, 0, 0)) * Box(36.0, seg_w, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
        wave = at(0.0, a, Z_MID - 0.4) * Location((88.0, 0, 0)) * Box(20.0, seg_w * 0.45, 0.8,
                                                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
        c = c + seg + wave.moved(Location((0, 0, 0.35 if k % 2 else -0.35)))
        x, y, _ = lp(67.5, a)
        c = c + zc(2.0, zf0 - 1.6, Z_MID + 0.5, x, y)               # segment rivet to the side plate
    # facing rivets, heads sunk in the facing counterbores
    for r, n, off in ((91.0, 24, 0.0), (78.0, 12, 15.0)):
        for k in range(n):
            x, y, _ = lp(r, off + 360.0 * k / n)
            c = c + zc(1.6, 1.7, K.PLATE_T - 1.7, x, y)
    return _l(c, spec)


def facing(spec) -> Part:
    """Wound yarn facing, counterbored for the rivets on its friction face (local z = 0)."""
    ro, ri, t = spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2, spec.nom("thickness")
    f = Sh.revolved([(ri, 0.6), (ri + 0.6, 0), (ro - 0.6, 0), (ro, 0.6), (ro, t), (ri, t)])
    for r, n, off in ((91.0, 24, 0.0), (78.0, 12, 15.0)):
        for k in range(n):
            x, y, _ = lp(r, off + 360.0 * k / n)
            f = f - zc(1.7, -1, t + 1, x, y) - zc(3.4, -1, 1.7, x, y)
    return _l(f, spec)


PARTS = {
    "clutch.unit.cover": {"build": cover},
    "clutch.unit.diaphragm-spring": {"build": diaphragm},
    "clutch.unit.release-plate": {"build": release_plate},
    "clutch.unit.release-plate-circlip": {"build": release_plate_circlip},
    "clutch.unit.release-plate-strap": {"build": release_plate_strap},
    "clutch.unit.pressure-plate": {"build": pressure_plate},
    "clutch.unit.pressure-plate-clip": {"build": pressure_plate_clip},
    "clutch.unit.strap-bolt": {"build": strap_bolt},
    "clutch.unit.tab-washer": {"build": tab_washer},
    "clutch.unit.cover-screw": {"build": cover_screw},
    "clutch.unit.spring-washer": {"build": spring_washer},
    "clutch.unit.hub": {"build": hub},
    "clutch.unit.damper-spring": {"build": damper_spring},
    "clutch.unit.carrier": {"build": carrier},
    "clutch.unit.facing": {"build": facing, "probes": {
        "outside_diameter": lambda p: probes.bbox_size(p, "x"),
        "thickness": lambda p: probes.bbox_size(p, "z")}},
}
