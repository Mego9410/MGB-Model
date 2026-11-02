"""Front engine mountings: the brackets, the bonded rubber mountings, packing plates and fixings (Haynes Ch 1 Fig 1.29
items 1-16, 39; Sec 64; printed p52).

Drawn in the car frame for the left-hand side from mgb.engine_mount_layout; builders take `side` and mirror for the
right, where the bracket differs (the right-hand bracket carries the tab that bolts behind the front plate's wing).

Forms (Fig 1.29): the rubber mounting - a moulded block bonded between two steel plates, two studs out of each plate;
the bracket - a pressing with its vertical plate and the V-shaped lower end (Fig 1.29 inset) that carries the
rubber's upper studs, stiffened by a flanged edge; the packing plate under the rubber.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot, Vector

from mgb import engine_mount_layout as M, fasteners as F
from mgb.chassis_geom import IN, box, frame_to, lab, rod, spring_washer, xprism, ycyl, yprism, zcyl, zprism
from mgb.poly2d import circle_pts, hull


def side_of(p, side):
    return p if side > 0 else p.mirror(Plane.XZ)


def pad_frame(k):
    """Frame on the mounting's axis, k mm up from the crossmember pad face (left side): local z = pad normal, local
    x = car x."""
    return frame_to(M.along(M.PAD, M.N, k), M.N, (1.0, 0.0, 0.0))


def rubber(spec, side=1) -> Part:
    """Items 10/11: bonded rubber block between two plates, two studs down and two up (left-hand, car frame)."""
    lx, ly = M.RUBBER_W
    t = M.PLATE_T
    k0 = M.PACKING_T
    plates = box(-lx / 2, lx / 2, -ly / 2, ly / 2, 0, t)
    up = box(-lx / 2 + 2, lx / 2 - 2, -ly / 2 + 2, ly / 2 - 2, M.RUBBER_T + t, M.RUBBER_T + 2 * t)
    # rubber block, waisted at its middle
    from mgb.chassis_geom import Solid
    r = box(-lx / 2 + 3, lx / 2 - 3, -ly / 2 + 3, ly / 2 - 3, t - 0.01, t + M.RUBBER_T + 0.01)
    for s in (1, -1):
        r = r - Location((0, s * (ly / 2 + 6.0), t + M.RUBBER_T / 2)) * Rot(0, 90, 0) * zcyl(10.5, -lx, lx)
    body = plates + up + r
    d = F.THREADS["3/8"][0] * IN
    for dx in (-M.STUD_DX, M.STUD_DX):
        body = body + zcyl(d / 2, -22.0, 0.01, dx, 0) + zcyl(d / 2, M.RUBBER_T + 2 * t - 0.01, M.RUBBER_T + 2 * t + 20.0, dx, 0)
    return lab(side_of(pad_frame(k0) * body, side), spec)


def packing_plate(spec, side=1) -> Part:
    lx, ly = M.RUBBER_W
    p = box(-lx / 2 - 2, lx / 2 + 2, -ly / 2 - 2, ly / 2 + 2, 0, M.PACKING_T)
    for dx in (-M.STUD_DX, M.STUD_DX):
        p = p - zcyl(5.0, -1, M.PACKING_T + 1, dx, 0)
    return lab(side_of(pad_frame(0.0) * p, side), spec)


def bracket(hand):
    """Items 1 (RH) / 2 (LH): vertical plate on the engine, the V-shaped lower end carrying the rubber's upper studs.
    Drawn on the left for both; the right-hand one (with the tab behind the front plate wing) is mirrored."""
    def b(spec, side=1) -> Part:
        t = M.BRACKET_T
        x0, x1 = M.PLATE_X
        # V-shaped flange: from the plate's foot up and outboard under the rubber's upper plate
        fl_c = M.FLANGE_C
        lo = M.along(fl_c, M.U, -M.RUBBER_W[1] / 2 - 4.0)
        hi = M.along(fl_c, M.U, M.RUBBER_W[1] / 2 + 2.0)
        n = M.N
        prof = [(lo[1], lo[2]), (hi[1], hi[2]), (hi[1] + n[1] * t, hi[2] + n[2] * t), (lo[1] + n[1] * t, lo[2] + n[2] * t)]
        flange = xprism(prof, x0 - 4.0, x1 + 8.0)
        # the vertical plate up the side of the engine
        py = M.PLATE_Y
        plate = box(x0, x1, py, py + t, lo[2] - 2.0, M.PLATE_TOP_Z)
        foot = xprism([(py, lo[2] - 2.0), (py + t, lo[2] - 2.0), (lo[1] + n[1] * t + 2.0, lo[2] + n[2] * t), (lo[1], lo[2])], x0, x1)
        br = flange + plate + foot
        # flanged (turned) edges for stiffness along the plate's sides
        for xa in (x0 - 0.01, x1 - t + 0.01):
            br = br + box(xa, xa + t, py + t - 0.01, py + 12.0, lo[2] + 6.0, M.PLATE_TOP_Z - 4.0)
        # stud holes in the flange
        for dx in (-M.STUD_DX, M.STUD_DX):
            br = br - frame_to(M.along(fl_c, (0, 0, 0), 0), n) * zcyl(5.0, -5.0, 10.0, dx, 0)
        if hand == "left":
            for x, z in M.LH_SCREWS:                                      # screws into the block's pad
                br = br - ycyl(5.0, py - 1, py + t + 1, x, z)
        else:
            # tab forward to behind the front plate's wing, two holes for the screws through the wing
            from parts.engine.block import plates as PL
            tx0, tx1 = M.RH_TAB_X
            ys = [abs(y) for y, z in PL.MOUNT_HOLES]
            zs = [z for y, z in PL.MOUNT_HOLES]
            tab = box(tx0, tx1, py, max(ys) + 10.0, min(zs) - 12.0, max(zs) + 12.0)
            arm = box(x1 - 1.0, tx1, py, py + t, min(zs) - 12.0, M.PLATE_TOP_Z)
            br = br + tab + arm + box(x1 - 1.0, tx1, py, py + t, lo[2] - 2.0, min(zs) - 11.9)
            for y, z in PL.MOUNT_HOLES:
                if abs(y) > 125.0:                                          # the outer pair (inner pair is at the wall)
                    br = br - Location((tx0 - 1, abs(y), z)) * Rot(0, 90, 0) * zcyl(5.2, 0, 10)
        return lab(side_of(br, side), spec)
    return b


def screw(size, series="UNF"):
    def b(spec):
        return lab(F.hex_bolt(size, spec.nom("length") / IN, series), spec)
    return b


def nut(size, series="UNF"):
    def b(spec):
        return lab(F.hex_nut(size, series), spec)
    return b


def sw(size):
    def b(spec):
        return lab(spring_washer(size), spec)
    return b


PARTS = {
    "engine.mountings.rubber-rh": {"build": lambda spec, side=-1: rubber(spec, side)},
    "engine.mountings.rubber-lh": {"build": rubber},
    "engine.mountings.packing-plate": {"build": packing_plate},
    "engine.mountings.bracket-rh": {"build": lambda spec, side=-1: bracket("right")(spec, side)},
    "engine.mountings.bracket-lh": {"build": bracket("left")},
    "engine.mountings.screw-rh": {"build": screw("3/8")},
    "engine.mountings.nut-rh": {"build": nut("3/8")},
    "engine.mountings.screw-lh": {"build": screw("3/8", "UNC")},
    "engine.mountings.stud-nut": {"build": nut("3/8")},
    "engine.mountings.stud-washer": {"build": sw("3/8")},
    "engine.mountings.screw-washer": {"build": sw("3/8")},
}
