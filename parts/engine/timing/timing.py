"""Timing gear: chainwheels, duplex chain, tensioner, camshaft locating plate, oil
thrower, timing cover and crankshaft pulley. Haynes Sec 18, 19, 50-52; Figs 1.11, 1.25;
photos 18.2, 50.5, 51.3, 51.8, 51.12, 51.15.

Wheels, pulley and small round parts are built about the X axis at the origin and
placed by the assembly; the chain, tensioner and cover are built in the engine frame
(absolute Y and Z, see mgb.timing_layout) because their shape follows the layout.
"""
import math

from build123d import (Align, Axis, Box, Compound, Cylinder, Location, Part, Plane, Polygon, Rot, SlotCenterToCenter,
                       Sphere, extrude, fillet)

from mgb import fasteners as F, probes, shapes as Sh, timing_layout as T

X = (1, 0, 0)


def _l(p, spec):
    p.label = spec.id
    return p


def _xdisc(r, x0, x1, y=0.0, z=0.0):
    return Cylinder(r, x1 - x0, rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _yz(points, x0, t):
    return extrude(Plane.YZ.offset(x0) * Polygon(*points, align=None), t, dir=X)


# ---- chainwheels --------------------------------------------------------------------------
def tooth_outline(teeth, seat_r=T.ROLLER_D / 2 + 0.2, samples=7):
    """Sprocket outline (y, z) about the origin: a roller seat at every pitch, straight
    flanks out to a narrow tip between seats."""
    R = T.PITCH / (2 * math.sin(math.pi / teeth))
    tip = R + 0.32 * T.PITCH
    a = 2 * math.pi / teeth
    half_tip = 0.6 / tip
    pts = []
    for k in range(teeth):
        th = k * a
        cy, cz = R * math.cos(th), R * math.sin(th)
        for j in range(samples):                                # seat arc facing the centre
            psi = th + math.pi + math.radians(75 - 150 * j / (samples - 1))
            pts.append((cy + seat_r * math.cos(psi), cz + seat_r * math.sin(psi)))
        for da in (a / 2 - half_tip, a / 2 + half_tip):          # tip of the next tooth
            pts.append((tip * math.cos(th + da), tip * math.sin(th + da)))
    return pts


def _toothed(teeth, x_centre):
    """Two rows of teeth for the duplex chain, centred on x_centre."""
    w = T.INNER_W - 0.5
    rows = None
    for dx in (-T.ROW_PITCH / 2, T.ROW_PITCH / 2):
        r = _yz(tooth_outline(teeth), x_centre + dx - w / 2, w)
        rows = r if rows is None else rows + r
    return rows


def cam_wheel(spec) -> Part:
    """40-tooth duplex wheel, dished web with two lightening holes (photo 51.3).
    Frame: axis X, rear face of the hub at x = 0, chain centre plane at x = hub offset."""
    n, bore, hub_l = int(spec.nom("teeth")), spec.nom("bore"), spec.nom("hub_length")
    R = T.PITCH / (2 * math.sin(math.pi / n))
    cx = T.CHAIN_X - T.CAM_HUB_X                                # chain plane from the hub's rear face
    w = _toothed(n, cx)
    rim_in = R - 7.5
    w = w - _xdisc(rim_in, cx - 12, cx + 12)
    w = w + (_xdisc(rim_in + 1, cx - 3, cx + 3) - _xdisc(rim_in - 6, cx - 4, cx + 4))   # rim band
    web = _xdisc(rim_in - 5, cx - 2.2, cx + 2.2)
    for ang in (0, 180):                                         # two lightening holes
        a = math.radians(ang + 35)
        web = web - _xdisc(11.5, cx - 5, cx + 5, 30 * math.cos(a), 30 * math.sin(a))
    hub = _xdisc(20, 0, hub_l)
    w = w + web + hub
    w = w - _xdisc(bore / 2, -1, hub_l + 1)
    w = w - Box(hub_l + 2, 4.8, 3.0).moved(Location((hub_l / 2, 0, bore / 2 + 1.0)))   # keyway
    w = w - Sphere(1.6).moved(Location((hub_l, 0, -(bore / 2 + 6))))                 # timing dimple (Fig 1.25)
    return _l(w, spec)


def crank_wheel(spec) -> Part:
    """20-tooth duplex wheel on a long hub. Frame: axis X, rear face at x = 0."""
    n, bore, hub_l = int(spec.nom("teeth")), spec.nom("bore"), spec.nom("hub_length")
    cx = T.CHAIN_X - T.CRANK_HUB_X
    w = _toothed(n, cx) + _xdisc(21, 0, hub_l)
    w = w - _xdisc(bore / 2, -1, hub_l + 1)
    w = w - Box(hub_l + 2, 4.8, 3.0).moved(Location((hub_l / 2, 0, bore / 2 + 1.0)))
    w = w - Sphere(1.6).moved(Location((hub_l, 0, bore / 2 + 6)))
    return _l(w, spec)


# ---- chain ----------------------------------------------------------------------------------
def chain(spec) -> Part:
    """52-pitch duplex roller chain round its real path (engine frame)."""
    pts, _ = T.chain_path(int(spec.nom("pitches")))
    rr = T.ROLLER_D / 2
    plate_t, plate_h = 0.75, 8.2
    solids = []
    xs_rows = (T.CHAIN_X - T.ROW_PITCH / 2, T.CHAIN_X + T.ROW_PITCH / 2)
    plate_x = [xs_rows[0] - T.INNER_W / 2 - 0.4, T.CHAIN_X - 0.4, T.CHAIN_X + 0.4 - plate_t,
               xs_rows[1] + T.INNER_W / 2 + 0.4 - plate_t]
    outer_x = [plate_x[0] - plate_t - 0.05, plate_x[3] + plate_t + 0.05]
    for k, (y, z) in enumerate(pts):
        for xr in xs_rows:
            solids.append(_xdisc(rr, xr - T.INNER_W / 2 + 0.3, xr + T.INNER_W / 2 - 0.3, y, z))
        solids.append(_xdisc(1.6, outer_x[0] - 0.6, outer_x[1] + plate_t + 0.6, y, z))           # pin
        y2, z2 = pts[(k + 1) % len(pts)]
        d = math.dist((y, z), (y2, z2))
        mid = ((y + y2) / 2, (z + z2) / 2)
        xs = plate_x if k % 2 == 0 else [outer_x[0], outer_x[1]]
        for x0 in xs:
            pl = Plane(origin=(x0, mid[0], mid[1]), x_dir=(0, (y2 - y) / d, (z2 - z) / d), z_dir=X)
            solids.append(extrude(pl * SlotCenterToCenter(d, plate_h), plate_t))
    c = Compound(children=solids)
    p = Part(c.wrapped)
    return _l(p, spec)


# ---- tensioner (Fig 1.11, double row) -------------------------------------------------------
def _tensioner_frame():
    """Plane at the slipper contact: x_dir along the chain run, z_dir pointing out of the chain."""
    (py, pz), m = T.tensioner_point()
    run = (-m[1], m[0])
    return py, pz, m, run


def _on_run(u, v, x0, t, w_run, w_out):
    """Box on the tensioner axis: u along the run, v outward from the chain, x from x0."""
    py, pz, m, run = _tensioner_frame()
    c = (py + run[0] * u + m[0] * v, pz + run[1] * u + m[1] * v)
    pts = []
    for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        pts.append((c[0] + run[0] * su * w_run / 2 + m[0] * sv * w_out / 2,
                    c[1] + run[1] * su * w_run / 2 + m[1] * sv * w_out / 2))
    return _yz(pts, x0, t)


def _out_cyl(r, v0, v1, x):
    """Cylinder along the tensioner axis (outward from the chain), from v0 to v1."""
    py, pz, m, _ = _tensioner_frame()
    pl = Plane(origin=(x, py + m[0] * v0, pz + m[1] * v0), x_dir=X, z_dir=(0, m[0], m[1]))
    return pl.location * Cylinder(r, v1 - v0, align=(Align.CENTER, Align.CENTER, Align.MIN))

SLIPPER_GAP = T.ROLLER_D / 2 + 1.0       # slipper face from the chain pitch line


def tensioner_body(spec) -> Part:
    """Cast body: plunger bore toward the chain, two bolt lugs onto the block, bottom plug
    boss for the Allen key (Haynes Sec 19 para 10)."""
    v0 = SLIPPER_GAP + 14
    x0 = T.PANEL_FACE + 1.6                                       # on the backplate
    body = _on_run(0, v0 + 18, x0, 30, 30, 36)
    body = body + _on_run(0, v0 + 30, x0, 8, 64, 16)            # flange with the bolt lugs
    body = body + _out_cyl(8, v0 + 36, v0 + 44, T.CHAIN_X)      # bottom plug boss
    body = body - _out_cyl(9.6, v0 - 1, v0 + 30, T.CHAIN_X)     # plunger bore
    for u in (-24, 24):                                         # bolt holes
        py, pz, m, run = _tensioner_frame()
        c = (py + run[0] * u + m[0] * (v0 + 30), pz + run[1] * u + m[1] * (v0 + 30))
        body = body - _xdisc(4.2, x0 - 1, x0 + 10, *c)
    return _l(body, spec)


def tensioner_slipper(spec) -> Part:
    """Rubber-faced slipper head on its plunger (Fig 1.11)."""
    v0 = SLIPPER_GAP
    pad = _on_run(0, v0 + 6, T.CHAIN_X - 12, 24, spec.nom("pad_length"), 12)
    plunger = _out_cyl(9.2, v0 + 10, v0 + 40, T.CHAIN_X)
    return _l(pad + plunger - _out_cyl(5.5, v0 + 16, v0 + 41, T.CHAIN_X), spec)


def tensioner_spring(spec) -> Part:
    py, pz, m, _ = _tensioner_frame()
    v0 = SLIPPER_GAP + 18
    sp = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("length"), 7, 1)
    pl = Plane(origin=(T.CHAIN_X, py + m[0] * v0, pz + m[1] * v0), x_dir=X, z_dir=(0, m[0], m[1]))
    return _l(pl.location * sp, spec)


def tensioner_cylinder(spec) -> Part:
    """Inner cylinder with the helical slot the plunger peg rides in."""
    v0 = SLIPPER_GAP + 26
    c = _out_cyl(5.0, v0, v0 + spec.nom("length"), T.CHAIN_X) - _out_cyl(1.6, v0 - 1, v0 + 6, T.CHAIN_X)
    return _l(c, spec)


def tensioner_backplate(spec) -> Part:
    t = spec.nom("thickness")
    v0 = SLIPPER_GAP + 14
    p = _on_run(0, v0 + 22, T.PANEL_FACE, t, 70, 52)
    py, pz, m, run = _tensioner_frame()
    for u in (-24, 24):
        c = (py + run[0] * u + m[0] * (v0 + 30), pz + run[1] * u + m[1] * (v0 + 30))
        p = p - _xdisc(4.2, T.PANEL_FACE - 1, T.PANEL_FACE + t + 1, *c)
    return _l(p, spec)


def tensioner_lockwasher(spec) -> Part:
    """Tab washer under both tensioner bolts, on top of the flange."""
    t = spec.nom("thickness")
    v0 = SLIPPER_GAP + 14
    x0 = T.PANEL_FACE + 1.6 + 8
    p = _on_run(0, v0 + 30, x0, t, 66, 14)
    py, pz, m, run = _tensioner_frame()
    for u in (-24, 24):
        c = (py + run[0] * u + m[0] * (v0 + 30), pz + run[1] * u + m[1] * (v0 + 30))
        p = p - _xdisc(4.2, x0 - 1, x0 + t + 1, *c)
        tab = _on_run(u + (5 if u > 0 else -5), v0 + 30, x0, 8, 4, 14)      # bent-up tab against a bolt flat
        p = p + tab
    return _l(p, spec)


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _l(Sh.washer(od, id_, t) - Box(1.0, od, t * 3).moved(Location((0, od / 2, 0))), spec)


def tensioner_plug(spec) -> Part:
    v = SLIPPER_GAP + 14 + 44
    py, pz, m, _ = _tensioner_frame()
    hexp = F.hex_nut("3/8")
    pl = Plane(origin=(T.CHAIN_X, py + m[0] * v, pz + m[1] * v), x_dir=X, z_dir=(0, m[0], m[1]))
    return _l(pl.location * hexp, spec)


# ---- camshaft locating plate (photo 50.5) ---------------------------------------------------
def locating_plate(spec) -> Part:
    """Three-lobed plate round the camshaft nose. Frame: axis X, rear face x = 0."""
    t = spec.nom("thickness")
    p = _xdisc(spec.nom("outside_diameter") / 2, 0, t)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        p = p + _xdisc(9.0, 0, t, 34 * math.cos(a), 34 * math.sin(a))
        p = p - _xdisc(3.6, -1, t + 1, 34 * math.cos(a), 34 * math.sin(a))
    p = p - _xdisc(spec.nom("inside_diameter") / 2, -1, t + 1)
    return _l(p, spec)


# ---- oil thrower ------------------------------------------------------------------------------
def oil_thrower(spec) -> Part:
    """Dished disc on the crank nose, concave face forward (Haynes Sec 51 para 9)."""
    od, t = spec.nom("outside_diameter"), spec.nom("thickness")
    prof = [(spec.nom("inside_diameter") / 2, 0), (od / 2 - 6, 0), (od / 2, 4.0), (od / 2, 4.0 + t),
            (od / 2 - 6 - t * 0.4, t), (spec.nom("inside_diameter") / 2, t)]
    return _l(Rot_x(Sh.revolved(prof)), spec)


def Rot_x(p):
    """Turn a part built along Z to lie along +X."""
    return Rot(0, 90, 0) * p


# ---- timing cover -------------------------------------------------------------------------------
def timing_cover(spec) -> Part:
    """Pressed steel cover: scalloped flange, deep dome with radiused edges, oil seal
    housing round the crankshaft and the ignition timing pointers (photo 51.12)."""
    t = spec.nom("sheet_thickness")
    x0 = T.PANEL_FACE + 0.4                                       # on the gasket
    depth = T.COVER_INNER + t - x0
    flange = _yz(T.cover_outline(14.0), x0, t)
    for y, z in T.COVER_SCREWS:
        flange = flange + _xdisc(8.0, x0, x0 + t, y, z)
    dome = _yz(T.cover_outline(0.0), x0, depth)
    try:
        dome = fillet(dome.edges().group_by(Axis.X)[-1], 16.0)
    except Exception:  # noqa: BLE001
        pass
    inner = _yz(T.cover_outline(-t), x0 - 0.5, depth - t + 0.5)
    c = flange + dome - inner
    cy, cz = T.CRANK
    c = c + _xdisc(spec.nom("seal_housing_diameter") / 2, x0 + depth - 2, x0 + depth + 7, cy, cz)
    c = c - _xdisc(22.5, x0, x0 + depth + 10, cy, cz)
    # timing pointers on a tab below the crank (TDC, 5 and 10 deg BTDC)
    tab = _yz([(cy - 34, cz - 42), (cy - 4, cz - 42), (cy - 4, cz - 60), (cy - 34, cz - 60)], x0 + depth - 1, 1.6)
    for k, a in enumerate((0, 5, 10)):
        ang = math.radians(-90 - a * 2.2)
        tip = (cy + 44 * math.cos(ang), cz + 44 * math.sin(ang))
        tab = tab + _yz([(tip[0] - 1.2, tip[1] - 14), (tip[0] + 1.2, tip[1] - 14), tip], x0 + depth - 1, 1.6)
    c = c + tab
    for y, z in T.COVER_SCREWS:
        c = c - _xdisc(3.4, x0 - 1, x0 + 5, y, z)
    return _l(c, spec)


def cover_gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = _yz(T.cover_outline(12.5), T.PANEL_FACE, t) - _yz(T.cover_outline(1.0), T.PANEL_FACE - 1, t + 2)
    for y, z in T.COVER_SCREWS:
        g = g - _xdisc(3.4, T.PANEL_FACE - 1, T.PANEL_FACE + 2, y, z)
    return _l(g, spec)


def cover_seal(spec) -> Part:
    od, id_, w = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("width")
    s = Sh.revolved([(id_ / 2, 0), (od / 2, 0), (od / 2, w), (id_ / 2 + 3, w), (id_ / 2, w - 2)])
    return _l(Rot_x(s), spec)


# ---- crankshaft pulley (photo 51.15) -------------------------------------------------------------
def crank_pulley(spec) -> Part:
    """Single-groove fan belt pulley on a long hub that runs in the cover seal.
    Frame: axis X, rear end of the hub at x = 0."""
    d, hub_l = spec.nom("outside_diameter"), spec.nom("hub_length")
    r = d / 2
    groove_w = spec.nom("groove_top_width")
    disc_x0 = hub_l - 20
    rb = spec.nom("bore") / 2
    prof = [(rb, 0), (21.5, 0), (21.5, disc_x0), (r - 2, disc_x0), (r, disc_x0 + 2),
            (r, disc_x0 + 4), (r - 13, disc_x0 + 4 + (groove_w - 6) / 2), (r - 13, disc_x0 + 4 + (groove_w + 6) / 2),
            (r, disc_x0 + 4 + groove_w), (r, disc_x0 + 6 + groove_w), (r - 2, disc_x0 + 8 + groove_w),
            (24, disc_x0 + 8 + groove_w), (24, hub_l), (rb, hub_l)]
    p = Rot_x(Sh.revolved(prof))
    p = p - Box(hub_l + 2, 4.8, 3.0).moved(Location((hub_l / 2, 0, rb + 1.0)))
    for k in range(3):                                             # drive holes in the web
        a = math.radians(120 * k)
        p = p - _xdisc(6.0, disc_x0 - 1, disc_x0 + 3, 33 * math.cos(a), 33 * math.sin(a))
    return _l(p, spec)


def woodruff_key(spec) -> Part:
    """Half-disc key: length along X, flat face up (+Z) into the hub keyway."""
    L, w = spec.nom("length"), spec.nom("width")
    k = Cylinder(L / 2, w, rotation=(90, 0, 0)) & Box(L, w, L / 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return _l(k, spec)


def lockwasher(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) + Box(8, od / 2 + 6, t, align=(Align.CENTER, Align.MIN, Align.MIN))
    return _l(w, spec)


def nut(size):
    return lambda spec: _l(F.hex_nut(size), spec)


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def packing_washer(spec) -> Part:
    return _l(Rot_x(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness"))), spec)


NUT = {"across_flats": F.across_flats, "thickness": lambda p: probes.bbox_size(p, "z")}

PARTS = {
    "engine.timing.cam-wheel": {"build": cam_wheel},
    "engine.timing.crank-wheel": {"build": crank_wheel},
    "engine.timing.chain": {"build": chain},
    "engine.timing.tensioner-body": {"build": tensioner_body},
    "engine.timing.tensioner-slipper": {"build": tensioner_slipper},
    "engine.timing.tensioner-spring": {"build": tensioner_spring},
    "engine.timing.tensioner-cylinder": {"build": tensioner_cylinder},
    "engine.timing.tensioner-backplate": {"build": tensioner_backplate},
    "engine.timing.tensioner-plug": {"build": tensioner_plug},
    "engine.timing.tensioner-bolt": {"build": bolt("5/16")},
    "engine.timing.tensioner-lockwasher": {"build": tensioner_lockwasher},
    "engine.timing.locating-plate-washer": {"build": spring_washer},
    "engine.timing.locating-plate": {"build": locating_plate},
    "engine.timing.locating-plate-screw": {"build": bolt("1/4")},
    "engine.timing.cam-nut": {"build": nut("5/8"), "probes": NUT},
    "engine.timing.cam-lockwasher": {"build": lockwasher},
    "engine.timing.packing-washer": {"build": packing_washer},
    "engine.timing.oil-thrower": {"build": oil_thrower},
    "engine.timing.cover": {"build": timing_cover},
    "engine.timing.cover-gasket": {"build": cover_gasket},
    "engine.timing.cover-seal": {"build": cover_seal},
    "engine.timing.cover-screw": {"build": bolt("1/4")},
    "engine.timing.crank-pulley": {"build": crank_pulley},
    "engine.timing.pulley-bolt": {"build": bolt("5/8")},
    "engine.timing.pulley-lockwasher": {"build": lockwasher},
    "engine.timing.crank-key": {"build": woodruff_key},
    "engine.timing.cam-key": {"build": woodruff_key},
}
