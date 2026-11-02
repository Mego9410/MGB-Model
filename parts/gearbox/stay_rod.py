"""Gearbox stay (steady) rod, three-synchromesh gearbox (Haynes Ch 1 Fig 1.29 items 20-32; Ch 1 Sec 6 para 33; Ch 6 Sec
14 para 1; printed p52): bracket, rod, buffers, buffer plates, distance tube, bushes, pin and fixings.

Car frame, datums in mgb.chassis_layout (STAY_*). Forms (Fig 1.29): the bracket (20) - a pressing screwed to the
crossmember's dip with an upright the rod's threaded end passes through; the rod (23) - a bar with an eye at its front
end for the rubber bushes (29) and a thread at the rear; rubber buffers (24) either side of the upright, each behind a
dished plate (25), on the distance tube (26), nut and spring washer (27, 28); the pin (30) - a wedge flange screwed
under the gearbox casing with the pin hanging from it, the plain washer and nut (31, 32) under the eye.
"""
from __future__ import annotations

from build123d import Location, Part, Rot

from mgb import chassis_layout as K, fasteners as F
from mgb.chassis_geom import IN, box, lab, spring_washer, xcyl, xprism, yprism, zcyl, zprism, zrev

Y, Z = K.STAY_Y, K.STAY_Z
PX = K.STAY_PIN[0]
WX = K.STAY_WEB_X
XM_TOP = K.STAY_BRACKET_SCREWS[0][2] + 2.6          # on the crossmember's centre bead
ROD_D = F.THREADS["3/8"][0] * IN


def bracket(spec) -> Part:
    t = 3.0
    x0, x1 = K.STAY_BRACKET_SCREWS[0][0] - 11.0, WX + t
    base = box(x0, x1, -26.0, 74.0, XM_TOP, XM_TOP + t)
    for x, y, z in K.STAY_BRACKET_SCREWS:
        base = base - zcyl(4.2, z - 1, z + t + 1, x, y)
    web = xprism([(Y - 16.0, XM_TOP + t - 0.01), (Y + 16.0, XM_TOP + t - 0.01), (Y + 16.0, Z + 16.0), (Y - 16.0, Z + 16.0)], WX, WX + t)
    web = web - xcyl(ROD_D / 2 + 3.5, WX - 1, WX + t + 1, Y, Z)
    gus = yprism([(x0 + 26.0, XM_TOP + t - 0.01), (WX + 0.01, XM_TOP + t - 0.01), (WX + 0.01, Z - 8.0)], Y - 15.0, Y - 12.0)
    gus = gus + yprism([(x0 + 26.0, XM_TOP + t - 0.01), (WX + 0.01, XM_TOP + t - 0.01), (WX + 0.01, Z - 8.0)], -16.0, -13.0)
    return lab(base + web + gus, spec)


def rod(spec) -> Part:
    """Item 23: front eye round the bushes, rod rearward through the bracket, threaded end."""
    x_end = WX - 26.0
    r = rod_ = xcyl(ROD_D / 2 + 1.6, x_end + 34.0, PX - 18.0, Y, Z)
    r = r + xcyl(ROD_D / 2, x_end, x_end + 34.01, Y, Z)
    eye = zrev([(11.5, -9.0), (17.0, -9.0), (17.0, 9.0), (11.5, 9.0)]).moved(Location((PX, Y, Z)))
    r = r + eye
    for k in range(16):                                                  # thread
        x = x_end + 1.5 + k * IN / 24
        r = r - Location((x, Y, Z)) * Rot(0, 90, 0) * zrev([(ROD_D / 2 - 0.4, 0), (ROD_D / 2 + 1, -0.3), (ROD_D / 2 + 1, 0.3)])
    return lab(r, spec)


def buffer(spec) -> Part:
    """Item 24: square rubber buffer with a centre hole (drawn on +z from 0, axis along z)."""
    w, t = spec.nom("width"), spec.nom("thickness")
    b = box(-w / 2, w / 2, -w / 2, w / 2, 0, t) - zcyl(6.6, -1, t + 1)
    b = b - box(-w / 2 - 1, w / 2 + 1, -1.0, 1.0, t - 1.0, t + 1)
    return lab(b, spec)


def buffer_plate(spec) -> Part:
    w = spec.nom("width")
    t = 2.0
    p = box(-w / 2, w / 2, -w / 2, w / 2, 0, t) + box(-w / 2, w / 2, w / 2 - t, w / 2, 0, 7.0) + box(-w / 2, w / 2, -w / 2, -w / 2 + t, 0, 7.0)
    return lab(p - zcyl(ROD_D / 2 + 0.6, -1, 3), spec)


def distance_tube(spec) -> Part:
    return lab(zrev([(ROD_D / 2 + 0.3, 0), (ROD_D / 2 + 3.0, 0), (ROD_D / 2 + 3.0, spec.nom("length")),
                     (ROD_D / 2 + 0.3, spec.nom("length"))]), spec)


def bush(spec) -> Part:
    """Item 29: rubber top-hat half bush in the rod's eye (along +z from its flange's outer face)."""
    b = zrev([(6.5, 0), (17.0, 0), (17.0, 2.5), (11.5, 2.5), (11.5, 9.0), (6.5, 9.0)])
    return lab(b, spec)


def pin(spec) -> Part:
    """Item 30: wedge flange under the casing's sloping side, two screw holes, the pin hanging down, threaded end."""
    top = K.STAY_PIN_TOP_Z
    top = top - 4.0                                                     # clear of the casing's sloping side
    fl = zprism([(-20.0, -14.0), (20.0, -14.0), (12.0, 14.0), (-12.0, 14.0)], top - 8.0, top - 0.3).moved(Location((PX, Y, 0)))
    fl = fl & yprism([(PX - 30, top - 8.0), (PX + 30, top - 8.0), (PX + 30, top + 2.0), (PX - 30, top + 2.0)], Y - 20, Y + 20)
    fl = fl - yprism([(PX - 31, top - 0.3), (PX + 31, top - 0.3), (PX + 31, top + 6.0), (PX - 31, top + 6.0)], Y - 21, Y + 21)
    for dx in (-14.0, 14.0):
        fl = fl - zcyl(4.2, top - 10, top + 1, PX + dx, Y - 6.0)
    p = fl + zcyl(6.4, Z - 13.0, top - 7.9, PX, Y) + zcyl(ROD_D / 2, Z - 26.0, Z - 12.99, PX, Y)
    return lab(p, spec)


def screw516(spec):
    return lab(F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def nut(size):
    def b(spec):
        return lab(F.hex_nut(size), spec)
    return b


def sw(size):
    def b(spec):
        return lab(spring_washer(size), spec)
    return b


def pw(size):
    def b(spec):
        return lab(F.plain_washer(size), spec)
    return b


PARTS = {
    "gearbox.stay-rod.bracket": {"build": bracket},
    "gearbox.stay-rod.bracket-screw": {"build": screw516},
    "gearbox.stay-rod.bracket-washer": {"build": sw("5/16")},
    "gearbox.stay-rod.rod": {"build": rod},
    "gearbox.stay-rod.buffer": {"build": buffer},
    "gearbox.stay-rod.buffer-plate": {"build": buffer_plate},
    "gearbox.stay-rod.distance-tube": {"build": distance_tube},
    "gearbox.stay-rod.rod-washer": {"build": sw("3/8")},
    "gearbox.stay-rod.rod-nut": {"build": nut("3/8")},
    "gearbox.stay-rod.bush": {"build": bush},
    "gearbox.stay-rod.pin": {"build": pin},
    "gearbox.stay-rod.pin-screw": {"build": screw516},
    "gearbox.stay-rod.pin-washer": {"build": sw("3/8")},
    "gearbox.stay-rod.pin-nut": {"build": nut("3/8")},
}
