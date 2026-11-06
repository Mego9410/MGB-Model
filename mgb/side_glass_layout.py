"""Side glazing datums shared by the quarter-lights and door glass (parts/body/closures.py), the windscreen pillars
(parts/body/screen.py) and the hood's edge (parts/body/hood.py). Car frame (mgb.car_layout); heights h above the
road (mgb.body_shell_layout.z_of).

All D, from Oliver's car (QA fix round 1, sides-glass):
- The quarter-light's outer chrome frame: rear foot x -1032 on the door top and top rear x -1105 at h 1150, the rear
  post leaning back 15 deg (Oliver's body scan, the chrome frame both sides: 15.0 left, 15.5 right; photos 14-16).
- Its front edge and the screen pillar's rear edge: the black strips between them found row by row in kf046 and kf048
  (undistorted, SfM cameras) and ray-cast onto the plane |y| 590: the pillar's rear edge at x -800 (kf048) / -835
  (kf046) at h 917 and -956 / -967 at h 1135-1144, i.e. about -786 at the door top leaning 32.7 deg (the two cameras
  averaged); the quarter-light's front edge 20 mm behind it, the strips between (kf048: 17-24, kf046: 20-22). (The
  reviewer's scan reading of -935 at the top was the top rail's end.)
- The pillar casting's bright outer face in side view runs from the strips forward to the screen glass's edge: kf046
  (4x zoom, ray-cast at |y| 590) glass edge x -820 / strip -851 at h 957, -837 / -873 at h 997, -855 / -890 at h 1035,
  i.e. 31-36 mm across at mid-height, about 54 at h 917 where the foot starts to flare (kf048 agrees, about 35 px); so
  its front edge is the screen's side edge (screen_base / screen_top at the pillar) plus a lip, and the foot flares
  forward to a rounded nose at x about -700 on a black rubber grommet (kf046 ray-cast -715 at h 878; scan chrome to
  -680 at h 880).
"""
from __future__ import annotations

import math

from mgb import body_shell_layout as S

WAIST_H = S.DOOR_TOP_H - 6.0                 # door top inner edge (below the roll) where the glass slot is
GLASS_TOP_H = 1160.0                         # door glass top, 8 mm up inside the hood's edge (P11b QA)
QL_TOP_H = GLASS_TOP_H - 16.0                # quarter-light frame's top-rail centre (outer edge QL_TOP_H + 6: scan 1150)
QL_FRAME_W = 18.0                            # the outer frame's flat chrome band (kf048 full res at 4x: 17-20 mm visible)
QL_BOTTOM_H = S.DOOR_TOP_H - 2.0             # the frame's bottom rail's lower edge on the door top's capping

QL_FRONT_FOOT = (-806.0, S.DOOR_TOP_H)       # outer frame's front edge at the door top (kf046 + kf048 ray-casts)
QL_FRONT_TOP = (-991.0, 1150.0)              # and at the top
QL_REAR_FOOT_X = -1032.0                     # outer frame's rear edge at the door top (scan)
QL_REAR_LEAN_DEG = 15.0                      # the rear post leans back (scan 15.0 / 15.5 deg; photos 14-16 deg)
QL_OUTER_TOP_H = QL_TOP_H + 6.0              # outer frame's top edge (scan 1150-1155)


def ql_front_x(h):
    """x of the quarter-light frame's front (outer) edge at height h."""
    (x0, h0), (x1, h1) = QL_FRONT_FOOT, QL_FRONT_TOP
    return x0 + (x1 - x0) * (h - h0) / (h1 - h0)


def ql_front_lean():
    """Tangent of the front edge's lean back from vertical."""
    (x0, h0), (x1, h1) = QL_FRONT_FOOT, QL_FRONT_TOP
    return (x0 - x1) / (h1 - h0)


def ql_rear_x(h):
    """x of the quarter-light frame's rear (outer) edge at height h: the rear post leaning back 15 deg."""
    return QL_REAR_FOOT_X - (h - S.DOOR_TOP_H) * math.tan(math.radians(QL_REAR_LEAN_DEG))


def ql_post_x(h):
    """Centre line of the rear post (divider), where the door glass's front edge runs in its channel."""
    return ql_rear_x(h) + QL_FRAME_W / 2


# ---- windscreen pillar (side view) ----------------------------------------------------------------------------------
PILLAR_STRIP_GAP = 20.0                      # pillar rear edge ahead of the quarter-light's front edge (the rubber strips)
PILLAR_LIP = 2.0                             # the casting's front edge just ahead of the glass's side edge (kf046)


def pillar_rear_x(h):
    """x of the pillar casting's rear edge at h: parallel to the quarter-light's front, the strips between."""
    return ql_front_x(h) + PILLAR_STRIP_GAP


def screen_edge_x(h):
    """x of the windscreen glass's side edge (at the pillar) at height h, from the screen lines."""
    (xb, hb), (xt, ht) = S.screen_base(S.SCREEN_HALF_W), S.screen_top(S.SCREEN_HALF_W)
    return xb + (xt - xb) * (h - hb) / (ht - hb)


def pillar_front_x(h):
    """x of the pillar casting's front edge at h: just ahead of the glass's side edge, which it holds."""
    return screen_edge_x(h) + PILLAR_LIP


def pillar_width(h):
    return pillar_front_x(h) - pillar_rear_x(h)


SHOE_NOSE_X = -700.0                         # the foot's rounded nose on the wing top (kf046 -715, scan chrome to -680)
SHOE_H = 15.0                                # the shoe's height above its rubber pad at the nose
PAD_T = 3.0                                  # the black rubber pad under the shoe
PILLAR_Y_OUT = S.SCREEN_HALF_W + 17.0        # the pillar's flat outer face (the quarter-light's front edge closes on it)
PILLAR_Y_IN = S.SCREEN_HALF_W - 19.0         # its inner face (the glass's edge is in a channel between them)
