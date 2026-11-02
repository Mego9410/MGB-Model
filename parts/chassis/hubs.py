"""Front hubs for wire wheels (Haynes Ch 11 Fig 11.2 items 67-75, 77; Sec 13; printed p203, 205, 208-209).

Drawn in the left-hand front hub frame of mgb.front_suspension_layout (origin on the wheel axis at the car
centre line, car axes, |y| outward); the assembly places them with `place(side)` (turned half round for the
right, so threads keep their hand). The hubs are handed: the left-hand hub carries the right-hand spinner
thread and the right-hand hub the left-hand thread (MGOC BTB347 LHF / BTB346 RHF, 12 tpi to GHN3-30850).

Forms (Fig 11.2): the hub (67) is one forging - the barrel over the inner bearing with the oil seal in its
inner end, the flange the disc bolts to (four holes on the P8 pitch circle), the inner cone the wheel seats
on, the 42 mm series Rudge-Whitworth splines and the spinner thread, bored through so the castellated nut
(75) and its split pin can be reached through the hole in the splines (Sec 13 para 2). Inside: the oil seal
collar (68) and seal (69), the inner taper roller bearing (70), the spacer (71), the 0.003 in shim (72), the
outer bearing (73), the retaining washer (74), the nut (75) and split pin, and the grease retainer (77)
pressed into the end.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Rot

from mgb import bearings as BR, fasteners as F, front_suspension_layout as L, gears as GR, probes, shapes as Sh
from mgb.chassis_geom import IN, box, castellated_nut, lab, ycyl, yrev, zcyl, zrev
from parts.axle.casing import handed_thread


def along_y(p, y0):
    return Location((0, y0, 0)) * Rot(-90, 0, 0) * p


def _pt(r, a):
    return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))


def hub(thread_hand):
    def b(spec) -> Part:
        f0, f1 = L.HUB_FLANGE_Y
        c0, c1 = L.EXT_COLLAR_Y
        s0, s1 = L.EXT_SPLINE_Y
        t0, t1 = L.EXT_THREAD_Y
        n, dmaj, dmin = L.EXT_SPLINE
        rc0, rc1 = L.EXT_CONE_R
        y_in = L.HUB_IN_Y
        R = L.HUB_BARREL_R
        prof = [(36.0, y_in), (R, y_in), (R, f0), (L.HUB_FLANGE_R - 4.0, f0), (L.HUB_FLANGE_R, f0 + 3.0),
                (L.HUB_FLANGE_R, f1), (44.0, f1), (40.0, f1 + 6.0), (rc0 + 3.0, c0 - 3.0), (rc0 + 3.0, c0 + 3.0),
                (rc0, c0 + 5.0), (rc1, c1), (dmin / 2 - 0.05, c1), (dmin / 2 - 0.05, s1), (L.EXT_THREAD_D / 2 - 1.7, s1 + 0.5),
                (L.EXT_THREAD_D / 2 - 1.7, t0 + 0.2), (L.HUB_BORE_R, t0 + 0.2), (L.HUB_BORE_R, L.OUT_BRG_Y[1] + 0.5),
                (L.OUT_BRG[1] / 2 - 2.0, L.OUT_BRG_Y[1] + 0.5), (L.OUT_BRG[1] / 2 - 2.0, L.OUT_BRG_Y[1]),
                (L.OUT_BRG[1] / 2, L.OUT_BRG_Y[1]), (L.OUT_BRG[1] / 2, L.OUT_BRG_Y[0]), (L.OUT_BRG[1] / 2 - 3.5, L.OUT_BRG_Y[0]),
                (L.OUT_BRG[1] / 2 - 3.5, L.OUT_BRG_Y[0] - 6.0), (L.IN_BRG[1] / 2 - 4.0, L.IN_BRG_Y[1] + 4.0),
                (L.IN_BRG[1] / 2 - 4.0, L.IN_BRG_Y[1]), (L.IN_BRG[1] / 2, L.IN_BRG_Y[1]), (L.IN_BRG[1] / 2, L.IN_BRG_Y[0]),
                (36.0, L.SEAL_Y[1])]
        h = yrev(prof)
        h = h + along_y(GR.spline_shaft(n, dmaj, dmin, s1 - s0 - 1.0), s0 + 0.5)
        h = h + along_y(handed_thread(L.EXT_THREAD_D, L.EXT_TPI, t1 - t0, thread_hand), t0)
        h = h - ycyl(L.HUB_BORE_R, L.OUT_BRG_Y[1], t1 + 1)
        for a in L.DISC_BOLT_ANGLES:                                         # disc bolt holes (nuts on the outer face)
            x, z = _pt(L.DISC_BOLT_PCD / 2, a)
            h = h - ycyl(5.0, f0 - 1, f1 + 1, x, z)
            h = h + (ycyl(8.5, f1 - 0.01, f1 + 1.0, x, z) - ycyl(5.0, f1 - 1, f1 + 2, x, z))   # spot faces
        # split pin access hole through the splines (Sec 13 para 2), at the top
        yn = (L.NUT_Y[0] + L.NUT_Y[1]) / 2 + 4.0
        h = h - Location((0, yn, 0)) * zcyl(3.2, 10.0, 30.0)
        for k in range(8):                                                   # lightening scallops between bolt holes
            pass
        return lab(h, spec)
    return b


def taper_bearing(which):
    def b(spec) -> Part:
        bore, od, w = (L.IN_BRG if which == "inner" else L.OUT_BRG)
        y0 = (L.IN_BRG_Y if which == "inner" else L.OUT_BRG_Y)[0]
        br = BR.taper_roller(bore, od, w)
        if which == "inner":                                                 # cone toward the inside: small end out
            return lab(along_y(br, y0), spec)
        br = br.mirror(__import__("build123d").Plane.XY).moved(Location((0, 0, w)))
        return lab(along_y(br, y0), spec)
    return b


def spacer(spec) -> Part:
    y0, y1 = L.SPACER_Y
    r = L.IN_BRG[0] / 2
    ro = L.OUT_BRG[0] / 2
    s = yrev([(r + 0.2, y0), (r + 4.0, y0), (r + 4.0, y0 + 3.0), (ro + 6.5, y1 - 3.0), (ro + 6.5, y1), (ro + 3.2, y1),
              (ro + 3.2, L.OUT_BRG_Y[0] - 10.0), (r + 0.2, y0 + 18.0)])
    return lab(s, spec)


def shim(spec) -> Part:
    t = spec.nom("thickness")
    y1 = L.OUT_BRG_Y[0]
    return lab(yrev([(L.OUT_BRG[0] / 2 + 0.3, y1 - t), (L.OUT_BRG[0] / 2 + 6.0, y1 - t), (L.OUT_BRG[0] / 2 + 6.0, y1),
                     (L.OUT_BRG[0] / 2 + 0.3, y1)]), spec)


def collar(spec) -> Part:
    y0, y1 = L.COLLAR_Y
    r = L.IN_BRG[0] / 2 + 3.0
    c = yrev([(r + 0.1, y0), (r + 8.0, y0), (r + 8.0, y1 - 1.0), (r + 7.0, y1), (r + 0.1, y1)])
    return lab(c, spec)


def oil_seal(spec) -> Part:
    y0, y1 = L.SEAL_Y
    ri = L.IN_BRG[0] / 2 + 3.0 + 8.0
    ro = L.IN_BRG[1] / 2 + 5.0
    s = yrev([(ri + 3.0, y0), (ro, y0), (ro, y1), (ro - 2.0, y1), (ro - 2.0, y0 + 1.2), (ri + 4.0, y0 + 1.2),
              (ri, y0 + 5.0), (ri, y0 + 3.0)])
    return lab(s, spec)


def retaining_washer(spec) -> Part:
    y0, y1 = L.WASHER_Y
    w = yrev([(L.OUT_BRG[0] / 2 + 0.2, y0), (L.OUT_BRG[0] / 2 + 11.0, y0), (L.OUT_BRG[0] / 2 + 11.0, y1),
              (L.OUT_BRG[0] / 2 + 0.2, y1)])
    w = w + box(-1.4, 1.4, y0, y1, L.OUT_BRG[0] / 2 - 1.6, L.OUT_BRG[0] / 2 + 0.25)    # key in the stub's slot
    return lab(w, spec)


def hub_nut(spec) -> Part:
    af = spec.nom("across_flats")
    n = castellated_nut(af, L.NUT_Y[1] - L.NUT_Y[0], 0.75 * IN * 0.94)
    return lab(along_y(Rot(0, 0, 30) * n, L.NUT_Y[0]), spec)


def split_pin(spec) -> Part:
    """Through the nut's slots and the stub axle (along x), legs opened round the nut."""
    L_ = spec.nom("length")
    d = spec.nom("diameter")
    y = L.STUB_END_Y - 3.5
    r = d / 4
    p = Location((-L_ / 2 - 2.0, y, 0)) * Rot(90, 0, 0) * __import__("build123d").Torus(d * 0.5, r)
    from mgb.chassis_geom import xcyl
    p = p + xcyl(r, -L_ / 2 - 2.0, L_ / 2, y, r) + xcyl(r, -L_ / 2 - 2.0, L_ / 2 - 3.0, y, -r)
    return lab(p, spec)


def grease_retainer(spec) -> Part:
    """Item 77: a pressed cup in the bore of the splined end."""
    t1 = L.EXT_THREAD_Y[1]
    r = L.HUB_BORE_R
    c = yrev([(0, t1 - 9.0), (r - 0.05, t1 - 9.0), (r - 0.05, t1 - 0.5), (r + 1.2, t1 - 0.5), (r + 1.2, t1 + 0.6),
              (r - 1.0, t1 + 0.6), (r - 1.0, t1 - 7.8), (0, t1 - 7.8)])
    return lab(c, spec)


PARTS = {
    "chassis.front-hubs.hub-lh": {"build": hub("right")},
    "chassis.front-hubs.hub-rh": {"build": hub("left")},
    "chassis.front-hubs.inner-bearing": {"build": taper_bearing("inner")},
    "chassis.front-hubs.outer-bearing": {"build": taper_bearing("outer")},
    "chassis.front-hubs.spacer": {"build": spacer},
    "chassis.front-hubs.shim": {"build": shim, "probes": {"thickness": lambda p: probes.bbox_size(p, "y")}},
    "chassis.front-hubs.collar": {"build": collar},
    "chassis.front-hubs.oil-seal": {"build": oil_seal},
    "chassis.front-hubs.retaining-washer": {"build": retaining_washer},
    "chassis.front-hubs.nut": {"build": hub_nut},
    "chassis.front-hubs.split-pin": {"build": split_pin},
    "chassis.front-hubs.grease-retainer": {"build": grease_retainer},
}


def _spline_major(p):
    bb = p.bounding_box()
    # the splines are the largest section beyond the cone: measure across them at mid-spline
    from build123d import Plane
    y = (L.EXT_SPLINE_Y[0] + L.EXT_SPLINE_Y[1]) / 2
    sec = p.intersect(box(-60, 60, y - 0.5, y + 0.5, -60, 60))
    return sec.bounding_box().size.X
