"""Wiring harness, wire by wire (P10b): every cable of the 1963 MGB's harness with its terminal
fittings, the harness joints and snap connectors, the earth points, and the switch gear the
harness needs that P10 did not build (headlamp dip switch, direction indicator switch, voltage
stabiliser). Haynes Fig 10.26 (printed p190) and Fig 6.19 (p131).

Each wire is its own part, built in the car frame along its route from mgb.wiring_layout: an
eight-sided cable swept through ruled sections (light in the viewer), with its fittings at both
ends - a female Lucar in its PVC sleeve on a blade, a sleeved bullet-type female on a pin or stud,
a ring terminal (eye) on a stud, or straight into a moulded plug, bulb holder or joint.
"""
from __future__ import annotations

import math

from build123d import Box, Compound, Cylinder, Location, Part, Plane, Solid

from mgb import body_layout as BL, elec_shapes as X, electrical_layout as E, wiring_layout as WL
from mgb.elec_shapes import box, label, rev, tryfillet, zc

_add, _sub, _unit, _cross, _dot, _perp = WL._add, WL._sub, WL._unit, WL._cross, WL._dot, WL._perp


# ---- the cable ---------------------------------------------------------------------------------------
def tube(points, r, sides=WL.SIDES):
    """Solid cable of radius r along a polyline: an n-gon carried along the path in a parallel
    transported frame, each section in the plane bisecting its corner, joined by ruled faces."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    from OCP.gp import gp_Pnt
    pts = points
    ts = []
    for k in range(len(pts)):
        if k == 0:
            t = _unit(_sub(pts[1], pts[0]))
        elif k == len(pts) - 1:
            t = _unit(_sub(pts[-1], pts[-2]))
        else:
            t = _unit(_add(_unit(_sub(pts[k], pts[k - 1])), _unit(_sub(pts[k + 1], pts[k]))))
        ts.append(t)
    n = _perp(ts[0])
    gen = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    gen.CheckCompatibility(False)
    for k, (p, t) in enumerate(zip(pts, ts)):
        n = _unit(_add(n, t, -_dot(n, t)))
        b = _cross(t, n)
        # keep the cable's full width through a mitred corner: stretch the section along the bend
        s, m = 1.0, None
        if 0 < k < len(pts) - 1:
            d0, d1 = _unit(_sub(pts[k], pts[k - 1])), _unit(_sub(pts[k + 1], pts[k]))
            s = 1.0 / max(0.5, _dot(d0, t))
            mm = _sub(d1, d0)
            mm = _add(mm, t, -_dot(mm, t))
            m = _unit(mm) if _dot(mm, mm) > 1e-12 else None
        poly = BRepBuilderAPI_MakePolygon()
        for j in range(sides):
            a = 2 * math.pi * (j + 0.5) / sides
            o = _add(_add((0.0, 0.0, 0.0), n, math.cos(a) * r), b, math.sin(a) * r)
            if m is not None:
                o = _add(o, m, _dot(o, m) * (s - 1.0))
            poly.Add(gp_Pnt(*_add(p, o)))
        poly.Close()
        gen.AddWire(poly.Wire())
    gen.Build()
    return Solid(gen.Shape())


def _sleeve_lucar(p, d, nrm, od):
    L, W, T = WL.LUCAR_SLEEVE
    side = _unit(_cross(d, nrm))
    c = _add(p, d, 0.5 + L / 2)
    body = Plane(origin=c, x_dir=side, z_dir=d).location * Box(W, T, L)
    neck = Plane(origin=_add(p, d, L - 1.0), x_dir=side, z_dir=d).location * Cylinder(od / 2 + 0.9, 5.0, align=X.BASE)
    return [body, neck]


def _sleeve_pin(p, d, od):
    L, R = WL.PIN_SLEEVE
    body = Plane(origin=_add(p, d, 0.5), z_dir=d).location * (Cylinder(R, L - 3.0, align=X.BASE)
                                                              + Cylinder(R + 0.5, 2.0, align=X.BASE))
    neck = Plane(origin=_add(p, d, L - 3.5), z_dir=d).location * Cylinder(od / 2 + 0.7, 4.0, align=X.BASE)
    return [body, neck]


def _eye(p, d, ax, er, od):
    ro = er + WL.EYE_OUT
    pl = Plane(origin=p, x_dir=d, z_dir=ax)
    ring = pl.location * (Cylinder(ro, 1.2, align=X.BASE) - Cylinder(er, 3.0))
    tongue = pl.location * Location((ro + 2.0, 0, 0.6)) * Box(5.0, ro * 1.1, 1.2)
    barrel = Plane(origin=_add(_add(p, d, ro + 4.0), ax, 0.6 + od / 2), z_dir=d).location * Cylinder(od / 2 + 0.7, 6.0, align=X.BASE)
    return [ring, tongue, barrel]


def fittings(end, od):
    k = end["kind"]
    if k == "lucar":
        return _sleeve_lucar(end["p"], end["d"], end["normal"], od)
    if k == "pin":
        return _sleeve_pin(end["p"], end["d"], od)
    if k == "eye":
        return _eye(end["p"], end["d"], end["axis"], end["eye_r"], od)
    return []


def wire(spec) -> Part:
    w = WL.layout()["wires"][spec.id]
    od = w["od"]
    pts = WL.smooth(w["points"], od)
    solids = [tube(pts, od / 2)]
    for e in ("from", "to"):
        solids += fittings(w["ends"][e], od)
    c = Compound(children=solids)
    return label(c, spec)


# ---- joints, connectors, earth points --------------------------------------------------------------------
def joint(spec) -> Part:
    name = spec.id.split(".")[-1]
    node, off, kind, lab = WL.JOINTS[name]
    p, a = WL.joint_point(name), WL.joint_axis(name)
    L = WL.JOINT_LEN[kind]
    n = WL.share_count("joint." + name)
    pl = Plane(origin=_add(p, a, -L / 2), z_dir=a).location
    if kind == "splice":            # taped soldered joint: a lump, rounded at the closed end
        r = 2.4 + 1.1 * math.sqrt(n)
        j = pl * rev([(0, 0), (r - 1.5, 0), (r, 2.0), (r, L - 1.0), (r - 0.6, L), (0, L)])
    elif kind == "snap":            # Lucas four-way snap connector: moulded rubber block with ribs
        j = pl * Location((0, 0, L / 2)) * Box(15.0, 15.0, L)
        j = tryfillet(j, j.edges(), 2.0)
        for z in (6.0, L - 6.0):
            j = j + pl * Location((0, 0, z)) * Box(16.4, 16.4, 2.0)
    else:                            # single/double snap connector sleeve over two bullets
        r = 4.2 if n <= 2 else 5.2
        j = pl * rev([(0, 0), (r - 0.8, 0), (r, 1.5), (r, L / 2 - 2.0), (r - 0.8, L / 2), (r, L / 2 + 2.0), (r, L - 1.5),
                      (r - 0.8, L), (0, L)])
    return label(j, spec)


def earth_point(spec) -> Part:
    """No 10 self-tapping screw with its shakeproof washer, square to the panel, over the eyelets."""
    name = spec.id.split("earth-", 1)[1]
    p, nrm = WL.earth_points()[name]
    n = WL.share_count("earth." + name)
    top = 1.3 * (n - 1) / 2 + 0.6 + 0.6
    pl = Plane(origin=_add(p, nrm, top), z_dir=nrm).location
    washer = pl * (Cylinder(5.2, 0.8, align=X.BASE) - Cylinder(2.6, 3.0))
    for k in range(8):                                              # shakeproof teeth
        washer = washer + pl * Location((0, 0, 0.4)) * Location((4.4 * math.cos(k * math.pi / 4), 4.4 * math.sin(k * math.pi / 4), 0.4)) * Box(1.6, 1.6, 0.8)
    head = pl * Location((0, 0, 0.8)) * rev([(0, 0), (4.6, 0), (4.6, 1.2), (3.6, 3.0), (0, 3.2)])
    head = head - pl * Location((0, 0, 3.4)) * Box(9.0, 1.0, 2.4) - pl * Location((0, 0, 3.4)) * Box(1.0, 9.0, 2.4)
    shank = Plane(origin=_add(p, nrm, -n * 1.3 - 12.0), z_dir=nrm).location * Cylinder(2.4, n * 1.3 + 12.0 + top, align=X.BASE)
    return label(washer + head + shank, spec)


# ---- switch gear P10 did not build ------------------------------------------------------------------------
def dip_switch(spec) -> Part:
    """Lucas foot dip switch: a pressed base on the toe board with two screw holes, the moulded body,
    the plunger in its rubber boot (pressed by the left foot), and the three blades out of the top
    end, down the slope."""
    L = spec.nom("base_length")
    pl = Plane(origin=WL.DIP_SWITCH, x_dir=WL.DIP_U, z_dir=WL.DIP_N).location
    base = pl * Location((0, 0, 0.8)) * Box(L, 36.0, 1.6)
    base = base - pl * Location((-L / 2 + 7.0, 0, 0)) * Cylinder(2.6, 5.0) - pl * Location((L / 2 - 7.0, 0, 0)) * Cylinder(2.6, 5.0)
    body = pl * Location((4.0, 0, 1.6)) * rev([(0, 0), (15.0, 0), (15.0, 12.0), (13.0, 14.0), (0, 14.0)])
    blk = pl * Location((16.0, 0, 7.0)) * Box(12.0, 28.0, 10.0)
    boot = pl * Location((4.0, 0, 15.5)) * rev([(0, 0), (8.0, 0), (9.0, 3.0), (7.5, 7.0), (8.5, 10.0), (6.0, 14.0), (0, 15.0)])
    s = base + body + blk + boot
    for k in ("feed", "main", "dip"):
        t = E.terminals()["dip." + k]
        bl = Plane(origin=t["p"], x_dir=_cross(t["normal"], t["d"]), z_dir=t["d"]).location * Location((0, 0, 4.0)) * Box(6.35, 0.8, 9.0)
        s = s + bl
    return label(s, spec)


def indicator_switch(spec) -> Part:
    """Column direction indicator switch: a moulded body in two halves clamped round P9's outer
    column tube under the wheel, the lever out to the right, the cancelling cam toward the wheel,
    and the row of blades out of its lower face."""
    from mgb import steering_layout as SL
    w = spec.nom("body_width")
    ax, cx_, cy_ = WL.COL_AXIS, WL.COL_X, WL.COL_Y
    pl = Plane(origin=WL.COLUMN_SWITCH, x_dir=cx_, z_dir=ax).location
    rc = SL.OUTER_TUBE_R + 0.6
    body = pl * Box(w, 52.0, 44.0)
    body = tryfillet(body, body.edges(), 6.0)
    body = body - pl * Cylinder(rc, 60.0)
    cam = pl * Location((0, 0, 24.5)) * (Cylinder(rc + 7.0, 5.0) - Cylinder(rc, 8.0))
    root = _add(_add(WL.COLUMN_SWITCH, cx_, -w / 2 + 2.0), ax, 4.0)
    lever = Plane(origin=root, z_dir=_neg_v(cx_)).location * rev([(0, 0), (4.0, 0), (2.8, 74.0), (0, 74.0)])
    knob = Plane(origin=_add(root, cx_, -74.0), z_dir=_neg_v(cx_)).location * rev([(0, 0), (6.0, 0), (6.0, 10.0), (4.0, 13.0), (0, 13.0)])
    s = body + cam + lever + knob
    T = E.terminals()
    for k in ("LGN", "GR", "GW", "LGY", "LGW", "B", "PB"):
        t = T["ind." + k]
        s = s + Plane(origin=t["p"], x_dir=_cross(t["normal"], t["d"]), z_dir=t["d"]).location * Location((0, 0, 3.0)) * Box(6.35, 0.8, 8.0)
    blk = pl * Location((0, 24.5, -10.0)) * Box(60.0, 7.0, 12.0)            # moulded terminal block on the lower face
    lead = Plane(origin=T["ind.horn"]["p"], z_dir=ax).location * Cylinder(3.0, 6.0, align=X.BASE)   # horn contact grommet
    return label(s + blk + lead, spec)


def _neg_v(v):
    return tuple(-c for c in v)


def stabiliser(spec) -> Part:
    """Bi-metallic voltage stabiliser: a steel can with crimped base and a fixing tab, its three
    blades (B, I, E) out of the bottom."""
    L, H, D = WL.STAB_SIZE
    sx, sy, sz = BL.STABILISER
    can = box(sx, sx + D, sy - L / 2, sy + L / 2, sz - H / 2, sz + H / 2)
    can = tryfillet(can, can.edges().filter_by(__import__("build123d").Axis.X), 3.0)
    tab = box(sx, sx + 1.0, sy + L / 2 - 1.0, sy + L / 2 + 14.0, sz - 7.0, sz + 7.0) - Location((sx, sy + L / 2 + 8.0, sz)) * Cylinder(2.2, 6.0, rotation=(0, 90, 0))
    s = can + tab
    for k in ("B", "I", "E"):
        t = E.terminals()["stab." + k]
        s = s + Plane(origin=t["p"], x_dir=_cross(t["normal"], t["d"]), z_dir=t["d"]).location * Location((0, 0, 3.5)) * Box(6.35, 0.8, 9.0)
    return label(s, spec)


def connector(spec) -> Part:
    """Snap connector standing in for a P11a lead until that phase's part is in the build."""
    key = {"electrical.wiring-starting.pump-connector": "pump.feed",
           "electrical.wiring-instruments.tank-connector": "tank.T"}[spec.id]
    t = E.terminals()[key]
    p = _add(t["p"], t["d"], -12.0)
    return label(Plane(origin=p, z_dir=t["d"]).location * Cylinder(6.0, 24.0), spec)


# ---- registry of builders ------------------------------------------------------------------------
def _parts():
    out = {}
    named = {"dip-switch": dip_switch, "indicator-switch": indicator_switch, "stabiliser": stabiliser,
             "pump-connector": connector, "tank-connector": connector}
    for sp in WL.all_specs():
        name = sp.id.split(".")[-1]
        if sp.data.get("route"):
            out[sp.id] = {"build": wire}
        elif name in WL.JOINTS:
            out[sp.id] = {"build": joint}
        elif name.startswith("earth-"):
            out[sp.id] = {"build": earth_point}
        elif name in named:
            out[sp.id] = {"build": named[name]}
    return out


PARTS = _parts()
