"""Rear fittings on the body's outer skin (QA fix round 1): the boot handle and lock, the boot lid badges, the hood
pegs on the rear deck and the tonneau studs on the rear wing tops. Car frame (mgb.car_layout: X forward, Y to the
car's left, Z up); heights above the road where marked. Every fitting is placed by a fore-aft station on the skin and
takes its height and its square from mgb.body_shell_layout, so it stays on the surface when the shell is refitted.

Derived (D), each by the method in its comment: Oliver's photo 25 (telephoto rear elevation, near-orthographic,
scaled on the 520 x 111 plate, 0.97 px/mm), his photo 06 (the badges square on), the matched keyframes (kf062,
kf071, kf104, kf105, kf173) and the scan's top view (QA rear: qa-rear-deck-plan).
"""
from __future__ import annotations

import numpy as np

from mgb import body_shell_layout as S, car_layout as CL

# ---- boot lid ------------------------------------------------------------------------------------------------------
# Handle and lock (Fig 12.12 items 2, 4): on the lid's rear fall over the plate, centred on the car. Photo 25 and kf062
# put its centre about 770 above the road at x -2905 (QA rear finding 3); it is placed by x so it rides the lid's fall.
BOOT_HANDLE_X = CL.bx(-2905.0)
BOOT_HANDLE_W, BOOT_HANDLE_H = 45.0, 60.0         # the pear-shaped escutcheon (photo 25: 44 x 61 mm)
# Badges (photo 06 square on; photo 25 and the scan's top view for the stations): the chrome MG octagon, 100 mm across
# its flats (photo 25: 103), centred x -2720; the chrome M-G-B letter badge ahead of it, centred x -2655, 58 wide.
BADGE_X = CL.bx(-2720.0)
BADGE_ACROSS = 100.0
SCRIPT_X = CL.bx(-2655.0)

# ---- rear deck and wing tops ------------------------------------------------------------------------------------------
# Hood pegs: two chrome shell-shaped pegs on the rear deck the hood frame's rear rail hooks under (kf071, kf105; the
# scan's top view: x -2156, y +308 and -321). The scan puts them a little over half way (0.53) from the cockpit's rear
# rim (-2055 on the car) to the lid's front edge (-2246); the deck's two edges are still being checked (PLAN), so the
# pegs keep that fraction of whatever deck the shell has.
HOOD_PEG_FRAC = 0.53
HOOD_PEG_Y = 315.0
# Tonneau studs: three a side on the rear wing tops round the cockpit's rear corners (kf071: three on the right, kf105:
# two showing on the left): beside the side rim just ahead of the corner, on the corner, and behind it, each snapped
# onto the rim's outline grown 45 mm (so they follow the cockpit opening if it moves).
TONNEAU_STUD_OFFSET = 45.0
TONNEAU_STUD_AIM = ((CL.bx(-1760.0), 700.0), (CL.bx(-1880.0), 660.0), (CL.bx(-1950.0), 560.0))

def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def skin_normal(x, y, h, d=1.5):
    """Outward unit normal of the outer skin at (x, y, h above the road), in the car frame."""
    g = []
    for k in range(3):
        p, m = [x, y, h], [x, y, h]
        p[k] += d
        m[k] -= d
        g.append((S.F(np.array([p[0]]), np.array([p[1]]), np.array([p[2]]))[0]
                  - S.F(np.array([m[0]]), np.array([m[1]]), np.array([m[2]]))[0]) / (2 * d))
    return _unit(g)


def skin_frame(x, y, h=None, up=(1.0, 0.0, 0.0)):
    """A frame on the skin over (x, y): origin on the top surface (car frame), z out of the skin, y along `up`
    projected into the surface (forward for a badge read from behind, up for the handle), x to the viewer's right.
    Returns (origin, x_dir, y_dir, z_dir) as tuples."""
    if h is None:
        h = S.top_h(x, y)
    n = skin_normal(x, y, h)
    u = np.asarray(up, float)
    v = _unit(u - u.dot(n) * n)
    xd = np.cross(v, n)
    return (float(x), float(y), float(S.z_of(h))), tuple(xd), tuple(v), tuple(n)


def lid_curvature_r(x, y=0.0, dx=25.0, r_max=6000.0):
    """Radius of the top surface's curvature along the car at (x, y) (the lid's fall), for fittings that follow it."""
    h0, h1, h2 = S.top_h(x - dx, y), S.top_h(x, y), S.top_h(x + dx, y)
    d1 = (h2 - h0) / (2 * dx)
    d2 = (h2 - 2 * h1 + h0) / dx ** 2
    if abs(d2) < 1e-6:
        return r_max
    return min(r_max, (1 + d1 * d1) ** 1.5 / abs(d2))


def hood_peg_points():
    """(x, y) of the two hood pegs, left then right."""
    x = S.COCKPIT_REAR_X + HOOD_PEG_FRAC * (S.BOOT_FRONT_X - S.COCKPIT_REAR_X)
    return [(x, HOOD_PEG_Y), (x, -HOOD_PEG_Y)]


def tonneau_stud_points(side):
    """(x, y) of the three tonneau studs on one side (side +1 left, -1 right)."""
    from mgb import body_shell as B
    ring = np.array(B.cockpit_outline(TONNEAU_STUD_OFFSET))
    pts = []
    for ax, ay in TONNEAU_STUD_AIM:
        k = int(np.argmin((ring[:, 0] - ax) ** 2 + (ring[:, 1] - ay) ** 2))
        pts.append((float(ring[k, 0]), side * float(ring[k, 1])))
    return pts
