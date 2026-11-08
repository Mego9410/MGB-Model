"""Brake pedal, early cars, and the common pedal pivot (Haynes Ch 9 Sec 17 para 3, Sec 24 and Fig 9.16 items 1-10,
printed p154, 159-160; Ch 5 Sec 8: the clutch pedal comes off the same way).

The brake pedal hangs beside the clutch pedal (parts.clutch.pedal) from the common pivot bolt in the pedal box,
outboard of it on RHD cars, the master cylinder pushrod's clevis just below the pivot. The early brake and clutch
pedals are the same pressing in the layout (D: Fig 9.16 item 1 for the form; the two pads side by side at the
same height), so the brake pedal, its bush, distance tube, pad, pull-off spring and clevis pin are the clutch
pedal's forms moved across to the brake cylinder's line (brake_layout.MC_Y). Built in the car frame.

Pivot stack along the bolt (Fig 9.16 items 5-8; Sec 24 paras 2-3), inboard to outboard: the bolt head on the box's
inboard wall, a plain washer, the inner spacer, the clutch pedal's distance tube in its bush, the centre (pedal)
spacer, the brake pedal's distance tube in its bush, the outer spacer, a plain washer, the outboard wall, the spring
washer and the nut.
"""
from __future__ import annotations

from build123d import Location, Part, Rot

from mgb import brake_layout as B, clutch_layout as K, fasteners as F, shapes as Sh
from mgb.brake_parts import IN, lab, spring_washer, split_pin, ycyl
from parts.clutch import pedal as CP

DY = B.MC_Y - K.MC_Y                          # clutch pedal line to the brake pedal line
MOVE = Location((0, DY, 0))
PX, _, PZ = B.PEDAL_PIVOT
Y_IN = B.BOX_Y[1] - B.BOX_T                   # inner faces of the box walls
Y_OUT = B.BOX_Y[0] + B.BOX_T
WASHER_T = 0.095 * IN                         # 1/2 in plain washer (fasteners.WASHER)
CLEVIS_PIN_L = 28.0                           # specs/brakes/pedal.yaml clevis-pin length


def _tube_ends(py):
    return py + 13.0, py - 13.0               # distance tubes 26 mm long (clutch spec), centred on each pedal


def stack():
    """(y0, y1) of each item on the pivot bolt, inboard (larger y) to outboard."""
    c0, c1 = _tube_ends(K.PEDAL_PIVOT[1])
    b0, b1 = _tube_ends(B.MC_Y)
    return {"washer-in": (Y_IN, Y_IN - WASHER_T), "spacer-in": (Y_IN - WASHER_T, c0), "spacer-centre": (c1, b0),
            "spacer-out": (b1, Y_OUT + WASHER_T), "washer-out": (Y_OUT + WASHER_T, Y_OUT)}


def _moved(fn):
    def build(spec) -> Part:
        return lab(MOVE * fn(spec), spec)
    return build


def _jog_path():
    """Brake arm centre line (car frame): the clutch pedal's arm on the brake cylinder's line (brake_layout ARM_Y), stepped
    outboard to the pad's line (PAD_Y) below the steering column, as the clutch arm is (QA fix round 1, cockpit)."""
    return CP.stepped_path(B.ARM_Y, B.PAD_Y)


def brake_pedal(spec) -> Part:
    """Item 1 (RHD): the clutch pedal's pressing, cranked outboard round the steering column (brake_layout ARM_Y)."""
    from build123d import Box, FilletPolyline, Plane, Rectangle, sweep, Align
    pts = _jog_path()
    path = None
    for rr in (14.0, 8.0, 4.0):
        try:
            path = FilletPolyline(*pts, radius=rr)
            break
        except ValueError:
            continue
    prof = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0), x_dir=(0, 1, 0)) * Rectangle(CP.T, 24.0)
    p = sweep(prof, path=path)
    py, T = B.MC_Y, CP.T
    cx, _, cz = B.PEDAL_CLEVIS
    ax, _, az = B.PEDAL_PAD
    p = p + ycyl(16.0, py - T / 2, py + T / 2, PX, PZ) + ycyl(13.0, py - 12.5, py + 12.5, PX, PZ)
    p = p + ycyl(10.0, py - T / 2, py + T / 2, cx, cz)
    pl = Plane(origin=(ax, B.PAD_Y, az), x_dir=(0, 1, 0), z_dir=CP.PAD_N)
    p = p + pl.location * Box(50.0, 62.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
    p = p + pl.location * Box(20.0, 50.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, -2.9)))
    p = p - ycyl(spec.nom("bush_bore") / 2, py - 20, py + 20, PX, PZ)
    p = p - ycyl(4.1, py - 10, py + 10, cx, cz)
    sx, sz = CP.SPRING_PEDAL
    p = p - ycyl(2.2, B.ARM_Y - 10, B.ARM_Y + 10, sx, sz)
    return lab(p, spec)


def return_spring(spec) -> Part:
    """Pull-off spring (item 10) from the hole in the arm, on the arm's joggled part, to its tab on the box."""
    return lab(Location((0, B.ARM_Y - K.PEDAL_PIVOT[1], 0)) * CP.return_spring(spec), spec)


def spacer(which):
    def build(spec) -> Part:
        y0, y1 = stack()[which]
        od, id_ = spec.nom("outside_diameter"), spec.nom("inside_diameter")
        return lab(ycyl(od / 2, y1, y0, PX, PZ) - ycyl(id_ / 2, y1 - 1, y0 + 1, PX, PZ), spec)
    return build


def pivot_washer(which):
    def build(spec) -> Part:
        y0, y1 = stack()[which]
        i, o = 0.531 * IN, 1.062 * IN
        return lab(ycyl(o / 2, min(y0, y1), max(y0, y1), PX, PZ) - ycyl(i / 2, min(y0, y1) - 1, max(y0, y1) + 1, PX, PZ), spec)
    return build


def pivot_bolt(spec) -> Part:
    """Fulcrum pin bolt, 1/2 UNF, head on the inboard wall (against the clutch pedal end, Sec 24 para 3)."""
    b = F.hex_bolt("1/2", spec.nom("length") / IN)
    return lab(Location((PX, B.BOX_Y[1], PZ)) * Rot(90, 0, 0) * b, spec)


def pivot_spring_washer(spec) -> Part:
    w, t = spring_washer("1/2")
    return lab(Location((PX, B.BOX_Y[0], PZ)) * Rot(90, 0, 0) * w, spec)


def pivot_nut(spec) -> Part:
    t = spring_washer("1/2")[1]
    return lab(Location((PX, B.BOX_Y[0] - t, PZ)) * Rot(90, 0, 0) * F.hex_nut("1/2"), spec)


def clevis_washer(spec) -> Part:
    """Plain washer under the split pin on the clevis pin's end (Sec 17 para 3)."""
    cx, cy, cz = B.PEDAL_CLEVIS
    t = spec.nom("thickness")
    y0 = cy + 9.0                                   # inboard face of the pushrod fork (the pin's head is outboard)
    return lab(ycyl(7.0, y0, y0 + t, cx, cz) - ycyl(4.1, y0 - 1, y0 + t + 1, cx, cz), spec)


def clevis_split_pin(spec) -> Part:
    cx, cy, cz = B.PEDAL_CLEVIS
    L = spec.nom("length")
    yp = cy + CLEVIS_PIN_L / 2 - 2.5                # through the hole in the clevis pin, outside the washer
    return lab(Location((cx, yp, cz + 5.5)) * Rot(180, 0, 0) * split_pin(spec.nom("diameter"), L), spec)


PARTS = {
    "brakes.pedal.pedal": {"build": brake_pedal},
    "brakes.pedal.bush": {"build": _moved(CP.bush)},
    "brakes.pedal.distance-tube": {"build": _moved(CP.distance_tube)},
    "brakes.pedal.pad": {"build": lambda spec: lab(Location((0, B.PAD_Y - K.PAD_Y, 0)) * CP.pad(spec), spec)},
    "brakes.pedal.return-spring": {"build": return_spring},
    "brakes.pedal.clevis-pin": {"build": _moved(CP.clevis_pin)},
    "brakes.pedal.clevis-washer": {"build": clevis_washer},
    "brakes.pedal.clevis-split-pin": {"build": clevis_split_pin},
    "brakes.pedal.pivot-bolt": {"build": pivot_bolt, "probes": {"length": lambda p: p.bounding_box().size.Y - F.BOLT_HEAD["1/2"][1] * IN}},
    "brakes.pedal.pivot-spring-washer": {"build": pivot_spring_washer},
    "brakes.pedal.pivot-nut": {"build": pivot_nut},
    "brakes.pedal.washer-inner": {"build": pivot_washer("washer-in")},
    "brakes.pedal.washer-outer": {"build": pivot_washer("washer-out")},
    "brakes.pedal.spacer-inner": {"build": spacer("spacer-in")},
    "brakes.pedal.spacer-centre": {"build": spacer("spacer-centre")},
    "brakes.pedal.spacer-outer": {"build": spacer("spacer-out")},
}
