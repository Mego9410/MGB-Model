"""Outer body panels (Haynes Ch 12; the 1962-67 roadster): front wings, grille panel, front valance, bonnet skin,
scuttle top, door skins, outer sills, rear wings, rear deck, boot lid skin and rear panel.

Each panel is the outer surface of mgb.body_shell trimmed to its region and thickened inward 1 mm. Regions are signed
distance fields (negative inside) built from the shut lines in mgb.body_shell_layout: every panel is its nominal
region shrunk by half the gap (4 mm opening gaps at the doors, bonnet and boot lid; 0.8 mm seams between fixed
panels), and its openings (wheel arches, headlamp nacelles, grille opening, wiper spindles, lamp holes) are holes in
the same field, so the trim is exact without solid booleans.

Drawn in place in the car frame. Panels are Compounds of thin solids.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Compound

from mgb import body_layout as BL, body_shell as B, body_shell_layout as S

H = S.z_of
G2 = S.GAP / 2
SM = S.SEAM / 2
LEAD = -1.0         # leaded seams (rear wings to the rear deck and rear panel): the panels lap 1 mm each way so no line shows (QA fix 1, rear 16)


def _l(p, spec):
    p.label = spec.id
    return p


def _cached(name, fn):
    return B.disk_cached(name, fn, extra_sources=("parts/body/panels.py",))


AND, OR, NOT = B.sd_and, B.sd_or, B.sd_not


# ---- nominal regions (at the shut-line centres) -----------------------------------------------------------------------
def side_sd(Y, side, margin=60.0):
    return margin - side * Y


def bonnet_sd(X, Y, Z):
    return AND(B.sd_poly(X, Y, B.bonnet_outline(0.0)), H(S.MOUTH_TOP_H) - Z)


def scuttle_sd(X, Y, Z):
    return AND(X - S.BONNET_REAR_X, (S.COCKPIT_FRONT_X - 40.0) - X, np.abs(Y) - S.wing_seam_y(X), H(700.0) - Z)


def cockpit_sd(X, Y, Z):
    return AND(B.sd_poly(X, Y, B.cockpit_outline(0.0)), H(600.0) - Z)


def grille_panel_sd(X, Y, Z):
    return AND(700.0 - X, np.abs(Y) - S.GRILLE_PANEL_Y, H(S.FRONT_VALANCE_H) - Z, -(bonnet_sd(X, Y, Z) - G2))


def valance_sd(X, Y, Z):
    return AND(640.0 - X, Z - H(S.FRONT_VALANCE_H))


DOOR_XZ = [(x, H(h)) for x, h in B.door_outline_xz(0.0)]


def door_xz_sd(X, Z):
    """The door's outline in side view (negative inside), either side."""
    return B.sd_poly(X, Z, DOOR_XZ)


def door_sd(X, Y, Z, side):
    return AND(door_xz_sd(X, Z), side_sd(Y, side, 300.0))


def sill_sd(X, Y, Z, side):
    return AND(X - (S.DOOR_FRONT_X - G2), (S.DOOR_REAR_X + G2) - X, Z - H(S.SILL_TOP_H), side_sd(Y, side, 300.0))   # under the door only: the
    # wings come down to the bottom ahead of and behind the door (Oliver's photo 09, profile 29)


BOOT_YZ = [(y, H(h)) for y, h in B.fillet_poly([(S.BOOT_W[-1][1], S.BOOT_REAR_H), (S.BOOT_W[-1][1], 1300.0),
                                                   (-S.BOOT_W[-1][1], 1300.0), (-S.BOOT_W[-1][1], S.BOOT_REAR_H)],
                                                  [S.BOOT_REAR_R, 0, 0, S.BOOT_REAR_R], 12)]


def boot_sd(X, Y, Z):
    """The boot lid: its plan outline (rounded front corners) and, seen from behind, the lower edge with its rounded
    corners (QA fix 1, rear 1: the car's lid is a soft rounded rectangle, photo 25, kf058, kf062)."""
    return AND(B.sd_poly(X, Y, B.boot_outline(0.0)), B.sd_poly(Y, Z, BOOT_YZ))


def rear_deck_sd(X, Y, Z):
    return AND(X - (S.COCKPIT_REAR_X + 80.0), (S.BOOT_FRONT_X - 40.0) - X, np.abs(Y) - S.REAR_DECK_SEAM_Y,
               H(700.0) - Z, -(boot_sd(X, Y, Z) - G2))


def rear_panel_sd(X, Y, Z):
    """The rear panel: under the boot lid and round its rounded lower corners."""
    return AND(X - (-2700.0), np.abs(Y) - S.REAR_PANEL_Y, Z - H(S.BOOT_REAR_H + S.BOOT_REAR_R + 40.0), -(boot_sd(X, Y, Z) - G2))


def arch_sd(X, Y, Z, which):
    """Inside the wheel arch opening (negative), on the outer sides only."""
    return AND(S.arch_level(which, X, Z), 380.0 - np.abs(Y))


def circle_yz(X, Y, Z, y, z, r, x_min):
    return AND(np.hypot(Y - y, Z - z) - r, x_min - X)


def circle_xy(X, Y, Z, x, y, r, z_min):
    return AND(np.hypot(X - x, Y - y) - r, z_min - Z)


def headlamp_sd(X, Y, Z):
    """Nacelle openings for P10's bowls: clear of the beam setting screws (92 mm radius), the bowl's 97 mm flange behind
    the face and the 99 mm rim over it."""
    return OR(*[circle_yz(X, Y, Z, s * BL.HEADLAMP_Y, BL.HEADLAMP_Z, 96.0, BL.HEADLAMP_RIM_X - 130.0) for s in (1, -1)])


def sidelamp_sd(X, Y, Z):
    """Stud and lead holes for P10's side and flasher lamps (two studs 22.5 mm either side, the lead between)."""
    out = []
    for s in (1, -1):
        for dy, r in ((-22.5, 2.6), (22.5, 2.6), (0.0, 6.0)):
            out.append(circle_yz(X, Y, Z, s * BL.SIDELAMP_Y + dy, BL.SIDELAMP_Z, r, BL.SIDELAMP_X - 60.0))
    return OR(*out)


def mouth_sd(X, Y, Z):
    return AND(B.sd_poly(Y, Z, S.mouth_outline()), 700.0 - X)


def rear_lamp_sd(X, Y, Z):
    """P10's rear lamp fixings in the wing ends: the two bulb holder holes and the three screw holes."""
    out = []
    for s in (1, -1):
        for dz, dy, r in ((40.0, 0.0, 8.5), (-40.0, 0.0, 8.5), (80.0, 0.0, 2.6), (-10.0, 24.0, 2.6), (-10.0, -24.0, 2.6)):
            zz = BL.REAR_LAMP_Z + dz * math.cos(math.radians(BL.REAR_LAMP_RAKE))   # up the raked plinth (QA fix 1)
            out.append(circle_yz(X, Y, Z, s * (BL.REAR_LAMP_Y + dy), zz, r, -9999.0)
                       + np.maximum(X - (BL.REAR_LAMP_X + 80.0), 0.0))
    return OR(*out)


def wiper_sd(X, Y, Z):
    return OR(*[circle_xy(X, Y, Z, x, y, 9.0, z - 60.0) for x, y, z in BL.WIPER_SPINDLES])


# ---- panels ---------------------------------------------------------------------------------------------------------
def wing_sd(side):
    def f(X, Y, Z):
        keep = AND(side_sd(Y, side), (S.DOOR_FRONT_X - 160.0) - X, -(door_xz_sd(X, Z) - G2))   # round the door's
        # curved front shut line and its rounded lower front corner
        others = OR(bonnet_sd(X, Y, Z) - G2, scuttle_sd(X, Y, Z) - SM, grille_panel_sd(X, Y, Z) - SM,
                    valance_sd(X, Y, Z) - SM, sill_sd(X, Y, Z, side) - SM, cockpit_sd(X, Y, Z),
                    arch_sd(X, Y, Z, "front"), headlamp_sd(X, Y, Z), sidelamp_sd(X, Y, Z))
        return AND(keep, -others)
    return f


def rear_wing_sd(side):
    def f(X, Y, Z):
        keep = AND(side_sd(Y, side), X - (S.DOOR_REAR_X + 160.0), -(door_xz_sd(X, Z) - G2))   # round the door's rear
        # shut line and its rounded lower rear corner
        others = OR(rear_deck_sd(X, Y, Z) - LEAD, boot_sd(X, Y, Z) - G2, rear_panel_sd(X, Y, Z) - LEAD,
                    sill_sd(X, Y, Z, side) - SM, cockpit_sd(X, Y, Z), arch_sd(X, Y, Z, "rear"), rear_lamp_sd(X, Y, Z))
        return AND(keep, -others)
    return f


def recess_sd(X, Y, Z, grow=0.0):
    """The door's finger recess opening in side view (an ellipse), negative inside."""
    xc, hc, L, Hh, _ = S.DOOR_RECESS
    a, b = L / 2 + grow, Hh / 2 + grow
    return (np.sqrt(((X - xc) / a) ** 2 + ((Z - H(hc)) / b) ** 2) - 1.0) * b


def door_skin_sd(side):
    def f(X, Y, Z):
        return AND(door_sd(X, Y, Z, side) + G2, -cockpit_sd(X, Y, Z), -recess_sd(X, Y, Z, -1.0))
    return f


def door_recess(side):
    """The pressed oval finger recess under the handle: a shallow dish (half an ellipsoid shell 1 mm thick) set into
    the skin's opening square to the skin, its lip lapping 1-2 mm behind the opening's edge."""
    import build123d as bd
    xc, hc, L, Hh, dep = S.DOOR_RECESS
    y0 = S.side_y(xc, hc)
    gx = (S.side_y(xc + 5.0, hc) - S.side_y(xc - 5.0, hc)) / 10.0
    gz = (S.side_y(xc, hc + 5.0) - S.side_y(xc, hc - 5.0)) / 10.0
    n = np.array([-gx, 1.0, -gz])
    n /= np.linalg.norm(n)
    outer = bd.scale(bd.Solid.make_sphere(1.0), (L / 2 + 2.0, Hh / 2 + 2.0, dep))
    inner = bd.scale(bd.Solid.make_sphere(1.0), (L / 2 + 1.0, Hh / 2 + 1.0, dep - 1.0))
    top = bd.Box(L + 20.0, Hh + 20.0, dep + 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    dish = (outer - inner) - top                       # the inward half (local z < 0), its lip on local z 0
    xd = np.array([1.0, 0.0, 0.0]) - n * n[0]
    pl = bd.Plane(origin=(xc, y0 - 0.8, H(hc)), x_dir=tuple(map(float, xd)), z_dir=tuple(map(float, n)))
    dish = bd.Location(pl) * dish
    return dish if side > 0 else dish.mirror(bd.Plane.XZ)


def sill_skin_sd(side):
    def f(X, Y, Z):
        return AND(sill_sd(X, Y, Z, side) + SM, -arch_sd(X, Y, Z, "front"), -arch_sd(X, Y, Z, "rear"))
    return f


def bonnet_skin_sd(X, Y, Z):
    return bonnet_sd(X, Y, Z) + G2


def scuttle_skin_sd(X, Y, Z):
    return AND(scuttle_sd(X, Y, Z) + SM, X - (S.BONNET_REAR_X - G2), -cockpit_sd(X, Y, Z), -wiper_sd(X, Y, Z))


def grille_panel_skin_sd(X, Y, Z):
    return AND(grille_panel_sd(X, Y, Z) + SM, -mouth_sd(X, Y, Z))


def valance_skin_sd(X, Y, Z):
    return AND(valance_sd(X, Y, Z) + SM, -arch_sd(X, Y, Z, "front"))


def rear_deck_skin_sd(X, Y, Z):
    return AND(rear_deck_sd(X, Y, Z) + LEAD, -cockpit_sd(X, Y, Z))


def boot_skin_sd(X, Y, Z):
    return boot_sd(X, Y, Z) + G2


def filler_sd(X, Y, Z):
    """The filler neck's hole in the rear panel (P11a fuel_supply_layout FILLER_CAP_*)."""
    from mgb import fuel_supply_layout as FL
    return circle_yz(X, Y, Z, FL.FILLER_CAP_Y, FL.FILLER_TUBE_TOP_Z, FL.FILLER_OD / 2 + 6.0, -9999.0)


def tailpipe_notch_sd(X, Y, Z):
    """The notch in the rear valance's lower edge the tail pipe passes through (QA fix 1 hand-off from the rear
    fittings: the pipe 365 above the road with its top tight to the valance, exhaust_layout TAIL_*): a slot up from the
    edge with a round head 6 mm clear of the pipe."""
    from mgb import exhaust_layout as E
    r = E.PIPE_OD / 2 + 6.0
    head = np.hypot(Y - E.TAIL_Y, Z - E.TAIL_Z) - r
    slot = AND(np.abs(Y - E.TAIL_Y) - r, Z - E.TAIL_Z)
    return AND(OR(head, slot), X - (E.TAIL_ROUTE[1][0] - 20.0))


def rear_panel_skin_sd(X, Y, Z):
    return AND(rear_panel_sd(X, Y, Z) + LEAD, -filler_sd(X, Y, Z), -tailpipe_notch_sd(X, Y, Z))


def _panel(name, sdf):
    def build(spec):
        return _l(_cached(name, lambda: B.skin_sdf(sdf)), spec)
    return build


front_wing = lambda side: _panel(f"front-wing-{side}", wing_sd(side))         # noqa: E731
rear_wing = lambda side: _panel(f"rear-wing-{side}", rear_wing_sd(side))       # noqa: E731
def door_skin(side):
    def build(spec):
        skin = _cached(f"door-skin-{side}", lambda: B.skin_sdf(door_skin_sd(side)))
        return _l(Compound(list(skin.solids()) + [door_recess(side)]), spec)
    return build



sill = lambda side: _panel(f"sill-{side}", sill_skin_sd(side))                 # noqa: E731
bonnet_skin = _panel("bonnet-skin", bonnet_skin_sd)
scuttle = _panel("scuttle", scuttle_skin_sd)
grille_panel = _panel("grille-panel", grille_panel_skin_sd)
front_valance = _panel("front-valance", valance_skin_sd)
rear_deck = _panel("rear-deck", rear_deck_skin_sd)
boot_skin = _panel("boot-skin", boot_skin_sd)
rear_panel = _panel("rear-panel", rear_panel_skin_sd)

PANELS = {
    "front-wing-l": front_wing(1), "front-wing-r": front_wing(-1), "grille-panel": grille_panel,
    "front-valance": front_valance, "bonnet-skin": bonnet_skin, "scuttle": scuttle,
    "door-skin-l": door_skin(1), "door-skin-r": door_skin(-1), "sill-l": sill(1), "sill-r": sill(-1),
    "rear-wing-l": rear_wing(1), "rear-wing-r": rear_wing(-1), "rear-deck": rear_deck, "boot-skin": boot_skin,
    "rear-panel": rear_panel,
}


def _half_width(p):
    bb = p.bounding_box()
    return max(abs(bb.min.Y), abs(bb.max.Y))


PARTS = {
    "body.front.front-wing-l": {"build": front_wing(1), "probes": {"half_width": _half_width}},
    "body.front.front-wing-r": {"build": front_wing(-1), "probes": {"half_width": _half_width}},
    "body.front.grille-panel": {"build": grille_panel},
    "body.front.front-valance": {"build": front_valance},
    "body.front.bonnet-skin": {"build": bonnet_skin},
    "body.front.scuttle": {"build": scuttle},
    "body.doors.skin-l": {"build": door_skin(1), "probes": {"half_width": _half_width}},
    "body.doors.skin-r": {"build": door_skin(-1), "probes": {"half_width": _half_width}},
    "body.structure.outer-sill-l": {"build": sill(1)},
    "body.structure.outer-sill-r": {"build": sill(-1)},
    "body.rear.rear-wing-l": {"build": rear_wing(1), "probes": {"half_width": _half_width}},
    "body.rear.rear-wing-r": {"build": rear_wing(-1), "probes": {"half_width": _half_width}},
    "body.rear.rear-deck": {"build": rear_deck},
    "body.rear.boot-skin": {"build": boot_skin},
    "body.rear.rear-panel": {"build": rear_panel},
}
