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

Fore-aft positions written as numbers in this module (the tables, the stations and the x values quoted in the
comments) are body stations: the frame the body was drawn in, with the front wheel axis at x 150. They are turned into
car x with mgb.car_layout bx()/bxt() (P12 moved the engine back in the body to Oliver's scan; the body did not change).
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


bx, bxt = CL.bx, CL.bxt


def bxv(table):
    """A table [(key, station)] whose values are body stations: values in car x."""
    return [(k, bx(v)) for k, v in table]


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
TOP_C = bxt([(830.0, 560.0), (785.0, 628.0), (755.0, 655.0), (715.0, 673.0), (660.0, 690.0), (600.0, 716.0), (500.0, 756.0),
         (424.0, 778.0), (300.0, 795.0), (150.0, 814.0), (0.0, 833.0), (-100.0, 846.0), (-200.0, 859.0), (-392.0, 883.0),
         (-453.0, 888.0), (-530.0, 898.0), (-605.0, 909.0), (-700.0, 912.0),   # QA fix 1: the scuttle rises from the bonnet's
         # rear edge (x -453) to the screen base at x -605 (Oliver's keyframes kf076/kf088/kf092 triangulated on the SfM
         # cameras: the scuttle vent's top 908 above the road at x -475; the scan's paint 895-905 by the vent, lower
         # outboard)
         (-900.0, 905.0), (-1300.0, 880.0), (-1650.0, 864.0),
         (-1900.0, 886.0), (-2100.0, 896.0), (-2350.0, 879.0), (-2550.0, 872.0), (-2650.0, 866.0),   # QA: Oliver's scan
         (-2750.0, 836.0), (-2850.0, 830.0), (-2950.0, 780.0), (-3050.0, 700.0)])   # (the tail itself: DECK_H and TAIL_C)
# Wing crown / shoulder line (the side's top edge): the front wing crowns over the headlamps (photo 29 silhouette
# X 567 h 729 at the hood front, 777 at X 372, 829 at X 48), the waist along the doors (h 849), the rear wings rising
# a little to the deck and falling to the lamp plinths (h 803 at the plinth's top corner, X -2774).
CROWN_H = bxt([(730.0, 680.0), (672.0, 730.0), (645.0, 739.0), (600.0, 745.0), (540.0, 752.0), (470.0, 760.0),
           (372.0, 776.0), (178.0, 806.0), (48.0, 824.0), (-82.0, 836.0), (-277.0, 846.0), (-500.0, 851.0),
           (-700.0, 852.0), (-1000.0, 860.0), (-1200.0, 863.0), (-1620.0, 866.0), (-1900.0, 878.0), (-2050.0, 884.0),
           (-2200.0, 876.0), (-2450.0, 857.0),   # waist +11 and rear wing tops +16..24 (QA: Oliver's scan; profile 29 at the rear)
           (-2600.0, 850.0), (-2700.0, 844.0), (-2780.0, 834.0), (-2860.0, 795.0), (-2950.0, 725.0)])   # the rear wings stand
# proud of the boot lid right back to the lamp plinths' top corners (Oliver's scan, sections every 50 mm; photos 23, 24)
CROWN_Y = bxt([(700.0, BL.HEADLAMP_Y), (560.0, BL.HEADLAMP_Y + 2.0), (300.0, 610.0), (0.0, 628.0), (-400.0, 655.0),
           (-700.0, 690.0), (-1620.0, 692.0), (-2200.0, 682.0), (-2780.0, BL.REAR_LAMP_Y), (-2950.0, BL.REAR_LAMP_Y)])
CROWN_S = mono(bxt([(700.0, 88.0), (300.0, 85.0), (-300.0, 95.0), (-700.0, 120.0), (-2200.0, 120.0), (-2780.0, 75.0)]))
# Plan: half-width at the strip line (the widest), the shoulder half-width, the lower edge tuck-under.
W_M = mono(bxt([(831.0, 380.0), (790.0, 520.0), (760.0, 600.0), (720.0, 664.0), (660.0, 702.0), (613.0, 716.0),
       (500.0, 738.0), (350.0, 754.0), (200.0, HALF_W), (-2250.0, HALF_W), (-2400.0, 753.0), (-2500.0, 742.0),
       (-2600.0, 731.0), (-2700.0, 716.0), (-2800.0, 697.0), (-2860.0, 688.0), (-2930.0, 680.0), (-2990.0, 668.0),
       (-3060.0, 645.0)]))   # the rear wings taper in plan to the lamp plinths, the lamps at the body's outer corners (Oliver's
# scan at the strip height, both sides within 5-10 mm: 752 at x -2400, 730 at -2600, 695 at -2800; photos 14, 24)
W_TUMBLE = mono(bxt([(700.0, 40.0), (500.0, 52.0), (0.0, 62.0), (-700.0, 70.0), (-2200.0, 72.0), (-2600.0, 58.0), (-2800.0, 42.0)]))
W_TUCK = mono(bxt([(800.0, 120.0), (600.0, 100.0), (300.0, 70.0), (0.0, 60.0), (-2300.0, 60.0), (-2600.0, 50.0), (-2900.0, 38.0)]))
H_M = BL.BODY_WIDEST_H                      # widest point (by the chrome strip)
SHOULDER_K = 105.0                          # blend radius where the side rolls into the top
# Lower edge of the skin (trim line): front valance bottom, sills, rear valance (P11a REAR_PANEL_LOW_Z).
Z_B = mono(bxt([(831.0, 250.0), (480.0, 252.0), (300.0, 262.0), (0.0, 270.0), (-260.0, 272.0), (-650.0, 273.0),
       (-760.0, 262.0), (-1600.0, 262.0), (-1760.0, 272.0), (-1950.0, 300.0), (-2300.0, 340.0), (-2480.0, 362.0),
       (-2650.0, 372.0), (-2780.0, 365.0), (-2880.0, 345.0), (-3060.0, 345.0)]))
# QA fix 1: the front wing's lower edge between the arch and the door 270-275 above the road (front 21: kf044
# back-projected, kf016); under the door the sill shows only about 60 mm below the door before it turns under, its
# lowest visible point 290-310 (sides-glass 13: kf015, kf044, kf048; the scan is reflection-corrupted there), so the
# skin rolls under on SILL_ROLL there; behind the rear arch the wing's lower edge at about 360-375, bumper-bottom level
# (rear 9: kf066, kf068); the rear valance turns under (TAIL_C) so it shows to about 385 from behind (photo 25) and ends
# 345 above the road at x -2880 (the scan from (x -2960, h 420) curving to (-2880, 345)), closing the view of the tank.
SILL_ROLL = mono(bxt([(-230.0, 0.0), (-560.0, 0.0), (-720.0, 50.0), (-1620.0, 50.0), (-1800.0, 0.0)]))   # roll radius
BLOB_BOTTOM = 160.0                         # the implicit body continues under the trim line to here
# Bonnet swage: none (QA fix 1, front 10 and 25: the real bonnet is smooth, no centre rib, its front lip a smooth arc
# over the grille; the earlier raised strip made a V-shaped dent where it met the nose's roll). The bonnet's centre
# line rises at an even slope from x 300 to its rear edge (the earlier flat zone over x 300..0 and the steeper rise
# behind it read as a wavy band across the bonnet in kf027 and kf083).
RIB_A = mono(bxt([(760.0, 0.0), (-300.0, 0.0)]))
RIB_W = 34.0
# Bonnet's edge valley: the bonnet's sides fall a little toward the shut lines inboard of the crowns.
BONNET_DROP = mono(bxt([(745.0, 0.0), (600.0, 14.0), (300.0, 12.0), (0.0, 6.0), (-300.0, 0.0)]))

# ---- nose (front surface x as a function of |y| and height) --------------------------------------------------------
# Centre: the grille surround's front (photo 29 X 758 corrected), the plate and valance below rolling back under,
# the bonnet's front edge above rolling back over the grille.
NOSE_C = mono(bxv([(120.0, 520.0), (200.0, 610.0), (250.0, 678.0), (300.0, 722.0), (340.0, 741.0), (380.0, 750.0),
          (440.0, 756.0), (589.0, 760.0), (610.0, 776.0), (635.0, 776.0), (655.0, 765.0), (680.0, 735.0), (720.0, 640.0),
          (800.0, 380.0)]))   # the nose rolls over the grille in a fuller, blunter lip (Oliver's scan: 25-45 mm further forward at h 600-650)
NOSE_PLAN_C = mono([(0.0, 0.0), (300.0, 4.0), (445.0, 30.0), (520.0, 78.0)])
# Wing fronts at the headlamp line (|y| 585) before the lamp recess: the face below the lamp down to the flasher and
# bumper (Oliver's photos 05, 20), the hood over the lamp (photo 29 hood front X 567-613, h 729-752).
NOSE_W = bxv([(120.0, 520.0), (200.0, 600.0), (260.0, 640.0), (330.0, 665.0), (420.0, 680.0), (495.0, 688.0),
          (540.0, 682.0), (575.0, 662.0), (600.0, 645.0), (640.0, 637.0), (700.0, 636.0), (730.0, 632.0),
          (750.0, 618.0), (770.0, 578.0), (800.0, 480.0)])
NOSE_PLAN_W = mono([(470.0, -40.0), (585.0, 0.0), (650.0, 14.0), (700.0, 38.0), (740.0, 90.0), (770.0, 170.0),
                     (800.0, 290.0)])
NOSE_ZONE = (440.0, 540.0)                  # |y| over which the centre profile gives way to the wing profile
NOSE_K = 150.0                             # blend of the nose into the sides
NOSE_K_LAMP = 150.0                         # and at the headlamp's height (QA fix 1: a tighter blend was tried; the scan keeps 150)
NOSE_TOP_K = 80.0                          # and into the top (the bonnet's front roll)
LAMP_Y, LAMP_H = BL.HEADLAMP_Y, ag(BL.HEADLAMP_Z)
NACELLE_X = BL.HEADLAMP_RIM_X - 14.0        # recess floor round the rim: P10's bowl flange plane
NACELLE_R = (100.0, 128.0)                  # recess flat to this radius, back to the wing front by the second
HOOD_LIP = 0.0                              # the wing's hood stands this far ahead of the rim at the top
# QA fix 1 (front 19): no raised ring and no crease from the rim's top-inboard to the bonnet: Oliver's scan round the
# rims (radii 100-210 every 30 deg, both sides alike) has the wing's face just above and above-inboard of the rim about
# 580, some 30 mm behind the earlier model, and the hood over the lamp fuller (566 at 125 above the centre), so the face
# is pulled back round the top of the rim (a negative swell); the crown over the lamp is left as it was (the front
# reviewer's side elevation matches it).
COWL_A = -35.0                              # mm (negative: back) at its peak
COWL_DIR = 100.0                            # deg from outboard (0) toward the top (90) where it is largest
COWL_R = (100.0, 120.0, 170.0)              # full from the recess edge to the second radius, gone by the third

# ---- tail (rear surface x as a function of |y| and height) ---------------------------------------------------------
TAIL_PANEL_X = U.REAR_PANEL_X               # rear panel face behind the number plate (P11a, moved by P11b)
TAIL_C = [(150.0, TAIL_PANEL_X + 200.0), (250.0, TAIL_PANEL_X + 130.0), (295.0, TAIL_PANEL_X + 100.0), (320.0, TAIL_PANEL_X + 88.0),
          (345.0, TAIL_PANEL_X + 78.0), (385.0, TAIL_PANEL_X + 32.0), (420.0, TAIL_PANEL_X + 7.0), (460.0, TAIL_PANEL_X), (600.0, TAIL_PANEL_X - 2.0), (640.0, TAIL_PANEL_X + 3.0), (665.0, TAIL_PANEL_X + 9.0),
          (690.0, TAIL_PANEL_X + 36.0), (720.0, TAIL_PANEL_X + 62.0), (745.0, TAIL_PANEL_X + 84.0), (770.0, TAIL_PANEL_X + 100.0),
          (790.0, TAIL_PANEL_X + 130.0), (806.0, TAIL_PANEL_X + 168.0), (820.0, TAIL_PANEL_X + 230.0),
          (840.0, TAIL_PANEL_X + 330.0)]   # QA fix 1 (rear 2): the boot lid rounds off higher and further back, through
# about (x -2853, h 770) (between the handle's evidence in photo 25 and kf062, x -2880, and Oliver's scan at h 760-780
# away from the reflection-lifted centre line: x -2780..-2850), its rear edge at 665
# (the boot lid's rear falls with the lamp plinths' rake: nothing stands behind the lamps above the bumper in the side
#  view, profile photo 29)
# Wing ends (photo 29: the lamp plinth raked about 31 deg, top corner X -2774 h 803, foot X -2930 h 570, the wing end
# under it X -2943 at h 511); the wing ends stand forward of the rear panel above the bumper ("wing kick").
TAIL_W = [(150.0, TAIL_PANEL_X + 85.0), (300.0, TAIL_PANEL_X + 14.0), (420.0, TAIL_PANEL_X + 8.0),
          ] + bxv([(511.0, -2950.0), (548.0, -2947.0), (580.0, -2940.0), (691.0, -2869.0), (760.0, -2824.0), (830.0, -2779.0),
          (870.0, -2735.0), (910.0, -2680.0)])   # plinth raked 33 deg through the lamp, its top corner at h 830 (Oliver's scan)
TAIL_PLAN = mono([(0.0, 0.0), (500.0, 2.0), (650.0, 4.0), (685.0, 9.0), (705.0, 20.0), (725.0, 48.0),
                   (750.0, 125.0)])   # square wing ends in plan, crisp outer edge (Oliver's photos 18, 23)
TAIL_CPLAN = mono([(0.0, 0.0), (350.0, 2.0), (420.0, 8.0), (470.0, 18.0), (520.0, 30.0), (560.0, 38.0), (650.0, 50.0)])
# QA fix 1 (rear 17): outboard of the overriders the rear panel rounds forward into the wing ends sooner (Oliver's
# scan at |y| 450-550, h 560-600: x -2893..-2924), which also rounds the boot lid's rear corners in plan; it and the
# wider blend into the wing ends (PLINTH_Y) take out the fold from the lamp top down to the lid's corner (rear 15).
# The valance under the bumper tucks forward and under (rear 9: the scan from (x -2960, h 420) curving to (-2880, 345)).
TAIL_K = 28.0
PLINTH_Y = (BL.REAR_LAMP_Y - 175.0, BL.REAR_LAMP_Y - 55.0)  # wing-end zone (inner and outer edge of the blend)


def crown_h(x):
    return _interp(CROWN_H, x)


def top_c(x):
    return _interp(TOP_C, x)


def w_m(x):
    return _interp(W_M, x)


def z_b(x):
    return _interp(Z_B, x)


TAIL_Z_B = (295.0, bx(-2830.0), 560.0)       # the rear valance's lower edge between the wing ends (h, behind x, inside |y|):
# it comes down below the bumper's silhouette (kf062: a thin red strip under the blade, no tank in view), past the
# scan's last point (x -2880, h 345), its return clear of the tank and the exhaust's rear mounting (x -2788..-2829)


def z_b_xy(X, Y):
    """The skin's lower edge at (x, y): Z_B, lowered between the wing ends at the tail to TAIL_Z_B."""
    h, x0, w = TAIL_Z_B
    zb = _interp(Z_B, X)
    t = _step((x0 - np.asarray(X, float)) / 40.0) * _step((w - np.abs(np.asarray(Y, float))) / 60.0)
    return zb + (np.minimum(zb, h) - zb) * t


BONNET_CAMBER = mono(bxt([(745.0, 26.0), (300.0, 30.0), (-392.0, 32.0), (-700.0, 20.0), (-1650.0, 20.0), (-2100.0, 30.0),
                 (-2400.0, 36.0), (-2900.0, 40.0)]))          # the top's fall from the centre to the crown line where no crown stands proud
# Rear deck and boot lid (Oliver's scan and photos 11, 14, 18, 23, 24, 25; his correction of 5 Nov): the rear wing
# crowns are the highest points; from each crown the surface drops inboard into a dip, and the deck and boot lid stay
# at that level right across between the dips (a camber of only 8 mm), falling gently from the cockpit's rear and
# rounding off at the back to the rear panel along the dips' own curve. The scan's dip heights (its deeper left side;
# the high centre points on the glossy lid are reflection lift) set DECK_H.
DECK_H = bxt([(-2055.0, 880.0), (-2120.0, 876.7), (-2200.0, 870.8), (-2300.0, 860.4), (-2450.0, 842.4), (-2550.0, 830.4),
               (-2650.0, 818.4), (-2700.0, 812.4), (-2740.0, 807.0), (-2780.0, 800.0), (-2850.0, 782.0), (-2900.0, 759.0),
               (-2960.0, 707.0), (-3000.0, 662.0)])
# (QA fix 1 review: a C2 spline with no inflection - the deck strip rounding over from the rim, the lid straight in the
# dip below the crowns, then rounding off at the back - so no transverse ridge shows across the lid; the deck's centre
# 888 at the rim, between the earlier model and the scan's 900-925)
# QA fix 1 (rear 2, cockpit 29): the deck strip behind the cockpit's rear rim (x -2055) stands about 900 above the road
# at the centre (Oliver's scan, both sides alike at |y| 300: 900-920 at x -2050..-2150), falling to the lid's front
# edge; the lid stays flat across and in the dip below the wing crowns, but rounds off higher and further back: about
# 804 at the centre over the lamp tops (x -2780; the lid 20-35 below the lamp tops, Oliver's own words "a bit lower
# than the lights"), through about (x -2853, h 770) (TAIL_C), its rear edge 665 above the road.
DECK_Y = 505.0                              # the deck is flat (8 mm camber) to here, then rises to the wing crowns
DECK_CAMBER = 8.0
DECK_RISE = 0.0075                          # how quickly it climbs to the crowns outboard of DECK_Y (per mm^2)
DECK_X = (bx(-1990.0), bx(-2100.0))                # blends in behind the cockpit's rear


def _smin(a, b, k):
    return -smax(-a, -b, k)


CROWN_KOUT = mono(bxt([(700.0, 0.0034), (300.0, 0.0032), (-700.0, 0.0030), (-1700.0, 0.0032), (-2200.0, 0.0040), (-2900.0, 0.0046)]))


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
    drop = _interp(BONNET_DROP, X) * np.exp(-((Y - _interp(BONNET_W, X)) / 60.0) ** 2)   # along the bonnet's shut lines
    rib = _interp(RIB_A, X) / (1.0 + (Y / RIB_W) ** 8)
    top = top - drop + rib
    w = _step((DECK_X[0] - X) / (DECK_X[0] - DECK_X[1]))
    deck = _interp(DECK_H, X) + DECK_CAMBER * (1.0 - np.minimum(Y / DECK_Y, 1.0) ** 2) \
        + DECK_RISE * np.maximum(Y - DECK_Y, 0.0) ** 2
    return top + w * (_smin(top, deck, 30.0) - top)


def _side_w(X, Hh):
    """Half-width of the side surface at height h: widest at the strip, tumblehome above, tuck-under below."""
    wm = _interp(W_M, X)
    hs = _interp(CROWN_H, X)
    tum = _interp(W_TUMBLE, X)
    tuck = _interp(W_TUCK, X)
    zb = _interp(Z_B, X)
    up = np.clip((Hh - H_M) / np.maximum(hs - H_M, 30.0), 0.0, 3.0)
    dn = np.clip((H_M - Hh) / np.maximum(H_M - zb, 30.0), 0.0, 3.0)
    R = np.maximum(_interp(SILL_ROLL, X), 1e-3)                      # the sill's roll under: a quarter round of radius R
    v = np.clip((zb + R - Hh) / R, 0.0, 1.0)                        # ending on the trim line
    roll = R * (1.0 - np.sqrt(np.maximum(1.0 - v * v * (2.0 - v * v) * 0.98, 0.0)))   # smoothed: level at the top
    return wm - tum * up ** 2 - tuck * dn ** 2.2 - roll


def _nose(Y, Hh):
    """x of the front surface: the grille surround and valance at the centre, the wing fronts outboard with the
    headlamp nacelles recessed round P10's rims under the wing's hood."""
    Y = np.abs(Y)
    xc = _interp(NOSE_C, Hh) - _interp(NOSE_PLAN_C, Y)
    xw = _interp(NOSE_W, Hh) - _interp(NOSE_PLAN_W, Y)
    t = _step((Y - NOSE_ZONE[0]) / (NOSE_ZONE[1] - NOSE_ZONE[0]))
    x = xc + (xw - xc) * t
    # the wing's face round the top of the lamp (COWL_*)
    rho = np.hypot(Y - LAMP_Y, Hh - LAMP_H)
    ang = np.degrees(np.arctan2(Hh - LAMP_H, Y - LAMP_Y))
    a = np.clip(np.cos(np.radians(ang - COWL_DIR)), 0.0, 1.0) ** 1.5
    g = _step((COWL_R[2] - rho) / (COWL_R[2] - COWL_R[1])) * _step((rho - COWL_R[0] + 40.0) / 40.0)
    x = x + COWL_A * a * g
    # headlamp recess
    r0, r1 = NACELLE_R
    w = _step((r1 - rho) / (r1 - r0))
    hood = _step((Hh - LAMP_H - 40.0) / 70.0) * HOOD_LIP
    floor = NACELLE_X + hood * _step((rho - r0 + 10.0) / 30.0)
    return x - np.maximum(x - floor, 0.0) * w


def _tail(Y, Hh):
    """x of the rear surface: the rear panel and boot lid at the centre, the raked wing ends (lamp plinths) at the
    sides, rounded in plan at the corners."""
    Y = np.abs(Y)
    xc = _interp(TAIL_C, Hh) + _interp(TAIL_CPLAN, Y)
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
    k_nose = NOSE_K - (NOSE_K - NOSE_K_LAMP) * _step((140.0 - np.abs(Hh - LAMP_H)) / 80.0)   # tighter round the lamp
    plan = smax(smax(fs, fn, k_nose), fr, TAIL_K)
    ft = Hh - _top(X, Y)
    k_top = SHOULDER_K - (SHOULDER_K - 45.0) * _step((X - bx(480.0)) / 80.0) * _step((Y - 470.0) / 60.0) \
        - (SHOULDER_K - 38.0) * _step((bx(-2100.0) - X) / 300.0)          # crisper rear wing tops into the lamp plinths
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
    return _root(lambda h: F(np.full_like(h, x), np.full_like(h, y), h), 460.0, 1400.0)   # from inside the tail (QA fix 1:
    # the rear valance now turns under above 300)


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
SPINE_X = (bx(250.0), bx(-2600.0))                 # where the arcs start (front, rear)
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
        out = f(np.zeros(n_psi)) > 0                                     # core point already outside (the caps' ends
        if out.any():                                                    # under the tail): back along the ray to the skin
            tn = np.repeat(np.linspace(0.0, -700.0, 141)[:, None], n_psi, axis=1)
            inside = f(tn) < 0
            kn = np.where(inside.any(0), inside.argmax(0), 0)
            a2 = tn[kn, np.arange(n_psi)]                                # inside
            b2 = tn[np.maximum(kn - 1, 0), np.arange(n_psi)]             # outside
            for _ in range(40):
                m = 0.5 * (a2 + b2)
                pos = f(m) > 0
                b2 = np.where(pos, m, b2)
                a2 = np.where(pos, a2, m)
            t = np.where(out & inside.any(0), 0.5 * (a2 + b2), t)
        P[i, :, 0] = x0 + dx * t
        P[i, :, 1] = y0 + dy * t
        P[i, :, 2] = z_of(h0 + dh * t)
    return P


# =====================================================================================================================
# Shut lines and openings (D, profile photo 29 unless stated)
# =====================================================================================================================
# Doors (Fig 12.15): front shut line X -701 up to h 690, then curving rearward under the screen pillar foot to a
# pointed top front corner on the waist (QA fix 1: Oliver's keyframes kf044, kf046 near side and kf016 off side, the
# shut line traced and back-projected on the SfM cameras, both sides within 5 mm); rear shut line X -1623; bottom edge
# 362 above the road; top on the waist; lower corners rounded about R110 (kf048, kf047: the rear lower corner from
# x -1603 h 502 to x -1558 h 385).
DOOR_FRONT_X = bx(-701.0)
DOOR_FRONT_CURVE = mono(bxv([(690.0, -701.0), (720.0, -706.0), (750.0, -713.0), (765.0, -719.0), (786.0, -730.0),
                             (808.0, -744.0), (830.0, -764.0), (850.0, -785.0), (861.0, -803.0)]))   # (h, x)
DOOR_TOP_FRONT_X = bx(-806.0)                 # the shut line across the waist roll, above the pointed corner
DOOR_REAR_X = bx(-1623.0)
DOOR_BOTTOM_H = 362.0
DOOR_TOP_H = 862.0                          # QA: Oliver's scan, the door tops 860 both sides (photo 29 read 849-852)
DOOR_LOWER_R = 110.0                        # radius of the door's lower corners (kf048: about R100-120)
DOOR_REAR_LEAN = 8.0                        # rear shut line leans forward this much from the bottom to the top
DOOR_RECESS = (bx(-1490.0), 780.0, 130.0, 55.0, 13.0)   # pressed oval finger recess under the handle: centre x, h,
# length, height, depth (QA fix 1, sides-glass 9: kf048, kf187, kf188)


def door_front_x(h):
    """x of the door's front shut line at height h above the road (straight below h 690, the curve above it)."""
    h = float(h)
    if h <= DOOR_FRONT_CURVE[0][0]:
        return DOOR_FRONT_X
    if h > DOOR_FRONT_CURVE[-1][0]:
        return DOOR_FRONT_CURVE[-1][1] + (DOOR_TOP_FRONT_X - DOOR_FRONT_CURVE[-1][1]) * min((h - 861.0) / 239.0, 1.0)
    return _interp(DOOR_FRONT_CURVE, h)


# Bonnet (Sec 6; QA fix 1, front 3): front edge on the grille surround's top; rear edge x -453 (the rear corners
# triangulated at x -433/-474, |y| 542, h 872 from kf076+kf081 and kf088+kf092, SfM cameras); sides along the shut
# lines measured on Oliver's scan in plan (half-width about 418 at x 700, 445 at 350, 480 at 0), widening to the rear
# corners.
BONNET_REAR_X = bx(-453.0)
BONNET_FRONT_X = bx(768.0)                     # at the centre, on the nose lip over the grille (Oliver's scan); the edge curves back toward the sides
BONNET_W = mono(bxt([(760.0, 410.0), (700.0, 418.0), (600.0, 426.0), (350.0, 445.0), (0.0, 480.0), (-250.0, 510.0),
                     (-453.0, 542.0)]))
BONNET_CORNER_R = (60.0, 22.0)              # front, rear plan corner radii
# Scuttle / front wing seam (bolted wings): from the bonnet's rear corner back to the screen pillar foot (QA fix 1,
# front 22: a fine seam line runs from the bonnet corner to the pillar foot in Oliver's kf076), then along the scuttle
# side; and the cockpit opening.
WING_SEAM = bxv([(542.0, -453.0), (572.0, -700.0)])        # (|y|, x) at its ends


def wing_seam_y(x):
    """|y| of the scuttle / front wing seam at x (numpy or scalar)."""
    (y0, x0), (y1, x1) = WING_SEAM
    t = np.clip((np.asarray(x, float) - x0) / (x1 - x0), 0.0, 1.0)
    out = y0 + (y1 - y0) * t
    return float(out) if np.ndim(out) == 0 else out


WING_SEAM_Y = WING_SEAM[-1][0]              # along the scuttle side behind the pillar foot
COCKPIT_FRONT_X = bx(-766.0)                   # scuttle rear lip over the facia (P10 FACIA_X -775)
COCKPIT_REAR_X = bx(-2055.0)                   # rear rim behind the hood stowage (QA fix 1, cockpit 29 / rear: Oliver's
# scan from inside the cockpit, sections at y -350, 0, 385: the rim and rear wall at x -2050..-2080; kf104/kf105 show
# the painted strip from the rim to the boot lid a fraction of the model's earlier one)
COCKPIT_W = bxt([(-766.0, 600.0), (-1000.0, 660.0), (-1650.0, 660.0), (-1850.0, 650.0), (-1960.0, 630.0), (-2055.0, 590.0)])
COCKPIT_CORNER_R = (60.0, 150.0)
# Boot lid (Sec 26; Oliver's photos 14, 18, 24): between the rear wings, front edge behind the rear deck, rear edge
# over the number plate, rounded lower corners.
BOOT_FRONT_X = bx(-2246.0)                  # QA fix 1 (rear deck): the lid's front edge on Oliver's scan
BOOT_W = bxt([(-2246.0, 560.0), (-2600.0, 560.0), (-2950.0, 548.0)])
BOOT_REAR_H = 665.0                         # lower edge of the lid on the tail (QA: photo 25 and kf062, 25-34 above the plate top)
BOOT_CORNER_R = 150.0                       # front corners in plan (kf071, kf105)
BOOT_REAR_R = 90.0                          # lower corners in rear elevation (photo 25, kf058, kf062)
REAR_DECK_SEAM_Y = 575.0                    # rear deck to rear wing welded seams
REAR_PANEL_Y = 560.0                        # rear panel to wing end seams
# Front panels: the valance under the bumper, the grille panel between the nacelles.
FRONT_VALANCE_H = 400.0
GRILLE_PANEL_Y = 470.0
SILL_TOP_H = DOOR_BOTTOM_H - 6.0            # outer sill to wing seam (below the doors)
# Grille opening (Sec 7, early grille; Oliver's photos 10, 15, 27): a wide shallow rounded rectangle, 890 mm across
# the surround, top following the bonnet's front edge, the bumper across its lower edge.
MOUTH_Y = 432.0                             # half-width of the opening (the surround laps 13 mm round it)
MOUTH_TOP_H = 589.0                         # QA: Oliver's photo 15 scaled on the plate
MOUTH_BOT_H = 423.0
MOUTH_END_R = 52.0                          # corner radius
MOUTH_BACK_X = bx(735.0)                       # grille opening's back edge (the grille sits in it)

# Wheel arch openings (profile photo 29): round, the front centred 8 mm behind the hub at hub height, the rear 16 mm
# behind and 32 mm below its hub; both about 370 mm radius.
FRONT_ARCH = (FAX - 8.0, WZ, 371.0)         # (x, z centre, radius)
REAR_ARCH = (RAX - 22.0, WZ - 30.0, 378.0)    # the circle the rear opening replaced (inner structure stations use it)
# The rear opening is a flattened arch, not a circle (Oliver's scan, both sides within 10 mm: 650 above the road over
# the hub, 634 at 150 either side, 587 at 250, 513 at 300, then straight down): half an ellipse 320 x 180 on a line
# 470 above the road, its sides vertical below that, centred over the hub.
REAR_ARCH_E = (RAX + 1.0, z_of(470.0), 320.0, 180.0)   # (x, z of the springing line, half-width, rise)


def arch_level(which, X, Z):
    """Inside the wheel arch opening (negative), in side view (x, car z), roughly in mm near the edge."""
    if which == "front":
        x, z, r = FRONT_ARCH
        return np.hypot(np.asarray(X) - x, np.asarray(Z) - z) - r
    xc, zc, a, b = REAR_ARCH_E
    dx, dz = np.abs(np.asarray(X, float) - xc), np.asarray(Z, float) - zc
    up = (np.sqrt((dx / a) ** 2 + (np.maximum(dz, 0.0) / b) ** 2) - 1.0) * b
    return np.where(dz >= 0.0, up, (dx / a - 1.0) * b)


def arch_outline(which, grow=0.0, z_low=None, n=36):
    """The opening's edge in side view [(x, car z)], grown outward by grow, from the rear foot over the top to the
    front foot, down to z_low (default the springing line / circle centre)."""
    if which == "front":
        x, z, r = FRONT_ARCH
        pts = [(x + (r + grow) * math.cos(math.radians(180.0 - 180.0 * k / n)),
                z + (r + grow) * math.sin(math.radians(180.0 - 180.0 * k / n))) for k in range(n + 1)]
        lo = z
    else:
        xc, zc, a, b = REAR_ARCH_E
        pts = [(xc + (a + grow) * math.cos(math.radians(180.0 - 180.0 * k / n)),
                zc + (b + grow) * math.sin(math.radians(180.0 - 180.0 * k / n))) for k in range(n + 1)]
        lo = zc
    if z_low is not None and z_low < lo:
        pts = [(pts[0][0], z_low)] + pts + [(pts[-1][0], z_low)]
    return pts
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
REAR_BULKHEAD_X = bx(-2080.0)                  # tonneau / boot front wall behind the hood stowage (QA fix 1: Oliver's scan, x -2055..-2080)
SCUTTLE_X = (BONNET_REAR_X, COCKPIT_FRONT_X)


def mouth_outline(grow=0.0, n=8):
    """Grille opening in front elevation as [(y, z)]: a rounded rectangle whose top edge arches a little with the
    bonnet's front edge."""
    # QA fix round 3: the opening follows the chrome surround's outline (mgb.grille_layout, kf027/kf218), 13 mm inside
    # its outer edge so the rolled bar laps the opening all round and no body colour shows between them.
    from mgb import grille_layout as GL
    return [(yy, z_of(hh)) for yy, hh in GL.surround_outline(grow - 13.0, n)]


# ---- windscreen (Fig 12.7-12.9) and hood ------------------------------------------------------------------------------
# Curved screen between two chrome pillars, a top rail, a bottom rail on the scuttle and a centre rod (Fig 12.7 items
# 1-3, 5, 9); pillars 575 mm either side (Oliver's photo 15). QA fix 1 (sides-glass 1, front 8): the screen is not one
# raked plane. Its base curves well forward at the centre (the bottom rail's chrome front measured on Oliver's scan,
# where the chrome is clean, and on kf092, kf046, kf088, kf080 on the SfM cameras: x -590..-600 at the centre, -605 at
# |y| 300, -630 at 400, -650 at 450, -690 at 500, -716 at 540, about -760 at the pillar foot), the glass's lower edge
# about 8 mm behind the rail's front; the top rail's front at x -833, h 1200 at the centre and the corners x
# -925..-935, h 1155-1160. So the glass leans about 43 deg from vertical at the centre and about 30 at the pillars.
SCREEN_HALF_W = 575.0                       # pillar centre lines at the feet
SCREEN_BASE = mono(bxv([(0.0, -605.0), (300.0, -615.0), (400.0, -638.0), (450.0, -658.0), (500.0, -698.0),
                        (540.0, -724.0), (575.0, -764.0), (620.0, -800.0)]))    # (|y|, x of the glass's lower edge)
SCREEN_BASE_UP = 12.0                       # the glass's lower edge above the scuttle (bottom rail and its seal)
SCREEN_TOP_X = bx(-850.0)                   # glass top edge at the centre
SCREEN_TOP_H = 1195.0                       # and its height above the road
SCREEN_TOP_SWEEP = 80.0                     # the top's corners further back (pillar tops at x -925..-935)
SCREEN_TOP_DROP = 38.0                      # and lower (1155-1160 at the pillars)
SCREEN_BASE_SWEEP = BL.WINDSCREEN_BASE_X - SCREEN_BASE[-2][1]    # 159: the base's sweep back from the centre to the pillar foot


def _screen_base_x(y):
    y = abs(float(y))
    tbl = [(-a, b) for a, b in reversed(SCREEN_BASE[1:])] + list(SCREEN_BASE)    # mirrored: level across the centre
    key = tuple(map(tuple, tbl))
    _MONOTONE.add(key)                      # PCHIP: level at the centre, no overshoot
    return _interp(tbl, y)


def screen_base(y):
    """(x, height) of the glass's lower edge at y on the scuttle: the base line in plan, standing SCREEN_BASE_UP on
    the scuttle's surface."""
    x = _screen_base_x(y)
    return (x, top_h(x, min(abs(y), SCREEN_HALF_W)) + SCREEN_BASE_UP)


def screen_top(y):
    t = (abs(y) / SCREEN_HALF_W) ** 2
    return (SCREEN_TOP_X - SCREEN_TOP_SWEEP * t, SCREEN_TOP_H - SCREEN_TOP_DROP * t)


SCREEN_RAKE_DEG = math.degrees(math.atan2(BL.WINDSCREEN_BASE_X - SCREEN_TOP_X, SCREEN_TOP_H - ag(BL.WINDSCREEN_BASE_Z)))


def pillar_rake():
    """Tangent of the screen pillar's lean (its glass edge from the foot to the top at the side)."""
    (xb, hb), (xt, ht) = screen_base(SCREEN_HALF_W), screen_top(SCREEN_HALF_W)
    return (xb - xt) / (ht - hb)


def screen_pt(y, v):
    """Glass surface point at y and fraction v up from the base: car (x, y, z)."""
    (xb, hb), (xt, ht) = screen_base(y), screen_top(y)
    return (xb + (xt - xb) * v, y, z_of(hb + (ht - hb) * v))
