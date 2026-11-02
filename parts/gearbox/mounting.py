"""Gearbox rear mounting, early cars: the two rubber mountings on the overdrive main casing and the
removable rear crossmember they sit on, with their fixings (Haynes Ch 1 Fig 1.29 items 17-19,
33-38, Sec 6 paras 33-35, Sec 64 paras 7-11; Ch 6 specifications, "mounting to gearbox case").

Built in the gearbox frame (GF) at the overdrive stations (z = e, moved back by O.Z0); positions
from mgb.overdrive_layout (pads) and mgb.chassis_layout (crossmember, body bolts).

Forms (Fig 1.29): the mounting is a bonded rubber block between a steel angle bolted to the casing
pad by two screws and a base plate with a stud down through the crossmember; the crossmember is a
pressed steel channel, its ends flattened for the body bolts, raised ears under the mountings and
a dip in the middle.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Rot

from mgb import chassis_layout as K, fasteners as F, overdrive_layout as O, probes, shapes as Sh
from mgb.poly2d import rounded
from parts.gearbox import casing as C
from parts.gearbox.od_casing import xcyl, ycyl

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)
zc, box, zprism = C.zc, C.box, C.zprism


def _out(p, spec):
    p = p.moved(Location((0, 0, O.Z0)))
    p.label = spec.id
    return p


def _l(p, spec):
    p.label = spec.id
    return p


# ---- rubber mounting (33), built for the left side; the assembly mirrors it for the right -------
E0, E1 = O.MOUNT_E
U0, U1 = O.MOUNT_UP
FACE = O.MOUNT_FACE
PLATE_T = 3.0
BASE_UP = K.PAD_UP + 0.5                     # base plate underside, on the crossmember pad
BASE_T = 3.0
STUD = K.MOUNT_STUD_LEFT


def _yz_prism(pts, e0, e1):
    """Prism along e of a polygon given as (left, up) points."""
    return zprism([(u, l) for l, u in pts], e0, e1)


PLATE_LOW = -96.0                            # the steel plate hangs below the casing pad


def mounting(spec) -> Part:
    """Item 33: a steel plate on the pad (two holes) hanging below it, the rubber block bonded to its
    lower part and to the base plate, the stud down through the crossmember ear."""
    e0, e1 = E0 + 1.0, E1 - 1.0
    em = (E0 + E1) / 2
    plate = box(PLATE_LOW, U1, FACE, FACE + PLATE_T, e0, e1)
    plate = plate + box(PLATE_LOW, PLATE_LOW + 2.5, FACE + PLATE_T - 0.01, FACE + 9.0, e0, e1)      # stiffening lip
    for e, u in O.MOUNT_SCREWS:
        plate = plate - ycyl(4.2, FACE - 1, FACE + PLATE_T + 1, u, e)
    top = BASE_UP + BASE_T
    rubber = _yz_prism([(FACE + PLATE_T - 0.2, -78.0), (FACE + 14.0, -78.0), (STUD + 16.0, top + 4.0),
                        (STUD + 16.0, top - 0.2), (FACE + 9.0, top - 0.2), (FACE + PLATE_T - 0.2, PLATE_LOW + 3.0)],
                       e0 + 2.0, e1 - 2.0)
    rubber = rubber - ycyl(6.0, FACE + 14.0, STUD + 20.0, top + 9.0, em)                      # void through the block
    base = box(BASE_UP, top, FACE + 6.0, STUD + 18.0, e0, e1)
    base = base + box(BASE_UP, top + 6.0, STUD + 16.0, STUD + 18.0, e0, e1)                    # turned-up edge
    stud = xcyl(0.375 * IN / 2, BASE_UP - 26.0, BASE_UP + 0.1, STUD, em)
    m = plate + rubber + base + stud
    return _out(m, spec)


# ---- crossmember (17) -----------------------------------------------------------------------------
def _profile_full():
    """Top surface (left, up) across the whole car, right end to left end."""
    half = K.PROFILE
    return [(-l, u) for l, u in reversed(half[1:])] + half


def crossmember(spec) -> Part:
    t = K.XM_T
    ec = K.MOUNT_E
    w = K.XM_WIDTH
    top = _profile_full()
    # web: the top path thickened downward
    web = _yz_prism(top + [(l, u - t) for l, u in reversed(top)], ec - w / 2, ec + w / 2)
    # front and rear flanges hanging from the web, tapering out at the ends
    def flange_poly():
        lo = []
        for l, u in reversed(top):
            depth = K.XM_FLANGE if abs(l) < K.END_LEFT[0] - 10.0 else 6.0
            lo.append((l, u - depth))
        return top + lo
    fp = flange_poly()
    for s in (1, -1):
        e_out = ec + s * w / 2
        web = web + _yz_prism(fp, min(e_out, e_out - s * t), max(e_out, e_out - s * t))
    c = web
    # stiffening bead along the web's centre between the mounting ears
    bead = _yz_prism([(-66.0, K.CENTRE_UP - 0.1), (66.0, K.CENTRE_UP - 0.1), (66.0, K.CENTRE_UP + 2.5), (-66.0, K.CENTRE_UP + 2.5)],
                     ec - 6.0, ec + 6.0)
    c = c + bead
    # holes: mounting studs, body bolts, lightening holes in the dip
    for s in (1, -1):
        c = c - xcyl(5.2, K.PAD_UP - 10, K.PAD_UP + 2, s * K.MOUNT_STUD_LEFT, ec)
        for de in (-K.BOLT_DE, K.BOLT_DE):
            c = c - xcyl(5.2, K.BODY_UP - 10, K.BODY_UP + 2, s * K.BOLT_LEFT, ec + de)
        c = c - xcyl(7.0, K.CENTRE_UP - 10, K.CENTRE_UP + 4, s * 40.0, ec)
    # a slot either side of the centre for the steady rod bracket screws (bracket is P9)
    for s in (1, -1):
        c = c - xcyl(4.2, K.CENTRE_UP - 10, K.CENTRE_UP + 4, s * 16.0, ec + 12.0)
    return _out(c, spec)


# ---- fixings ---------------------------------------------------------------------------------------
def bolt(size):
    def b(spec):
        return _l(F.hex_bolt(size, spec.nom("length") / IN), spec)
    return b


def nut(size):
    def b(spec):
        return _l(F.hex_nut(size), spec)
    return b


def plain_washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


WASHER = C.WASHER

PARTS = {
    "gearbox.mounting.mounting": {"build": mounting},
    "gearbox.mounting.mounting-screw": {"build": bolt("5/16"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.mounting.mounting-screw-washer": {"build": C.spring_washer, "probes": WASHER},
    "gearbox.mounting.crossmember": {"build": crossmember},
    "gearbox.mounting.stud-nut": {"build": nut("3/8")},
    "gearbox.mounting.stud-washer": {"build": C.spring_washer, "probes": WASHER},
    "gearbox.mounting.stud-plain-washer": {"build": plain_washer, "probes": WASHER},
    "gearbox.mounting.crossmember-screw": {"build": bolt("3/8"), "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "gearbox.mounting.crossmember-washer": {"build": C.spring_washer, "probes": WASHER},
}
