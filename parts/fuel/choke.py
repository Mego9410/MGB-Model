"""Choke (mixture) control: the facia knob and cable, and the jet linkage on the twin SU HS4s that it pulls.

Haynes Ch 3 Fig 3.10 items 46-72, Fig 3.13, Sec 21, Sec 23 para 22; Ch 12 Sec 47 para 4; parts list plate 108-G2;
Rimmer Bros GRID019709; Oliver's photo 16 (see specs/fuel/choke.yaml). Built in the car frame at mgb.throttle_layout's
datums; the parts used more than once are built locally and placed by `placements()`.

Kinematics as drawn (pushed home): pulling the knob draws the inner up through the abutment, lifting the cable lever
and the interconnecting rod; the lever-and-pin clamps lift the jet levers' outer ends, the levers rock on their pivot
bolts and the links push both jets down. The rod also lifts the throttle shaft lever's stop (fuel.throttle) for the
fast idle.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Rot

from mgb import carb_layout as K, fasteners as F, throttle_layout as T
from mgb.brake_parts import IN, box, chamfered_hex, lab, spring_washer, xcyl, xrev, ycyl, zc
from mgb.poly2d import circle_pts, hull
from parts.fuel.throttle import _bar, _disc, _pan_screw, _small_nut, ferrule

KX, KY, KZ = T.CHOKE_KNOB
X_PANEL = KX - 1.2 - 3.0                       # rear face of the raised centre panel (parts/body/interior.py)
BEZEL_T = 3.0
KNOB_L = 11.0                                  # (specs/fuel/choke.yaml knob length)


# =====================================================================================================================
# the control on the facia
# =====================================================================================================================
def knob(spec) -> Part:
    """Round knob, its face cut with a C (reversed as twisted in photo 16), a skirt and the rod into the bush."""
    r = spec.nom("diameter") / 2
    L = spec.nom("length")
    x0 = X_PANEL - BEZEL_T - T.CHOKE_KNOB_OUT                  # knob's front (bezel side)
    x1 = x0 - L
    k = Location((x1, KY, KZ)) * xrev([(0, 0), (r - 1.2, 0), (r, 1.2), (r, L - 2.0), (r - 2.5, L), (0, L)])
    k = k - xcyl(r - 2.0, x0 - 2.5, x0 + 0.1, KY, KZ) + xcyl(4.0, x0 - 3.0, x0, KY, KZ)   # skirt, hub
    k = k - _c_segments(x1 - 0.1, x1 + 0.5)                     # the C cut in the face (filled white: knob-letter)
    k = k + xcyl(2.4, x0, X_PANEL + 2.0, KY, KZ)                  # rod into the bush
    return lab(k, spec)


def _c_segments(x0, x1, r0=4.8, r1=6.5):
    """Prisms of the knob's C (an arc 270 degrees round, opening toward the car's left), between x0 and x1."""
    from mgb.brake_parts import xprism
    a0, a1 = 135.0 - 360.0 + 90.0, 45.0 + 90.0
    arc, arc_in = circle_pts(0.0, 0.0, r1, 24, a0, a1), circle_pts(0.0, 0.0, r0, 24, a0, a1)
    out = None
    for a, b, c, d in zip(arc, arc[1:], arc_in[1:], arc_in):
        seg = xprism([(KY + a[0], KZ + a[1]), (KY + b[0], KZ + b[1]), (KY + c[0], KZ + c[1]), (KY + d[0], KZ + d[1])], x0, x1)
        out = seg if out is None else out + seg
    return out


def knob_letter(spec) -> Part:
    """The white C filling the groove in the knob's face (photo 16)."""
    x1 = X_PANEL - BEZEL_T - T.CHOKE_KNOB_OUT - KNOB_L
    return lab(_c_segments(x1 + 0.05, x1 + 0.45, 4.9, 6.4), spec)


def control(spec) -> Part:
    """Chrome bezel on the panel, threaded bush through the panel and facia, forward to the outer's crimp."""
    rb = spec.nom("bush_diameter") / 2
    c = Location((X_PANEL - BEZEL_T, KY, KZ)) * xrev([(2.6, 0), (7.0, 0), (9.5, 1.6), (9.5, BEZEL_T), (2.6, BEZEL_T)])
    c = c - box(X_PANEL - BEZEL_T - 0.1, X_PANEL - BEZEL_T + 0.8, KY - 0.6, KY + 0.6, KZ + 4.0, KZ + 9.6)   # twist slot
    c = c + xcyl(rb, X_PANEL, KX + T.CHOKE_BUSH_L - 6.0, KY, KZ)
    c = c + xcyl(rb - 1.2, KX + T.CHOKE_BUSH_L - 6.0, KX + T.CHOKE_BUSH_L, KY, KZ)          # crimp over the outer
    c = c - xcyl(2.5, X_PANEL - BEZEL_T - 1, KX + T.CHOKE_BUSH_L - 8.0, KY, KZ)            # bore for the rod
    for k in range(10):                                                                    # thread grooves
        x = KX + 2.0 + k * 1.6
        c = c - (xcyl(rb + 0.1, x, x + 0.5, KY, KZ) - xcyl(rb - 0.35, x - 0.1, x + 0.6, KY, KZ))
    return lab(c, spec)


def facia_nut(spec) -> Part:
    af = spec.nom("across_flats")
    n = chamfered_hex(af, 4.8) - zc(5.4, -1, 6)
    return lab(Location((KX + 0.8, KY, KZ)) * Rot(0, 90, 0) * n, spec)


def facia_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = xcyl(8.5, KX, KX + t, KY, KZ) - xcyl(5.6, KX - 1, KX + t + 1, KY, KZ)
    for k in range(10):                                                                    # shakeproof teeth
        a = math.radians(36 * k)
        w = w - box(KX - 1, KX + t + 1, KY + 7.0 * math.cos(a) - 0.5, KY + 7.0 * math.cos(a) + 0.5,
                    KZ + 7.0 * math.sin(a) - 0.5, KZ + 7.0 * math.sin(a) + 0.5)
    return lab(w, spec)


def cable_outer(spec) -> Part:
    """Outer on the CHOKE_OUTER route, a ferrule at the carburettor end (the facia end is crimped in the bush)."""
    from mgb.elec_shapes import cable as swept
    pts = T.CHOKE_OUTER
    c = swept(pts, spec.nom("outside_diameter"), 28.0) + ferrule(pts[0], pts[1])
    return lab(c, spec)


def cable_inner(spec) -> Part:
    """Exposed end of the wire: from the abutment down through the trunnion's cross hole."""
    fx, fy, fz = T.CHOKE_FERRULE
    return lab(zc(spec.nom("diameter") / 2, T.CHOKE_TRUNNION_Z - 7.0, fz + 10.0, fx, fy), spec)


def grommet(spec) -> Part:
    """Rubber grommet in the bulkhead hole, its groove gripping the panel."""
    ro = spec.nom("outside_diameter") / 2
    gx, gy, gz = T.CHOKE_GROMMET
    g = Location((T.CAB - 3.0, gy, gz)) * xrev([(3.2, 0), (ro, 0), (ro, 3.0 - 0.05), (ro - 2.2, 3.0 - 0.05),
                                                 (ro - 2.2, 4.25), (ro, 4.25), (ro, 7.0), (3.2, 7.0)])
    return lab(g, spec)


def abutment(spec) -> Part:
    """AHH6734: hex cup on the bracket's flange, the ferrule's seat in it, the thread through the flange."""
    fx, fy, fz = T.CHOKE_FERRULE
    L = spec.nom("length")
    a = Location((fx, fy, fz)) * chamfered_hex(9.5, 6.0) + zc(5.0, fz + 6.0, fz + 8.0, fx, fy)
    a = a + zc(3.0, fz - 7.0, fz, fx, fy)
    a = a - zc(3.35, fz + 2.0, fz + 8.1, fx, fy) - zc(1.2, fz - 8.0, fz + 3.0, fx, fy)
    return lab(a, spec)


def abutment_nut(spec) -> Part:
    fx, fy, fz = T.CHOKE_FERRULE
    z = fz - T.BRACKET_T - 1.0
    n = chamfered_hex(spec.nom("across_flats"), 3.6) - zc(2.8, -1, 5)
    return lab(Location((fx, fy, z)) * Rot(180, 0, 0) * n, spec)


def abutment_washer(spec) -> Part:
    fx, fy, fz = T.CHOKE_FERRULE
    z = fz - T.BRACKET_T
    w = zc(5.0, z - 1.0, z, fx, fy) - zc(3.1, z - 2, z + 1, fx, fy)
    return lab(w - box(fx, fx + 6, fy - 0.4, fy + 0.4, z - 2, z + 1), spec)


# =====================================================================================================================
# jet linkage
# =====================================================================================================================
RY, RZ = T.ROD
EAR_Y = (251.0, 262.0)                         # clamp ears on the inboard side of the rod bore, bolt along z
EAR_BOLT_Y = 256.5
EAR_Z = (RZ - 3.0, RZ + 6.0)


def _clamp_on_rod(x0, x1, extra=None, ear_x=None, bolt_x=None):
    """Split boss on the rod with its two ears toward the engine (a horizontal slot), the bolt's hole along z."""
    ex0, ex1 = ear_x or (x0, x1)
    bx = (x0 + x1) / 2 if bolt_x is None else bolt_x
    c = _disc((RY, RZ), 5.5, "x", x0, x1)
    c = c + box(ex0, ex1, EAR_Y[0], RY, *EAR_Z)
    if extra is not None:
        c = c + extra
    c = c - box(ex0 - 1, ex1 + 1, EAR_Y[0] - 1, RY, RZ - 0.6, RZ + 0.6)
    c = c - xcyl(T.ROD_R + 0.05, min(x0, ex0) - 1, max(x1, ex1) + 1, RY, RZ)
    c = c - zc(2.5, RZ - 7, RZ + 8, bx, EAR_BOLT_Y)
    return c


def cable_lever(spec) -> Part:
    """Fig 3.10 69: clamp on the rod, the plate up to the trunnion's hole."""
    t = spec.nom("thickness")
    x = T.CHOKE_LEVER_X
    arm = _bar([(RY, RZ), (RY, T.CHOKE_TRUNNION_Z)], 8.0, "x", x - t / 2, x + t / 2)
    p = _clamp_on_rod(x - 4.0, x + 4.0, arm)
    p = p - xcyl(3.05, x - 3, x + 3, RY, T.CHOKE_TRUNNION_Z)
    return lab(p, spec)


def _small_bolt_z(d, L, af):
    """Hex bolt along +z from its head's underside (local)."""
    from mgb.brake_parts import hexp
    return hexp(af, 0.35 * af, -0.35 * af) + zc(d / 2, 0.0, L)


def cable_lever_bolt(spec) -> Part:
    d = spec.nom("thread_diameter")
    return lab(_small_bolt_z(d, 14.0, 0.375 * IN), spec)


def cable_lever_nut(spec) -> Part:
    return lab(_small_nut(spec.nom("across_flats"), 3.6, 0.1875 * IN), spec)


def cable_lever_washer(spec) -> Part:
    """3/16 in spring washer (local, from z 0)."""
    t = spec.nom("thickness") * 0.8
    w = zc(4.3, 0.0, t) - zc(2.5, -1, t + 1) - box(0, 5, -0.4, 0.4, -1, t + 1)
    return lab(w, spec)


def trunnion(spec) -> Part:
    """AUE34: brass trunnion through the lever, head on its rear side, the wire through its cross hole, the 5BA
    clamp screw in its front end."""
    x = T.CHOKE_LEVER_X
    z = T.CHOKE_TRUNNION_Z
    p = xcyl(4.2, x - 4.5, x - 1.5, RY, z) + xcyl(3.0, x - 1.5, x + 6.0, RY, z)
    p = p - zc(1.0, z - 5, z + 5, x + T.TRUNNION_DX, RY)
    p = p + xcyl(1.3, x + 6.0, x + 7.5, RY, z) + xcyl(2.4, x + 7.5, x + 9.0, RY, z)
    p = p - box(x + 8.4, x + 9.1, RY - 3, RY + 3, z - 0.35, z + 0.35)
    return lab(p, spec)


def rod(spec) -> Part:
    r = spec.nom("diameter") / 2
    p = xcyl(r, -T.ROD_HALF, T.ROD_HALF, RY, RZ)
    return lab(p, spec)


def _jet_lever_x(xc):
    return xc - K.side(xc) * T.JET_LEVER_DX


def _clamp_x(xc):
    s = K.side(xc)
    face = _jet_lever_x(xc) - s * (T.JET_LEVER_T / 2 + 0.5)
    return sorted((face, face - s * T.ROD_CLAMP_W))


def _clamp_ears(xc):
    """Ears run 3 mm further toward the engine centre than the clamp, the bolt there (clear of the barrel)."""
    x0, x1 = _clamp_x(xc)
    if K.side(xc) > 0:
        return (x0 - 3.0, x1), x0 + 1.5
    return (x0, x1 + 3.0), x1 - 1.5


def rod_clamp(xc):
    def build(spec) -> Part:
        """Fig 3.10 64/65: clamp on the rod, an arm down to the pin in the jet lever's outer hole."""
        x0, x1 = _clamp_x(xc)
        s = K.side(xc)
        py, pz = T.JET_PIN
        arm = _bar([(RY, RZ), (py, pz)], 9.0, "x", x0, x1)
        ears, bx = _clamp_ears(xc)
        p = _clamp_on_rod(x0, x1, arm, ears, bx)
        lx = _jet_lever_x(xc)
        pin_x = sorted((x0 + 0.5 if s < 0 else x1 - 0.5, lx + s * (T.JET_LEVER_T / 2 + 1.2)))
        p = p + xcyl(2.4, pin_x[0], pin_x[1], py, pz)
        return lab(p, spec)
    return build


def jet_lever(xc):
    def build(spec) -> Part:
        """Fig 3.10 46/47: lever (pivot boss, inner hole to the link, outer hole for the clamp's pin, a flanged edge)
        and the link riveted to it, its foot screwed to the jet head's lug."""
        t = spec.nom("thickness")
        s = K.side(xc)
        lx = _jet_lever_x(xc)
        qy, qz = T.JET_PIVOT
        ly, lz = T.JET_LINK_TOP
        py, pz = T.JET_PIN
        a0, a1 = lx - t / 2, lx + t / 2
        p = _bar([(ly - 2.0, lz), (qy, qz + 3.0), (py + 2.0, pz)], 10.0, "x", a0, a1)
        inb = a0 if s > 0 else a1                                                # inboard face
        ring = _disc((qy, qz), 9.0, "x", min(inb, inb - s * 0.6), max(inb, inb - s * 0.6)) - \
            _disc((qy, qz), 6.3, "x", inb - 2.0, inb + 2.0)
        p = p + ring                                                             # pressed ring round the pivot
        p = p - xcyl(3.3, a0 - 1, a1 + 1, qy, qz) - xcyl(2.55, a0 - 1, a1 + 1, py, pz)
        # link
        kx = xc - s * T.JET_LINK_DX
        k0, k1 = kx - T.JET_LINK_T / 2, kx + T.JET_LINK_T / 2
        jy, jz = T.JET_LUG
        link = _bar([(ly, lz), (jy, jz + 10.0)], 8.0, "x", k0, k1) + _bar([(jy, jz + 10.0), (jy, jz)], 5.6, "x", k0, k1)
        link = link - xcyl(1.9, k0 - 1, k1 + 1, jy, jz)
        rivet = xcyl(1.6, min(a0, k0) - 0.8, max(a1, k1) + 0.8, ly, lz)
        rivet = rivet + xcyl(2.6, min(a0, k0) - 1.2, min(a0, k0) - 0.01, ly, lz) + \
            xcyl(2.6, max(a1, k1) + 0.01, max(a1, k1) + 1.2, ly, lz)
        bridge = box(*sorted((a1 if s > 0 else a0, k0 if s > 0 else k1)), ly - 3.0, ly + 3.0, lz - 3.0, lz + 3.0)
        p = p + link + rivet + bridge
        return lab(p, spec)
    return build


def link_screw(spec) -> Part:
    """Fig 3.10 51: small pan-head screw through the link's foot into the jet lug (local, along +z)."""
    return lab(_pan_screw(3.0, spec.nom("length"), 5.6, 1.8), spec)


def pivot_bolt(spec) -> Part:
    return lab(_small_bolt_z(spec.nom("thread_diameter"), spec.nom("length"), 0.375 * IN), spec)


def pivot_tube(spec) -> Part:
    od, L = spec.nom("outside_diameter"), spec.nom("length")
    return lab(zc(od / 2, 0.0, L) - zc(2.5, -1, L + 1), spec)


def pivot_washer(spec) -> Part:
    t = spec.nom("thickness")
    return lab(zc(6.0, 0.0, t) - zc(3.35, -1, t + 1), spec)


def jet_lever_spring(spec) -> Part:
    from mgb.brake_parts import coil
    L = T.JET_LEVER_T * 0 + _SPRING_L
    c = coil(0.8, spec.nom("outside_diameter"), L, 3.5)
    return lab(c, spec)


_SPRING_L = 4.9


def _pivot_stack(xc):
    """x stations inboard from the lever's inner face: washer, spring, washer, bolt head (signed toward inboard)."""
    s = K.side(xc)
    face = _jet_lever_x(xc) - s * T.JET_LEVER_T / 2
    w = 1.0
    st = [face, face - s * w, face - s * (w + _SPRING_L), face - s * (2 * w + _SPRING_L)]
    return s, st


def placements():
    pl = {k: [] for k in ("link-screw", "pivot-bolt", "pivot-tube", "pivot-washer", "jet-lever-spring",
                          "rod-clamp-bolt", "rod-clamp-washer", "rod-clamp-nut")}
    qy, qz = T.JET_PIVOT
    jy, jz = T.JET_LUG
    for xc in (T.FRONT, T.REAR):
        s, st = _pivot_stack(xc)
        toward = Rot(0, 90, 0) if s > 0 else Rot(0, -90, 0)                 # local +z -> outboard (toward the jet)
        kx = xc - s * T.JET_LINK_DX
        pl["link-screw"].append(Location((kx - s * T.JET_LINK_T / 2, jy, jz)) * toward)
        pl["pivot-bolt"].append(Location((st[3], qy, qz)) * toward)
        pl["pivot-tube"].append(Location((st[2], qy, qz)) * toward)
        pl["pivot-washer"] += [Location((st[1], qy, qz)) * toward, Location((st[3], qy, qz)) * toward]
        pl["jet-lever-spring"].append(Location((st[2], qy, qz)) * toward)
        _, xm = _clamp_ears(xc)
        pl["rod-clamp-bolt"].append(Location((xm, EAR_BOLT_Y, EAR_Z[0])))
        pl["rod-clamp-washer"].append(Location((xm, EAR_BOLT_Y, EAR_Z[1])))
        pl["rod-clamp-nut"].append(Location((xm, EAR_BOLT_Y, EAR_Z[1] + 0.8)))
    x = T.CHOKE_LEVER_X
    pl["cable-lever-bolt"] = [Location((x, EAR_BOLT_Y, EAR_Z[0]))]
    pl["cable-lever-washer"] = [Location((x, EAR_BOLT_Y, EAR_Z[1]))]
    pl["cable-lever-nut"] = [Location((x, EAR_BOLT_Y, EAR_Z[1] + 0.8))]
    return pl


FR, RR = T.FRONT, T.REAR
PARTS = {
    "fuel.choke.knob": {"build": knob, "probes": {"diameter": lambda p: p.bounding_box().size.Y}},
    "fuel.choke.knob-letter": {"build": knob_letter},
    "fuel.choke.control": {"build": control},
    "fuel.choke.facia-nut": {"build": facia_nut},
    "fuel.choke.facia-washer": {"build": facia_washer},
    "fuel.choke.cable-outer": {"build": cable_outer},
    "fuel.choke.cable-inner": {"build": cable_inner},
    "fuel.choke.grommet": {"build": grommet, "probes": {"outside_diameter": lambda p: p.bounding_box().size.Y}},
    "fuel.choke.abutment": {"build": abutment},
    "fuel.choke.abutment-nut": {"build": abutment_nut},
    "fuel.choke.abutment-washer": {"build": abutment_washer},
    "fuel.choke.cable-lever": {"build": cable_lever},
    "fuel.choke.cable-lever-bolt": {"build": cable_lever_bolt},
    "fuel.choke.cable-lever-nut": {"build": cable_lever_nut},
    "fuel.choke.cable-lever-washer": {"build": cable_lever_washer},
    "fuel.choke.trunnion": {"build": trunnion},
    "fuel.choke.rod": {"build": rod},
    "fuel.choke.rod-clamp-front": {"build": rod_clamp(FR)},
    "fuel.choke.rod-clamp-rear": {"build": rod_clamp(RR)},
    "fuel.choke.rod-clamp-bolt": {"build": cable_lever_bolt},
    "fuel.choke.rod-clamp-washer": {"build": lambda spec: lab(zc(4.0, 0.0, spec.nom("thickness")) - zc(2.5, -1, 2), spec)},
    "fuel.choke.rod-clamp-nut": {"build": cable_lever_nut},
    "fuel.choke.jet-lever-front": {"build": jet_lever(FR)},
    "fuel.choke.jet-lever-rear": {"build": jet_lever(RR)},
    "fuel.choke.link-screw": {"build": link_screw},
    "fuel.choke.pivot-bolt": {"build": pivot_bolt},
    "fuel.choke.pivot-tube": {"build": pivot_tube},
    "fuel.choke.pivot-washer": {"build": pivot_washer},
    "fuel.choke.jet-lever-spring": {"build": jet_lever_spring},
}
