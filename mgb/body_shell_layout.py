"""Body shell datums (P11b): the outer surface of the 1962-67 "pull-handle" MGB roadster, the panel shut lines and the
openings, and the inner structure's stations. Car frame (mgb.car_layout: X forward, Y to the car's left, Z up, origin
on the engine centreline at the head joint face). Heights in the tables are above the road (`ag`), converted with
`z_of`.

The outer surface is an implicit body F(x, y, h) < 0 inside, built from height and width functions (the side, the
top with the wing crowns and the bonnet swage, the nose with the headlamp nacelles, the tail with the lamp plinths)
joined by smooth maxima, so the nose and tail roll into the sides and top without creases. mgb.body_shell samples it
along rays from a spine (planes square to the car in the middle, rotating forward and down round the nose and back
and down round the tail) and fits one B-spline face to the samples; the panels are trimmed out of that face.

Sources.
- Published (S): overall length 153.2 in, width 59.9 in, height 49.4 in hood up, wheelbase 91 in, tracks (mgb.car_layout,
  mgexp.com "Dimensions & Weight"; FIA homologation 3016).
- Haynes (H): Ch 12 Sec 1 (printed p216) the welded body and underframe; Sec 18, Figs 12.7-12.9 the windscreen;
  Sec 21, 39, Fig 12.15 the early door with wind-up glass and quarter-light; Sec 34-35, Fig 12.13 the pull handle;
  Sec 6 the bonnet; Sec 7 the early grille; Sec 10, Fig 12.1 the bumpers; Sec 25-26, Fig 12.12 the boot lid.
- Derived (D), "profile photo 29 scaled on the wheelbase": the side elevation of an early pull-handle roadster
  (Oliver's reference 29, a near-orthographic telephoto side view), scaled so its wheel centres are the 91 in
  wheelbase apart (3.244 mm per pixel, wheel centres at pixel (268.5, 530) and (981, 530.5)); centre-plane points
  corrected for their extra depth (camera about 26 m away, eye 1.14 m above the road, from the horizon). The
  overhangs, the top line, the waist, the strip, the door shut lines and bottom, the sill and lower body line, both
  arches, the screen rake and height and the lamp rake come from it.
- Derived (D), "Oliver's photo NN": front and rear elevations and plan proportions from Oliver's own car (photos 05,
  10, 15, 18, 20, 24, 27: telephoto front and rear views scaled on the 198 mm headlamp rim and the 540 mm number
  plate), the headlamp, flasher, grille and overrider positions.
"""
from __future__ import annotations

import functools
import math

import numpy as np

from mgb import body_layout as BL, car_layout as CL, front_suspension_layout as FS, underbody_layout as U

IN = 25.4
G = CL.GROUND_Z
T = 1.0                                     # outer panel thickness (D: 20 swg steel, about 0.9-1.0 mm)
GAP = 4.0                                   # opening panel gaps (doors, bonnet, boot lid)
SEAM = 0.8                                  # welded or bolted seams between fixed panels (drawn as a fine line)


def z_of(h):
    """Car z of a height above the road."""
    return G + h


def ag(z):
    return z - G


_SPLINES = {}
_MONOTONE = set()                            # tables interpolated without overshoot (PCHIP, C1)


def mono(table):
    _MONOTONE.add(tuple(map(tuple, table)))
    return table


def _interp(table, x):
    """Cubic spline (C2, natural ends) through [(x, v)] given in either order, held level beyond the ends.
    Accepts a scalar or a numpy array. (C2 so the paint's highlights run smoothly over the table stations.)"""
    key = tuple(map(tuple, table))
    sp = _SPLINES.get(key)
    if sp is None:
        from scipy.interpolate import CubicSpline, PchipInterpolator
        pts = sorted(table)
        xs = np.array([p[0] for p in pts], float)
        vs = np.array([p[1] for p in pts], float)
        f = PchipInterpolator(xs, vs) if key in _MONOTONE else CubicSpline(xs, vs, bc_type="natural")
        sp = (table, f, xs[0], xs[-1])
        _SPLINES[key] = sp
    _, cs, x0, x1 = sp
    xa = np.clip(np.asarray(x, float), x0, x1)
    out = cs(xa)
    return float(out) if np.ndim(out) == 0 else out


def smooth(a, b, t):
    """Smoothstep from a (t<=0) to b (t>=1); scalar or array."""
    t = np.clip(t, 0.0, 1.0)
    out = a + (b - a) * t * t * (3 - 2 * t)
    return float(out) if np.ndim(out) == 0 else out


def _step(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * t * (t * (6 * t - 15) + 10)       # smootherstep (C2)


def smax(a, b, k):
    """Cubic smooth maximum (C2): exactly max(a, b) where |a - b| > k, a rounded blend inside that band. For two
    perpendicular distance fields it rounds the corner to a fillet of radius about k / 1.76."""
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.maximum(a, b) + h ** 3 * k / 6.0


# ---- datums from earlier phases -----------------------------------------------------------------------------------
FRONT_X, REAR_X, HALF_W = CL.FRONT_X, CL.REAR_X, CL.WIDTH / 2
FAX, RAX, WZ = CL.FRONT_AXLE_X, CL.REAR_AXLE_X, CL.WHEEL_Z
H_WHEEL = ag(WZ)

# =====================================================================================================================
# The body's shape (D, profile photo 29 and Oliver's photos; x car, h above the road, y >= 0)
# =====================================================================================================================
# Top centre line: bonnet (front edge on the grille surround's top, curving up over the radiator's header tank -
# Oliver's photo 28 shows the radiator's top well above the slam panel - and on to the scuttle), scuttle to P10's screen
# base, a nominal deck across the cockpit (cut away), the rear deck and the boot lid falling to the tail.
TOP_C = [(800.0, 560.0), (745.0, 625.0), (720.0, 641.0), (680.0, 668.0), (600.0, 716.0), (500.0, 756.0),
         (424.0, 778.0), (300.0, 795.0), (150.0, 808.0), (0.0, 823.0), (-100.0, 840.0), (-200.0, 856.0), (-392.0, 880.0), (-550.0, 896.0),
         (BL.WINDSCREEN_BASE_X, ag(BL.WINDSCREEN_BASE_Z)), (-900.0, 905.0), (-1300.0, 880.0), (-1650.0, 864.0),
         (-1900.0, 868.0), (-2100.0, 876.0), (-2350.0, 880.0), (-2550.0, 864.0), (-2650.0, 852.0),
         (-2750.0, 836.0), (-2850.0, 765.0), (-2950.0, 690.0), (-3050.0, 600.0)]
# Wing crown / shoulder line (the side's top edge): the front wing crowns over the headlamps (photo 29 silhouette
# X 567 h 729 at the hood front, 777 at X 372, 829 at X 48), the waist along the doors (h 849), the rear wings rising
# a little to the deck and falling to the lamp plinths (h 803 at the plinth's top corner, X -2774).
CROWN_H = [(730.0, 680.0), (672.0, 730.0), (645.0, 739.0), (600.0, 745.0), (540.0, 752.0), (470.0, 760.0),
           (372.0, 776.0), (178.0, 806.0), (48.0, 824.0), (-82.0, 836.0), (-277.0, 846.0), (-500.0, 851.0),
           (-700.0, 852.0), (-1200.0, 852.0), (-1620.0, 855.0), (-1900.0, 860.0), (-2200.0, 862.0), (-2450.0, 855.0),
           (-2600.0, 846.0), (-2700.0, 838.0), (-2780.0, 812.0), (-2860.0, 760.0), (-2950.0, 700.0)]
CROWN_Y = [(700.0, BL.HEADLAMP_Y), (560.0, BL.HEADLAMP_Y + 2.0), (300.0, 610.0), (0.0, 628.0), (-400.0, 655.0),
           (-700.0, 690.0), (-1620.0, 692.0), (-2200.0, 682.0), (-2780.0, BL.REAR_LAMP_Y), (-2950.0, BL.REAR_LAMP_Y)]
CROWN_S = mono([(700.0, 88.0), (300.0, 85.0), (-300.0, 95.0), (-700.0, 120.0), (-2200.0, 120.0), (-2780.0, 75.0)])
# Plan: half-width at the strip line (the widest), the shoulder half-width, the lower edge tuck-under.
W_M = mono([(831.0, 380.0), (790.0, 520.0), (760.0, 600.0), (720.0, 664.0), (660.0, 702.0), (613.0, 716.0),
       (500.0, 738.0), (350.0, 754.0), (200.0, HALF_W), (-2400.0, HALF_W), (-2600.0, 754.0), (-2750.0, 738.0),
       (-2850.0, 718.0), (-2930.0, 690.0), (-2990.0, 640.0), (-3060.0, 520.0)])
W_TUMBLE = mono([(700.0, 40.0), (500.0, 52.0), (0.0, 62.0), (-700.0, 70.0), (-2200.0, 72.0), (-2800.0, 70.0)])
W_TUCK = mono([(800.0, 120.0), (600.0, 100.0), (300.0, 70.0), (0.0, 60.0), (-2300.0, 60.0), (-2600.0, 85.0), (-2900.0, 110.0)])
H_M = ag(BL.SIDE_STRIP_Z)                   # widest point at the chrome strip
SHOULDER_K = 105.0                          # blend radius where the side rolls into the top
# Lower edge of the skin (trim line): front valance bottom, sills, rear valance (P11a REAR_PANEL_LOW_Z).
Z_B = mono([(831.0, 250.0), (480.0, 245.0), (300.0, 246.0), (-260.0, 250.0), (-1000.0, 254.0), (-1700.0, 265.0),
       (-1950.0, 278.0), (-2300.0, 300.0), (-2550.0, 330.0), (-2650.0, 352.0), (-2750.0, 372.0), (-2850.0, 366.0),
       (-3060.0, 345.0)])         # the rear valance comes down behind the bumper (Oliver's photos 18, 24)
BLOB_BOTTOM = 182.0                         # the implicit body continues under the trim line to here
# Bonnet swage: a low raised strip down the middle of the bonnet, continuing the grille badge's centre bar.
RIB_A = mono([(760.0, 6.0), (600.0, 6.0), (100.0, 4.0), (-300.0, 0.0)])
RIB_W = 34.0
# Bonnet's edge valley: the bonnet's sides fall a little toward the shut lines inboard of the crowns.
BONNET_DROP = mono([(745.0, 0.0), (600.0, 14.0), (300.0, 12.0), (0.0, 6.0), (-300.0, 0.0)])

# ---- nose (front surface x as a function of |y| and height) --------------------------------------------------------
# Centre: the grille surround's front (photo 29 X 758 corrected), the plate and valance below rolling back under,
# the bonnet's front edge above rolling back over the grille.
NOSE_C = [(120.0, 520.0), (200.0, 610.0), (250.0, 678.0), (300.0, 722.0), (340.0, 741.0), (380.0, 750.0),
          (440.0, 756.0), (600.0, 757.0), (625.0, 748.0), (645.0, 725.0), (670.0, 680.0), (720.0, 560.0), (800.0, 380.0)]
NOSE_PLAN_C = mono([(0.0, 0.0), (300.0, 4.0), (445.0, 30.0), (520.0, 78.0)])
# Wing fronts at the headlamp line (|y| 585) before the lamp recess: the face below the lamp down to the flasher and
# bumper (Oliver's photos 05, 20), the hood over the lamp (photo 29 hood front X 567-613, h 729-752).
NOSE_W = [(120.0, 520.0), (200.0, 600.0), (260.0, 640.0), (330.0, 665.0), (420.0, 680.0), (495.0, 688.0),
          (540.0, 682.0), (575.0, 662.0), (600.0, 645.0), (640.0, 637.0), (700.0, 636.0), (730.0, 632.0),
          (750.0, 618.0), (770.0, 578.0), (800.0, 480.0)]
NOSE_PLAN_W = mono([(470.0, -40.0), (585.0, 0.0), (650.0, 14.0), (700.0, 38.0), (740.0, 90.0), (770.0, 170.0),
                     (800.0, 290.0)])
NOSE_ZONE = (440.0, 540.0)                  # |y| over which the centre profile gives way to the wing profile
NOSE_K = 150.0                             # blend of the nose into the sides
NOSE_TOP_K = 120.0                          # and into the top (the bonnet's front roll)
LAMP_Y, LAMP_H = BL.HEADLAMP_Y, ag(BL.HEADLAMP_Z)
NACELLE_X = BL.HEADLAMP_RIM_X - 14.0        # recess floor round the rim: P10's bowl flange plane
NACELLE_R = (100.0, 140.0)                  # recess flat to this radius, back to the wing front by the second
HOOD_LIP = 0.0                              # the wing's hood stands this far ahead of the rim at the top

# ---- tail (rear surface x as a function of |y| and height) ---------------------------------------------------------
TAIL_PANEL_X = U.REAR_PANEL_X               # rear panel face behind the number plate (P11a, moved by P11b)
TAIL_C = [(150.0, TAIL_PANEL_X + 120.0), (250.0, TAIL_PANEL_X + 40.0), (330.0, TAIL_PANEL_X + 8.0),
          (420.0, TAIL_PANEL_X), (600.0, TAIL_PANEL_X - 2.0), (640.0, TAIL_PANEL_X + 16.0),
          (690.0, TAIL_PANEL_X + 72.0), (740.0, TAIL_PANEL_X + 124.0), (800.0, TAIL_PANEL_X + 186.0), (880.0, TAIL_PANEL_X + 305.0)]
# (the boot lid's rear falls with the lamp plinths' rake: nothing stands behind the lamps above the bumper in the side
#  view, profile photo 29)
# Wing ends (photo 29: the lamp plinth raked about 31 deg, top corner X -2774 h 803, foot X -2930 h 570, the wing end
# under it X -2943 at h 511); the wing ends stand forward of the rear panel above the bumper ("wing kick").
TAIL_W = [(150.0, TAIL_PANEL_X + 130.0), (300.0, TAIL_PANEL_X + 30.0), (420.0, TAIL_PANEL_X + 10.0),
          (511.0, -2943.0), (570.0, -2930.0), (690.0, -2858.0), (803.0, -2774.0), (880.0, -2700.0)]
TAIL_PLAN = mono([(0.0, 0.0), (500.0, 2.0), (640.0, 6.0), (700.0, 22.0), (740.0, 60.0), (770.0, 120.0),
                   (800.0, 220.0)])
TAIL_K = 60.0
PLINTH_Y = (BL.REAR_LAMP_Y - 85.0, BL.REAR_LAMP_Y - 45.0)   # wing-end zone (inner and outer edge of the blend)


def crown_h(x):
    return _interp(CROWN_H, x)


def top_c(x):
    return _interp(TOP_C, x)


def w_m(x):
    return _interp(W_M, x)


def z_b(x):
    return _interp(Z_B, x)


BONNET_CAMBER = mono([(745.0, 26.0), (300.0, 30.0), (-392.0, 32.0), (-700.0, 20.0), (-1650.0, 20.0), (-2100.0, 30.0),
                 (-2900.0, 30.0)])          # the top's fall from the centre to the crown line where no crown stands proud
CROWN_KOUT = mono([(700.0, 0.0034), (300.0, 0.0032), (-700.0, 0.0030), (-1700.0, 0.0032), (-2200.0, 0.0040), (-2900.0, 0.0046)])


def _top(X, Y):
    """Height of the top surface at (x, |y|): a cambered dome across the centre, the wing crowns as ridges along
    CROWN_Y where they stand above the dome (the front wings), rolling down outboard into the shoulder; the bonnet
    swage on the centre line and a slight valley along the bonnet's shut lines."""
    Y = np.abs(Y)
    c = _interp(TOP_C, X)
    ch = _interp(CROWN_H, X)
    cy = _interp(CROWN_Y, X)
    cs = _interp(CROWN_S, X)
    d0 = np.maximum(c - ch, _interp(BONNET_CAMBER, X))
    dome = c - d0 * (Y / cy) ** 2
    A = ch - (c - d0)                                     # crown above the dome at cy (0 where the crown is the dome)
    inner = dome + A * np.exp(-((Y - cy) / cs) ** 2)
    s0 = -2.0 * d0 / cy                                   # the dome's slope at cy, carried outboard (C1 at the crown)
    u = np.maximum(Y - cy, 0.0)
    outer = ch + s0 * u - _interp(CROWN_KOUT, X) * u ** 2
    top = np.where(Y <= cy, inner, outer)
    drop = _interp(BONNET_DROP, X) * np.exp(-((Y - (cy - 120.0)) / 60.0) ** 2)
    rib = _interp(RIB_A, X) / (1.0 + (Y / RIB_W) ** 8)
    return top - drop + rib


def _side_w(X, Hh):
    """Half-width of the side surface at height h: widest at the strip, tumblehome above, tuck-under below."""
    wm = _interp(W_M, X)
    hs = _interp(CROWN_H, X)
    tum = _interp(W_TUMBLE, X)
    tuck = _interp(W_TUCK, X)
    zb = _interp(Z_B, X)
    up = np.clip((Hh - H_M) / np.maximum(hs - H_M, 30.0), 0.0, 3.0)
    dn = np.clip((H_M - Hh) / np.maximum(H_M - zb, 30.0), 0.0, 3.0)
    return wm - tum * up ** 2 - tuck * dn ** 2.2


def _nose(Y, Hh):
    """x of the front surface: the grille surround and valance at the centre, the wing fronts outboard with the
    headlamp nacelles recessed round P10's rims under the wing's hood."""
    Y = np.abs(Y)
    xc = _interp(NOSE_C, Hh) - _interp(NOSE_PLAN_C, Y)
    xw = _interp(NOSE_W, Hh) - _interp(NOSE_PLAN_W, Y)
    t = _step((Y - NOSE_ZONE[0]) / (NOSE_ZONE[1] - NOSE_ZONE[0]))
    x = xc + (xw - xc) * t
    # headlamp recess
    rho = np.hypot(Y - LAMP_Y, Hh - LAMP_H)
    r0, r1 = NACELLE_R
    w = _step((r1 - rho) / (r1 - r0))
    hood = _step((Hh - LAMP_H - 40.0) / 70.0) * HOOD_LIP
    floor = NACELLE_X + hood * _step((rho - r0 + 10.0) / 30.0)
    return x - np.maximum(x - floor, 0.0) * w


def _tail(Y, Hh):
    """x of the rear surface: the rear panel and boot lid at the centre, the raked wing ends (lamp plinths) at the
    sides, rounded in plan at the corners."""
    Y = np.abs(Y)
    xc = _interp(TAIL_C, Hh)
    xw = _interp(TAIL_W, Hh)
    t = _step((Y - PLINTH_Y[0]) / (PLINTH_Y[1] - PLINTH_Y[0]))
    return xc + (xw - xc) * t + _interp(TAIL_PLAN, Y)


def F(X, Y, Hh):
    """Implicit outer body (negative inside); x car, y car, h above the road; numpy arrays."""
    X = np.asarray(X, float)
    Y = np.abs(np.asarray(Y, float))
    Hh = np.asarray(Hh, float)
    fs = Y - _side_w(X, Hh)
    fn = X - _nose(Y, Hh)
    fr = _tail(Y, Hh) - X
    plan = smax(smax(fs, fn, NOSE_K), fr, TAIL_K)
    ft = Hh - _top(X, Y)
    k_top = SHOULDER_K - (SHOULDER_K - 45.0) * _step((X - 480.0) / 80.0) * _step((Y - 470.0) / 60.0) \
        - (SHOULDER_K - 55.0) * _step((-2100.0 - X) / 300.0)          # crisper rear wing tops into the lamp plinths
    body = smax(plan, ft, k_top)
    fb = BLOB_BOTTOM - Hh
    return smax(body, fb, 60.0)


# ---- scalar probes on the implicit surface (used by the inner parts that follow the skin) ---------------------------
def _root(fn, lo, hi, n=48):
    """First zero of fn on [lo, hi] (fn(lo) < 0 inside): coarse march then bisection."""
    ts = np.linspace(lo, hi, 64)
    v = fn(ts)
    k = np.argmax(v > 0) if (v > 0).any() else len(ts) - 1
    a, b = ts[max(k - 1, 0)], ts[k]
    for _ in range(n):
        m = 0.5 * (a + b)
        if fn(np.array([m]))[0] > 0:
            b = m
        else:
            a = m
    return 0.5 * (a + b)


@functools.lru_cache(maxsize=200000)
def _side_y(x, h):
    return _root(lambda y: F(np.full_like(y, x), y, np.full_like(y, h)), 0.0, 900.0)


@functools.lru_cache(maxsize=200000)
def _top_h(x, y):
    return _root(lambda h: F(np.full_like(h, x), np.full_like(h, y), h), 300.0, 1400.0)


@functools.lru_cache(maxsize=200000)
def _nose_x(y, h):
    return 0.0 + _root(lambda d: F(d, np.full_like(d, y), np.full_like(d, h)), 0.0, 1100.0)


@functools.lru_cache(maxsize=200000)
def _tail_x(y, h):
    return -_root(lambda d: F(-d, np.full_like(d, y), np.full_like(d, h)), 1500.0, 3300.0)


def side_y(x, h):
    """Half-width of the outer surface at x and height h (above the road)."""
    return _side_y(round(float(x), 2), round(float(h), 2))


def top_h(x, y):
    """Height above the road of the outer surface's top at (x, |y|)."""
    return _top_h(round(float(x), 2), round(abs(float(y)), 2))


def nose_x(y, h):
    return _nose_x(round(abs(float(y)), 2), round(float(h), 2))


def tail_x(y, h):
    return _tail_x(round(abs(float(y)), 2), round(float(h), 2))


def nose_x_np(Y, Hh):
    return np.vectorize(nose_x)(Y, Hh)


def tail_x_np(Y, Hh):
    return np.vectorize(tail_x)(Y, Hh)


def w_b(x):
    """Half-width at the skin's lower edge."""
    return side_y(x, z_b(x))


Z_M = H_M

# =====================================================================================================================
# Ray sampling of the surface (mgb.body_shell): the spine runs along the car at SPINE_H, turning down round the nose
# and the tail on arcs; each station's rays fan out in the plane square to the spine.
# =====================================================================================================================
SPINE_H = 470.0
SPINE_X = (250.0, -2600.0)                  # where the arcs start (front, rear)
SPINE_R = 330.0                             # arc radius (the arcs end SPINE_R lower, SPINE_R further out)
PSI_MAX = 128.0                             # rays from the top (0) round to under the body (deg)


def spine_frames(step=25.0, cap_n=36, cap_deg=80.0):
    """[(origin (x, h), up (dx, dh))]: stations from the front arc's end to the rear arc's end."""
    out = []
    xf, xr = SPINE_X
    for k in range(cap_n, 0, -1):          # front arc, from pointing down-forward to square
        p = math.radians(cap_deg * k / cap_n)
        out.append(((xf + SPINE_R * math.sin(p), SPINE_H - SPINE_R * (1 - math.cos(p))), (math.sin(p), math.cos(p))))
    n = int(round((xf - xr) / step))
    for k in range(n + 1):
        out.append(((xf - (xf - xr) * k / n, SPINE_H), (0.0, 1.0)))
    for k in range(1, cap_n + 1):
        p = math.radians(cap_deg * k / cap_n)
        out.append(((xr - SPINE_R * math.sin(p), SPINE_H - SPINE_R * (1 - math.cos(p))), (-math.sin(p), math.cos(p))))
    return out


CORE = (480.0, 140.0, 360.0)                # ray core ellipse: half-width, half-height; half-width at the caps' ends


def sample_grid(n_psi=193, step=25.0, cap_n=36):
    """Points of the outer surface: array (stations, rays, 3) in the car frame, rays from -PSI_MAX (right) to
    +PSI_MAX (left). In each station's plane the rays leave a core ellipse along its normals (so they never cross,
    and the wing crowns cannot shadow the bonnet behind them as they would from a single centre)."""
    frames = spine_frames(step, cap_n)
    th = np.radians(np.linspace(-PSI_MAX, PSI_MAX, n_psi))
    P = np.zeros((len(frames), n_psi, 3))
    A0, Bc, A1 = CORE
    for i, ((ox, oh), (ux, uh)) in enumerate(frames):
        cap = math.degrees(math.asin(min(abs(ux), 1.0))) / 80.0          # 0 square, 1 at the arc's end
        Ac = A0 + (A1 - A0) * cap
        cb, ca = Ac * np.sin(th), Bc * np.cos(th)                        # core point (across, along up)
        nb, na = np.sin(th) / Ac, np.cos(th) / Bc
        L = np.hypot(nb, na)
        nb, na = nb / L, na / L
        x0, y0, h0 = ox + ca * ux, cb, oh + ca * uh
        dx, dy, dh = na * ux, nb, na * uh
        f = lambda t: F(x0 + dx * t, y0 + dy * t, h0 + dh * t)            # noqa: E731
        ts = np.repeat(np.linspace(0.0, 1600.0, 160)[:, None], n_psi, axis=1)
        v = f(ts)
        hit = v > 0
        k = np.where(hit.any(0), hit.argmax(0), len(ts) - 1)
        a = ts[np.maximum(k - 1, 0), np.arange(n_psi)]
        b = ts[k, np.arange(n_psi)]
        for _ in range(40):
            m = 0.5 * (a + b)
            pos = f(m) > 0
            b = np.where(pos, m, b)
            a = np.where(pos, a, m)
        t = 0.5 * (a + b)
        P[i, :, 0] = x0 + dx * t
        P[i, :, 1] = y0 + dy * t
        P[i, :, 2] = z_of(h0 + dh * t)
    return P


# =====================================================================================================================
# Shut lines and openings (D, profile photo 29 unless stated)
# =====================================================================================================================
# Doors (Fig 12.15): front shut line X -695 below the waist with the top front corner rounded back to X -763 under
# the screen pillar; rear shut line X -1623; bottom edge 362 above the road; top on the waist.
DOOR_FRONT_X = -695.0
DOOR_REAR_X = -1623.0
DOOR_BOTTOM_H = 362.0
DOOR_TOP_H = 852.0
DOOR_FRONT_TOP_R = 95.0                     # radius of the door's top front corner (the shut line under the pillar)
DOOR_REAR_LEAN = 8.0                        # rear shut line leans forward this much from the bottom to the top
# Bonnet (Sec 6; Oliver's photos 05, 20, 27): front edge on the grille surround's top, rear edge ahead of the scuttle
# vent, sides along the valley inboard of the wing crowns.
BONNET_REAR_X = -392.0
BONNET_FRONT_X = 752.0                      # at the centre; the edge curves back toward the sides
BONNET_W = [(760.0, 448.0), (600.0, 462.0), (200.0, 474.0), (-392.0, 478.0)]
BONNET_CORNER_R = (60.0, 22.0)              # front, rear plan corner radii
# Scuttle / front wing seam (bolted wings) along the top of the scuttle side, and the cockpit opening.
WING_SEAM_Y = 628.0
COCKPIT_FRONT_X = -766.0                    # scuttle rear lip over the facia (P10 FACIA_X -775)
COCKPIT_REAR_X = -1905.0                    # rear rail behind the hood stowage
COCKPIT_W = [(-766.0, 600.0), (-1000.0, 660.0), (-1650.0, 660.0), (-1800.0, 640.0), (-1905.0, 575.0)]
COCKPIT_CORNER_R = (60.0, 120.0)
# Boot lid (Sec 26; Oliver's photos 14, 18, 24): between the rear wings, front edge behind the rear deck, rear edge
# over the number plate, rounded lower corners.
BOOT_FRONT_X = -2140.0
BOOT_W = [(-2140.0, 560.0), (-2600.0, 560.0), (-2950.0, 548.0)]
BOOT_REAR_H = 640.0                         # lower edge of the lid on the tail
BOOT_CORNER_R = 90.0
REAR_DECK_SEAM_Y = 575.0                    # rear deck to rear wing welded seams
REAR_PANEL_Y = 560.0                        # rear panel to wing end seams
# Front panels: the valance under the bumper, the grille panel between the nacelles.
FRONT_VALANCE_H = 400.0
GRILLE_PANEL_Y = 470.0
SILL_TOP_H = DOOR_BOTTOM_H - 6.0            # outer sill to wing seam (below the doors)
# Grille opening (Sec 7, early grille; Oliver's photos 10, 15, 27): a wide shallow rounded rectangle, 890 mm across
# the surround, top following the bonnet's front edge, the bumper across its lower edge.
MOUTH_Y = 432.0                             # half-width of the opening (the surround laps 13 mm round it)
MOUTH_TOP_H = 596.0
MOUTH_BOT_H = 428.0
MOUTH_END_R = 52.0                          # corner radius
MOUTH_BACK_X = 735.0                        # grille opening's back edge (the grille sits in it)

# Wheel arch openings (profile photo 29): round, the front centred 8 mm behind the hub at hub height, the rear 16 mm
# behind and 32 mm below its hub; both about 370 mm radius.
FRONT_ARCH = (FAX - 8.0, WZ, 371.0)         # (x, z centre, radius)
REAR_ARCH = (RAX - 22.0, WZ - 30.0, 378.0)
ARCH_LIP = 16.0                             # turned-in lip round each opening

# ---- inner structure stations ---------------------------------------------------------------------------------------
BULKHEAD_X = CL.BULKHEAD_X
INNER_WING_Y = BL.INNER_WING_Y
SILL_INNER_Y = U.SILL_Y                     # inner sill faces (P11a)
FLOOR_TOP_Z = U.FLOOR_Z + 1.2
FRONT_LEG_Y = FS.BODY_BOLT_Y                # front chassis leg centre line (P9 crossmember mountings)
FRONT_LEG_W = 76.0
FRONT_LEG_BOTTOM_Z = FS.BODY_FACE_Z
FRONT_LEG_TOP_Z = FS.BODY_LEG_TOP_Z
REAR_BULKHEAD_X = -1955.0                   # tonneau / boot front wall (behind the hood stowage)
SCUTTLE_X = (-392.0, COCKPIT_FRONT_X)


def mouth_outline(grow=0.0, n=8):
    """Grille opening in front elevation as [(y, z)]: a rounded rectangle whose top edge arches a little with the
    bonnet's front edge."""
    from mgb.body_shell import fillet_poly
    w, h0, h1 = MOUTH_Y + grow, MOUTH_BOT_H - grow, MOUTH_TOP_H + grow
    top = [(w * k / 6, h1 + 8.0 * (1 - (k / 6) ** 2)) for k in range(6, -7, -1)]
    pts = [(w, h0)] + top[:1] + top[1:-1] + top[-1:] + [(-w, h0)]
    radii = [MOUTH_END_R + grow] + [MOUTH_END_R + grow] + [0] * (len(top) - 2) + [MOUTH_END_R + grow, MOUTH_END_R + grow]
    out = fillet_poly(pts, radii, n)
    return [(yy, z_of(hh)) for yy, hh in out]


# ---- windscreen (Fig 12.7-12.9) and hood ------------------------------------------------------------------------------
# Curved screen between two chrome pillars, a top rail, a bottom rail on the scuttle and a centre rod (Fig 12.7 items
# 1-3, 5, 9). Base on P10's screen base at the centre, swept back toward the pillar feet at the scuttle sides (photo
# 29: pillar foot X -757 at the door top); raked 45 deg in side view, the top rail 1105-1120 mm above the road
# (photo 29 at the pillar, Oliver's photo 15 at the centre); pillars 575 mm either side (Oliver's photo 15).
SCREEN_HALF_W = 575.0                       # pillar centre lines at the feet
SCREEN_BASE_SWEEP = 57.0                    # base line further back at the sides than at the centre
SCREEN_TOP_H = 1118.0                       # top rail centre above the road
SCREEN_RAKE_DEG = 45.0                      # from vertical
SCREEN_TOP_SWEEP = 100.0


def screen_base(y):
    """(x, height) of the glass's lower edge at y on the scuttle."""
    t = (abs(y) / SCREEN_HALF_W) ** 2
    return (BL.WINDSCREEN_BASE_X - SCREEN_BASE_SWEEP * t, ag(BL.WINDSCREEN_BASE_Z) - 52.0 * t)


def screen_top(y):
    t = (abs(y) / SCREEN_HALF_W) ** 2
    xb, hb = screen_base(0.0)
    rise = SCREEN_TOP_H - hb
    return (xb - rise * math.tan(math.radians(SCREEN_RAKE_DEG)) - SCREEN_TOP_SWEEP * t, SCREEN_TOP_H - 6.0 * t)


def screen_pt(y, v):
    """Glass surface point at y and fraction v up from the base: car (x, y, z)."""
    (xb, hb), (xt, ht) = screen_base(y), screen_top(y)
    return (xb + (xt - xb) * v, y, z_of(hb + (ht - hb) * v))
