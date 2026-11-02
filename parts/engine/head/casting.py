"""Cylinder head casting, 18G. Haynes Fig 1.6 item 1, layout from Fig 1.5.

Built in the head frame (see mgb.head_layout): joint face at z = 0, front +X,
manifold side +Y.
"""
import math

from build123d import (Align, Axis, Box, Cylinder, Location, Part, Plane, Rot, Solid, Vector,
                       fillet)

from mgb import probes
from mgb.head_layout import layout

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
# rocker cover rail and top valley (derived; see casting.yaml notes)
RAIL_X = (-199.0, 194.0)
RAIL_Y = (-27.0, 97.0)
RAIL_H = 4.0
VALLEY = 3.0
HEATER_BOSS = 4.0


def _rod(a, b, r) -> Part:
    """Cylinder of radius r from point a to point b."""
    a, b = Vector(*a), Vector(*b)
    d = b - a
    return Part(Solid.make_cylinder(r, d.length, Plane(a, z_dir=d)).wrapped)


def build(spec) -> Part:
    lay = layout(spec)
    top = lay.top_z
    L, W = lay.x_max - lay.x_min, lay.y_max - lay.y_min
    cx, cy = (lay.x_max + lay.x_min) / 2, (lay.y_max + lay.y_min) / 2
    head = Box(L, W, top, align=BASE).moved(Location((cx, cy, 0)))
    head = fillet(head.edges().filter_by(Axis.Z), 7.0)
    head = fillet(head.edges().group_by(Axis.Z)[0], 1.5)       # machined joint face edge
    head = fillet(head.edges().group_by(Axis.Z)[-1], 3.0)

    # raised rail for the rocker cover gasket, valley inside it (Fig 1.6 shows the
    # spring seats and rocker pads standing up from a recessed top)
    rx0, rx1, ry0, ry1 = RAIL_X[0], RAIL_X[1], RAIL_Y[0], RAIL_Y[1]
    rail_out = fillet(Box(rx1 - rx0, ry1 - ry0, RAIL_H, align=BASE).edges().filter_by(Axis.Z), 16.0)
    rail_in = fillet(Box(rx1 - rx0 - 18, ry1 - ry0 - 18, RAIL_H + 2, align=BASE).edges().filter_by(Axis.Z), 8.0)
    rc = Location(((rx0 + rx1) / 2, (ry0 + ry1) / 2, top))
    head = head + (rail_out - rail_in.moved(Location((0, 0, -1)))).moved(rc)
    valley = fillet(Box(rx1 - rx0 - 18, ry1 - ry0 - 18, VALLEY + 1, align=BASE).edges().filter_by(Axis.Z), 8.0)
    valley = valley.moved(Location(((rx0 + rx1) / 2, (ry0 + ry1) / 2, top - VALLEY)))
    keep = []
    for v in lay.valves:
        keep.append(Cylinder(18.5, VALLEY + 2, align=BASE).moved(Location((v.x, v.y, top - VALLEY - 1))))    # spring seats
        keep.append(Cylinder(10.0, VALLEY + 2, align=BASE).moved(Location((v.x, lay.pushrod_y, top - VALLEY - 1))))
    for x in lay.cyl_x:                                                  # rocker pedestal pads
        keep.append(Box(26, 64, VALLEY + 2, align=BASE).moved(Location((x, (lay.short_stud_y + lay.pushrod_y) / 2, top - VALLEY - 1))))
    for x, y in lay.cover_studs:
        keep.append(Cylinder(8.0, VALLEY + 2, align=BASE).moved(Location((x, y, top - VALLEY - 1))))
    for k in keep:
        valley = valley - k
    head = head - valley
    # manifold face: the port band stands proud of the side
    for z0, z1 in ((-1, 7), (65, top + 0.5)):
        head = head - Box(L + 2, 4, z1 - z0, align=BASE).moved(Location((cx, lay.y_max - 1.0, z0)))
    # plug side: recessed panels between the plug bosses
    for x, w in ((0.0, 44), (lay.pitch, 44), (-lay.pitch, 44), (192.0, 36), (-192.0, 36)):
        head = head - Box(w, 6, 46, align=BASE).moved(Location((x, lay.y_min, 12)))
    # heater water outlet boss on the rear end (blanked off when no heater valve is fitted)
    head = head + Cylinder(17, HEATER_BOSS + 2, rotation=(0, 90, 0)).moved(Location((lay.x_min - HEATER_BOSS / 2 + 1, -25, 45)))

    # thermostat outlet boss on the front of the top face
    tx, ty = lay.thermostat
    head = head + Cylinder(31, top + 6, align=BASE).moved(Location((tx, ty, 0)))
    # spark plug bosses on the right-hand face
    for x, y, z in lay.plugs:
        head = head + _rod((x, lay.y_min + 6, 34), (x, lay.y_min - 4, 38.5), 13)

    vr = {v.name: v for v in lay.valves}
    d_in, d_ex = 39.74, 34.17                        # valve heads (Haynes p22, nominal)
    cut = []
    # bathtub combustion chambers: one pocket round each cylinder's two valves
    for c, x in enumerate(lay.cyl_x, start=1):
        a, b = [v for v in lay.valves if v.cyl == c]
        for v in (a, b):
            dv = d_in if v.kind == "inlet" else d_ex
            cut.append(Cylinder(dv / 2 + 2.5, lay.chamber_depth, align=BASE).moved(Location((v.x, v.y, 0))))
        cut.append(Box(lay.vpitch, 30, lay.chamber_depth, align=BASE).moved(Location((x, lay.valve_y - 4, 0))))
        cut.append(Cylinder(14, lay.chamber_depth, align=BASE).moved(Location((x, -14, 0))))
    # valve throats, guide bores and pushrod holes
    for v in lay.valves:
        dv = d_in if v.kind == "inlet" else d_ex
        cut.append(Cylinder(dv / 2 - 2.5, 30, align=BASE).moved(Location((v.x, v.y, lay.chamber_depth - 0.5))))
        cut.append(Cylinder(spec.nom("guide_bore") / 2, top + 2, align=BASE).moved(Location((v.x, v.y, 20))))
        cut.append(Cylinder(spec.nom("pushrod_hole") / 2, top + 2, align=BASE).moved(Location((v.x, lay.pushrod_y, -1))))
    # ports: each runs from the manifold face to its valve throats
    face_y = lay.y_max
    for (px, pz, names), (rw, rh) in [(p, (19, 21)) for p in lay.inlet_ports] + \
                                     [(p, (16, 18)) for p in lay.exhaust_ports]:
        cut.append(_rod((px, face_y + 1, pz), (px, face_y - 22, pz), min(rw, rh)))
        for n in names:
            v = vr[n]
            cut.append(_rod((px, face_y - 20, pz), (v.x, v.y, 26), min(rw, rh) - 2.5))
    # head studs, short rocker studs, cover studs, manifold stud holes
    for _, x, y, _ in lay.head_studs:
        cut.append(Cylinder(spec.nom("head_stud_hole") / 2, top + 10, align=BASE).moved(Location((x, y, -1))))
    for x in lay.cyl_x:
        cut.append(Cylinder(3.4, 25, align=BASE).moved(Location((x, lay.short_stud_y, top - 24))))
    for x, y in lay.cover_studs:
        cut.append(Cylinder(2.7, 25, align=BASE).moved(Location((x, y, top - 24))))
    for x, z, _ in lay.manifold_studs:
        cut.append(_rod((x, face_y + 1, z), (x, face_y - 26, z), 3.4))
    # spark plug holes, 14 mm, angled down into each chamber
    for x, y, z in lay.plugs:
        cut.append(_rod((x, lay.y_min - 6, 39), (x, y, z), 7.0))
    # thermostat pocket and water holes in the joint face
    cut.append(Cylinder(24, 30, align=BASE).moved(Location((tx, ty, top - 24))))
    for x in lay.cyl_x:
        for dx in (-30, 30):
            cut.append(Cylinder(5, 22, align=BASE).moved(Location((x + dx, -50, -1))))
    cut.append(Cylinder(9, 30, rotation=(0, 90, 0)).moved(Location((lay.x_min, -25, 45))))
    # thermostat stud holes
    for k in range(3):
        a = math.radians(90 + 120 * k)
        cut.append(Cylinder(3.4, 20, align=BASE).moved(Location((tx + 26 * math.cos(a), ty + 26 * math.sin(a), top - 14))))
    # P10: tapped hole for the temperature gauge's thermal transmitter (Ch 1 Sec 13 para 6)
    from mgb import electrical_layout as EZ
    bx_, by_, bz_ = EZ.TEMP_BULB
    cut.append(_rod((bx_, by_ - 4.0, bz_), (bx_, by_ + 21.0, bz_), 5.2))
    for c in cut:
        head = head - c
    head.label = spec.id
    return head


PARTS = {"engine.head.casting": {"build": build}}
