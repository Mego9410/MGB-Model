"""Timing drive layout, shared by the timing parts, the front plate and the assembly.

Engine frame (mgb.engine_layout). Seen from the front (Haynes Fig 1.25) the camshaft
wheel is up and to the left of the car, the crankshaft wheel below it, and the chain
tensioner presses on the run on the car's right-hand side.

Published figures: duplex chain of 52 pitches at 3/8 in on 20- and 40-tooth wheels
(Steve Strange, "Tuning the B-Series Engine"); chain dimensions to ISO 606 06B-2.
Axial positions and the cover outline are derived (D).
"""
from __future__ import annotations

import math
from pathlib import Path

from mgb import engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parent.parent
EL = E.layout(head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml")))

PITCH = E.CHAIN_PITCH
ROLLER_D = 6.35          # ISO 606 06B
INNER_W = 5.72           # ISO 606 06B, width between inner plates
ROW_PITCH = 10.24        # ISO 606 06B-2, transverse pitch of the two rows
R_CRANK = E.pitch_radius(E.CRANK_TEETH)
R_CAM = E.pitch_radius(E.CAM_TEETH)

CRANK = (0.0, EL.crank_z)                 # (y, z) centres
CAM = (EL.cam_y, EL.cam_z)

BLOCK_FRONT = 226.0                       # block front face (half the block length)
PLATE_FACE = BLOCK_FRONT + 0.8 + 3.2      # front face of the front plate
PANEL_FACE = PLATE_FACE + 1.6             # the pressed timing panel the cover seats on
CHAIN_X = 244.0                           # chain centre plane
COVER_INNER = 270.0                       # inside face of the timing cover dome
COVER_T = 1.6
LOCATING_T = 3.0                          # camshaft locating plate, on the front plate
CAM_HUB_X = PANEL_FACE + LOCATING_T + 0.4 # rear face of the camshaft wheel hub
CRANK_SHOULDER_X = 221.0                  # front of the front main journal (mgb crank model)
PACKING_T = 1.6
CRANK_HUB_X = CRANK_SHOULDER_X + PACKING_T
TENSIONER_V = 30.0                        # tensioner centre, out from the chain pitch line


def tangent_run(side: int):
    """Straight chain run between the wheels on the car's left (+1) or right (-1).

    Returns (point on crank pitch circle, point on cam pitch circle, outward unit normal)."""
    ay, az = CRANK
    by, bz = CAM
    dy, dz = by - ay, bz - az
    c = math.hypot(dy, dz)
    dy, dz = dy / c, dz / c
    ny, nz = -dz, dy                       # normal to the crank-to-cam line, toward the car's right (-Y)
    cos_a = (R_CRANK - R_CAM) / c
    sin_a = math.sqrt(1 - cos_a * cos_a) * -side
    my, mz = cos_a * dy + sin_a * ny, cos_a * dz + sin_a * nz
    return (ay + R_CRANK * my, az + R_CRANK * mz), (by + R_CAM * my, bz + R_CAM * mz), (my, mz)


def chain_path(n: int = E.CHAIN_PITCHES):
    """n roller centres spaced evenly round the pitch-line path of the chain."""
    ta_r, tb_r, m_r = tangent_run(-1)
    ta_l, tb_l, m_l = tangent_run(1)

    def ang(p, c):
        return math.atan2(p[1] - c[1], p[0] - c[0])

    # path: right run crank->cam, round the cam (top), left run cam->crank, round the crank (bottom)
    a_cam0, a_cam1 = ang(tb_r, CAM), ang(tb_l, CAM)
    a_crk0, a_crk1 = ang(ta_l, CRANK), ang(ta_r, CRANK)
    span_cam = (a_cam0 - a_cam1) % (2 * math.pi)          # clockwise over the top
    span_crk = (a_crk0 - a_crk1) % (2 * math.pi)          # clockwise under the bottom
    segs = [("line", ta_r, tb_r), ("arc", CAM, R_CAM, a_cam0, -span_cam),
            ("line", tb_l, ta_l), ("arc", CRANK, R_CRANK, a_crk0, -span_crk)]

    def seg_len(s):
        return math.dist(s[1], s[2]) if s[0] == "line" else abs(s[4]) * s[2]

    total = sum(seg_len(s) for s in segs)
    pts = []
    for k in range(n):
        d = total * k / n
        for s in segs:
            L = seg_len(s)
            if d <= L:
                if s[0] == "line":
                    t = d / L
                    pts.append((s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t))
                else:
                    a = s[3] + s[4] * d / L
                    pts.append((s[1][0] + s[2] * math.cos(a), s[1][1] + s[2] * math.sin(a)))
                break
            d -= L
    return pts, total


def tensioner_point():
    """Where the slipper meets the right-hand run, and the outward direction."""
    ta, tb, m = tangent_run(-1)
    t = 0.42
    return (ta[0] + (tb[0] - ta[0]) * t, ta[1] + (tb[1] - ta[1]) * t), m


def _hull(points):
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def cover_outline(grow: float = 0.0, samples: int = 48):
    """Outline (y, z) of the timing cover: round the camshaft wheel, the crankshaft wheel
    and the tensioner, grown outward by `grow`."""
    (sy, sz), m = tensioner_point()
    circles = [(CAM, R_CAM + 13 + grow), (CRANK, R_CRANK + 22 + grow),
               ((sy + m[0] * TENSIONER_V, sz + m[1] * TENSIONER_V), 40 + grow)]
    pts = []
    for (cy, cz), r in circles:
        for k in range(samples):
            a = 2 * math.pi * k / samples
            pts.append((round(cy + r * math.cos(a), 3), round(cz + r * math.sin(a), 3)))
    return _hull(pts)


def perimeter_points(outline, spacing: float):
    """Points spaced roughly evenly round a closed outline."""
    segs = list(zip(outline, outline[1:] + outline[:1]))
    total = sum(math.dist(a, b) for a, b in segs)
    n = max(3, round(total / spacing))
    out, k, run = [], 0, 0.0
    for a, b in segs:
        L = math.dist(a, b)
        while k < n and k * total / n <= run + L:
            t = (k * total / n - run) / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            k += 1
        run += L
    return out


COVER_SCREWS = perimeter_points(cover_outline(9.0), 46.0)
