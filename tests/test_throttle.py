"""Throttle and choke controls (P3b): the layout keeps the Haynes clearances and the parts meet where they join."""
import math

from mgb import carb_layout as K, throttle_layout as T

IN = 25.4


def test_fast_idle_gap_is_the_haynes_feeler():
    # Sec 21 para 11: 0.012 in feeler between the shaft lever's stop and the choke interconnecting spindle
    assert abs(T.FAST_IDLE_GAP - 0.012 * IN) < 1e-9


def test_pedal_cable_end_lines_up_with_the_guide():
    assert T.CABLE_END[1] == T.GUIDE[1] and T.CABLE_END[2] == T.GUIDE[2]
    assert T.CABLE_END[0] < T.CAB < T.GUIDE[0] + 1e-9


def test_cables_start_on_the_bracket_over_their_levers():
    fx, fy, fz = T.THROTTLE_FERRULE
    assert (fx, fy) == (T.ACCEL_LEVER_X + T.SWIVEL_DX, T.ACCEL_PIN[0])
    cx, cy, cz = T.CHOKE_FERRULE
    assert (cx, cy) == (T.CHOKE_LEVER_X + T.TRUNNION_DX, T.ROD[0])
    assert T.THROTTLE_OUTER[0][:2] == (fx, fy) and T.CHOKE_OUTER[0][:2] == (cx, cy)


def test_throttle_spindles_reach_the_couplings():
    assert T.CLAMP_X[0] < T.SPINDLE_END < T.CLAMP_X[1]
    assert T.CLAMP_X[0] < T.SHAFT_HALF < T.CLAMP_X[1]


def test_choke_rod_ends_in_its_clamps():
    for xc in K.CARB_X:
        lever_face = abs(xc) - T.JET_LEVER_DX - T.JET_LEVER_T / 2 - 0.5
        assert lever_face - T.ROD_CLAMP_W < T.ROD_HALF < lever_face


def test_cable_runs_have_no_tight_kinks():
    for pts in (T.THROTTLE_OUTER, T.CHOKE_OUTER):
        for a, b, c in zip(pts, pts[1:], pts[2:]):
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - b[i] for i in range(3)]
            cos = sum(p * q for p, q in zip(u, v)) / (math.hypot(*u) * math.hypot(*v))
            assert cos > -0.2, (a, b, c)
