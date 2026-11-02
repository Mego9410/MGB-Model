"""Clutch release gear: graphite release bearing and its cup, the two retaining clips, the
withdrawal lever with its bush, pivot bolt, washer and locknut, and the lever dust cover.
Haynes Ch 5: specs printed p106 (graphite MY3D bearing), Sec 7 (p109), Fig 5.1 items 8 and 9
(p107), Fig 5.2 item 6 (p108), photos 7.1a, 7.1b and 7.3 (p110).

The bearing and cup are built in the clutch frame (mgb.clutch_layout; local z rearward from
the flywheel face, x up, y left), like the clutch unit. The lever, its pivot parts and the
dust cover are built in the engine frame at their places from mgb.gearbox_layout.

Forms:
- carbon ring: plain graphite ring with a chamfered running face standing out of its cup
  (Fig 5.2 item 6; photos 7.1a/7.1b).
- cup: pressed steel cup with two lugs at 12 and 6 o'clock carrying trunnion pins the fork
  ends sit on (Fig 5.1 item 8 shows a lug and its pin).
- clips: spring plates turned through 90 deg to free the bearing (Sec 7 para 2; Fig 5.1
  item 9 shows the plate with its hole and bent tail; photo 7.1b shows one each side).
- lever: forged; a boss on the vertical pivot bolt, a half-ring fork round the right of the
  bearing to the two trunnions, and an outer arm through the bellhousing wall to an eye for
  the slave cylinder pushrod.
"""
import math

from build123d import Align, Box, Cylinder, Location, Part, Plane, Rot, extrude, Polygon, scale

from mgb import clutch_layout as K, fasteners as F, gearbox_layout as G, probes, shapes as Sh
from parts.clutch.unit import BASE, at, lp, ring, zc

Z_FACE = K.FACE_X - K.BEARING_FACE               # carbon running face (local z)
Z_CUP0 = K.FACE_X - K.CUP_FRONT
Z_CUP1 = Z_CUP0 + K.CUP_DEPTH
Z_PIN = K.FACE_X - K.TRUNNION_X
PIN_ANGLES = (90.0, 270.0)                       # 12 and 6 o'clock
PX, PY, PZ = G.PIVOT


def _l(p, spec):
    p.label = spec.id
    return p


def carbon(spec) -> Part:
    ro, ri, L = spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2, spec.nom("length")
    c = Sh.revolved([(ri + 1.0, Z_FACE), (ro - 1.0, Z_FACE), (ro, Z_FACE + 1.0), (ro, Z_FACE + L), (ri, Z_FACE + L),
                     (ri, Z_FACE + 1.0)])
    return _l(c, spec)


def cup(spec) -> Part:
    """Pressed cup the carbon is pressed into, with the two trunnion lugs and pins."""
    r = K.CUP_R
    t = 2.2
    c = Sh.revolved([(30.0, Z_CUP1 - t), (r - t, Z_CUP1 - t), (r - t, Z_CUP0), (r, Z_CUP0), (r, Z_CUP1 - 2.0),
                     (r - 2.0, Z_CUP1), (30.0, Z_CUP1)])
    c = c + ring(r - t - 0.1, r - t + 0.6, Z_CUP0, Z_CUP0 + 2.0)       # rolled lip over the carbon
    for a in PIN_ANGLES:
        lug = at(0.0, a, Z_PIN - 7.0) * Location((r - 3.0 + 4.0, 0, 0)) * Box(8.0, 18.0, 14.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c = c + lug
        pin = at(0.0, a, Z_PIN) * Location((K.TRUNNION_R - 4.0, 0, 0)) * Rot(0, 90, 0) * \
            Sh.chamfered_cyl(9.0, 13.0, 0.8).moved(Location((0, 0, -6.5)))
        c = c + pin
    return _l(c, spec)


def clip(spec) -> Part:
    """Fig 5.1 item 9: spring clip over the pin end, its legs gripping the fork end. Built at
    the 12 o'clock pin; the assembly turns it for the 6 o'clock one."""
    t = spec.nom("thickness")
    r0 = K.TRUNNION_R + 4.1                      # on the outer face of the fork end
    plate = at(0.0, 90.0, Z_PIN) * Location((r0 + t / 2, 0, 0)) * Box(t, 15.0, 26.0)
    plate = plate - (at(0.0, 90.0, Z_PIN) * Location((r0, 0, 0)) * Rot(0, 90, 0) * Cylinder(4.7, 4 * t))
    for s in (-1, 1):                            # legs down the fork's front and back faces
        plate = plate + at(0.0, 90.0, Z_PIN + s * (6.0 + t / 2)) * Location((r0 - 3.5, 0, 0)) * Box(7.0, 11.0, t)
    plate = plate + at(0.0, 90.0, Z_PIN + 13.0) * Location((r0 + 3.0, 0, 0)) * Box(6.0, 9.0, t)   # tail to turn it by
    return _l(plate, spec)


# ---- withdrawal lever (Sec 7 para 3) --------------------------------------------------------------
def lever(spec) -> Part:
    w = spec.nom("fork_thickness")
    xr = PX
    # half-ring fork round the right of the bearing, ends past the trunnions
    ann = Cylinder(K.TRUNNION_R + 4.0, w, rotation=(0, 90, 0)) - Cylinder(K.TRUNNION_R - 3.7, w + 2, rotation=(0, 90, 0))
    ann = ann.moved(Location((xr, 0.0, PZ)))
    yoke = ann & Box(w + 2, 80.0, 140.0, align=(Align.CENTER, Align.MAX, Align.CENTER)).moved(Location((xr, 8.0, PZ)))
    for a in (1, -1):                                       # pin holes in the fork ends
        yoke = yoke - Location((xr, 0.0, PZ + a * K.TRUNNION_R)) * Cylinder(4.8, 20)
    # boss on the pivot bolt, and the web joining it to the fork
    boss = Location((PX, PY, PZ)) * Cylinder(G.PIVOT_BOSS_R, 2 * G.PIVOT_LUG_Z - 0.6)
    web = Location((xr, (PY + G.PIVOT_BOSS_R - K.TRUNNION_R) / 2 - 2.0, PZ)) * Box(w, 12.0, 24.0)
    # outer arm out through the wall to the pushrod eye, tapering
    ex, ey, ez = G.LEVER_END
    L = math.hypot(ex - PX, ey - PY)
    ang = math.degrees(math.atan2(ey - PY, ex - PX))
    arm = extrude(Plane.XZ * Polygon((0, -11.0), (L, -10.0), (L, 10.0), (0, 11.0), align=None), 4.5, both=True)
    arm = Location((PX, PY, PZ)) * Rot(0, 0, ang) * arm
    rib = Location((PX, PY, PZ)) * Rot(0, 0, ang) * Location((L * 0.45, 0, 0)) * Box(L * 0.7, 13.0, 4.0)
    eye = Location((ex, ey, ez)) * Cylinder(10.0, 20.0)             # fork end for the pushrod eye
    lv = yoke + boss + web + arm + rib + eye
    lv = lv - Location((PX, PY, PZ)) * Cylinder(spec.nom("bush_bore") / 2, 40.0)
    lv = lv - Location((ex + 5.0, ey, ez)) * Box(30.0, 24.0, 9.0)   # slot open toward the slave cylinder
    lv = lv - Location((ex, ey, ez)) * Cylinder(4.1, 30.0)
    return _l(lv, spec)


def bush(spec) -> Part:
    od, id_ = spec.nom("outside_diameter"), spec.nom("inside_diameter")
    L = 2 * G.PIVOT_LUG_Z - 0.6
    return _l(Sh.tube(od, id_, L).moved(Location((PX, PY, PZ - L / 2))), spec)


def pivot_bolt(spec) -> Part:
    """Pivot bolt, head on the upper lug, down through the lugs and the bush."""
    b = F.hex_bolt("3/8", spec.nom("length") / 25.4)
    return _l(Location((PX, PY, PZ + G.PIVOT_LUG_Z + G.PIVOT_LUG_T)) * Rot(180, 0, 0) * b, spec)


def pivot_washer(spec) -> Part:
    w = Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness"))
    return _l(w.moved(Location((PX, PY, PZ - G.PIVOT_LUG_Z - G.PIVOT_LUG_T - spec.nom("thickness")))), spec)


def locknut(spec) -> Part:
    """Self-locking nut under the lower lug: hex with its nylon insert collar."""
    n = F.hex_nut("3/8")
    t = 25.4 * F.NUT["3/8"][1]
    n = n + Sh.tube(15.0, 9.0, 3.0, t)
    z0 = PZ - G.PIVOT_LUG_Z - G.PIVOT_LUG_T - 1.65
    return _l(Location((PX, PY, z0)) * Rot(180, 0, 0) * n, spec)


def dust_cover(spec) -> Part:
    """Oval rubber gaiter: flange on the wall round the lever opening, two convolutions and a
    neck that grips the lever (Sec 7 para 3; MGOC Spares 22H1337, oval section)."""
    L = spec.nom("length")
    prof_o = [(0, 0), (30.0, 0), (30.0, 2.5), (25.0, 3.0), (22.0, 7.0), (24.0, 11.0), (19.5, 15.0), (21.5, 19.0),
              (16.4, L - 4), (16.0, L), (0, L)]
    body = Sh.revolved(prof_o)
    body = body - Sh.revolved([(0, -1), (27.0, -1), (22.5, 3.0), (19.5, 7.0), (21.5, 11.0), (17.0, 15.0),
                               (19.0, 19.0), (14.3, L - 4), (14.2, L + 1), (0, L + 1)])
    body = scale(body, by=(1.0, 0.55, 1.0))          # oval: tall (lever depth) and narrow
    pl = Plane(origin=G.LEVER_PORT, x_dir=(0, 0, 1), z_dir=G.LEVER_DIR)
    # the lever's own cross-section through the neck
    return _l(pl.location * body, spec)


PARTS = {
    "clutch.release.carbon": {"build": carbon, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "clutch.release.cup": {"build": cup},
    "clutch.release.clip": {"build": clip},
    "clutch.release.lever": {"build": lever},
    "clutch.release.bush": {"build": bush},
    "clutch.release.pivot-bolt": {"build": pivot_bolt},
    "clutch.release.pivot-washer": {"build": pivot_washer},
    "clutch.release.locknut": {"build": locknut},
    "clutch.release.dust-cover": {"build": dust_cover},
}
