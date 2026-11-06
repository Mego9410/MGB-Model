"""Front grille datums (QA fix round 1, front fittings), car frame (mgb.car_layout), heights h above the road.

The early grille's chrome surround as measured on Oliver's car: his registered scan in an orthographic front view
(scratchpad qa-front r2 front_scan, mm grid) and keyframes kf216, kf218-220 (form). The surround is a heavy rolled
chrome bar: its outer edge 435 mm either side of the centre line, the bottom at h 435, the top arching up from h 566
at the ends to h 593 at the centre under the bonnet's lip, with big corner radii (about 45 at the bottom, 70 at the
top). Its section is a round bar about 22 mm across. The body's grille opening (mgb.body_shell_layout mouth_outline)
is bigger than this at the top corners and the bottom; mgb.body_shell_layout can take the opening from
surround_outline() when the nose is next reworked.

The slats behind it stand on a 22 mm pitch, about 6 mm of chrome each with rounded fronts and tops (kf029 intensity
profile, kf218, kf220); the MG badge stands proud on the centre bar, its top about level with the bonnet's lip
(scan: h 546-623, about 70 wide); the two club badges stand on brackets from the bottom bar: the Heritage Motor
Centre Gaydon 1924-1999 badge on the off side and the AA badge on the near side (scan: centres y -215 and +190, h
about 505; kf218-220 put them a little higher, near the top bar: h 512 used; about 66 and 70 mm across).
"""
from __future__ import annotations

import math

SURR_HW = 435.0                  # outer half-width
SURR_BOT_H = 435.0               # outer bottom
SURR_TOP_H = (593.0, 566.0)      # outer top at the centre and at the ends
SURR_BAR_R = 11.0                # the rolled bar's section radius
SURR_CORNER_R = (45.0, 70.0)     # outer corner radii, bottom and top
SURR_PROUD = 9.0                 # the bar's front stands this far ahead of the nose skin

SLAT_PITCH = 22.0
SLAT_W = 6.0                     # chrome across the car
SLAT_DEPTH = 18.0                # front to back
SLAT_SET_BACK = 8.0              # slat fronts behind the nose skin

BADGE_H = (546.0, 623.0)         # MG badge bottom point and top
BADGE_W = 70.0
BADGE_PROUD = 26.0               # badge face ahead of the nose skin at the grille's centre (14 ahead of the bonnet lip)

CLUB_BADGES = {                  # name: (y, h of the centre, diameter)
    "hmc": (-215.0, 512.0, 70.0),
    "aa": (190.0, 512.0, 70.0),
}


def top_h(y, grow=0.0):
    """Outer top edge height at y (before the corner rounding), grown by grow."""
    t = min(abs(y) / SURR_HW, 1.0)
    return SURR_TOP_H[0] - (SURR_TOP_H[0] - SURR_TOP_H[1]) * t * t + grow


def surround_outline(grow=0.0, n=8):
    """Front elevation [(y, h)] of the surround's outer edge, grown by grow (negative: inward)."""
    from mgb.body_shell import fillet_poly
    w, b = SURR_HW + grow, SURR_BOT_H - grow
    top = [(w * k / 8, top_h(SURR_HW * k / 8, grow)) for k in range(8, -9, -1)]
    pts = [(w, b)] + top + [(-w, b)]
    rb, rt = max(SURR_CORNER_R[0] + grow, 2.0), max(SURR_CORNER_R[1] + grow, 2.0)
    radii = [rb, rt] + [0.0] * (len(top) - 2) + [rt, rb]
    return fillet_poly(pts, radii, n)


def resample(pts, step):
    """Closed polyline resampled at about `step` spacing."""
    out = []
    m = len(pts)
    for i in range(m):
        a, b = pts[i], pts[(i + 1) % m]
        L = math.dist(a, b)
        k = max(1, int(round(L / step)))
        for j in range(k):
            out.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    return out
