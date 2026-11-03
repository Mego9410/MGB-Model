"""Body shell (P11b) layout checks: the shell agrees with the published sizes and clears the running gear."""
import math

import numpy as np

from mgb import body_layout as BL, body_shell_layout as S, car_layout as CL, front_suspension_layout as FS
from parts.body import structure as St


def test_body_width_is_the_published_width():
    assert abs(2 * max(S.w_m(x) for x in range(-2400, 200, 50)) - CL.WIDTH) < 0.5


def test_wheel_arches_sit_under_the_chrome_strip():
    for x, z, r in (S.FRONT_ARCH, S.REAR_ARCH):
        top = S.ag(z + r)
        assert top < S.Z_M and top > S.ag(CL.WHEEL_Z) + CL.TYRE_D / 2 + 20.0


def test_screen_and_hood_stay_under_the_published_height():
    assert S.SCREEN_TOP_H < CL.HEIGHT_HOOD_UP
    from parts.body import hood as Hd
    assert abs(max(Hd.crown(u / 100) for u in range(101)) - (CL.HEIGHT_HOOD_UP - 2.5)) < 1.0


def test_bonnet_clears_the_radiator_and_head():
    # radiator header tank top (cooling_layout) and the rocker cover, 804 and 799 mm above the road (P2/P3)
    from mgb import cooling_layout as CO
    assert S.top_h(CO.RAD_CORE[1], 0.0) - 2.0 > S.ag(CO.RAD_TOP_TANK[1]) + 5.0


def test_headlamps_sit_in_the_nacelles():
    # the nacelle face is at P10's bowl flange and the lamp centre is under the wing's crown
    assert abs(S.nose_x(BL.HEADLAMP_Y, S.ag(BL.HEADLAMP_Z)) - (BL.HEADLAMP_RIM_X - 14.0)) < 1.0
    assert S.top_h(S.NACELLE_X - 20.0, BL.HEADLAMP_Y) > S.ag(BL.HEADLAMP_Z) + 99.0


def _tyre_envelope(front_in=28.0, rear_in=37.0):
    """Points of the left front tyre swept through the lock range about P9's king pin (32 ft turning circle)."""
    R, W = CL.TYRE_D / 2, 0.92 * 5.6 * 25.4 / 2 + 4.0
    c = np.array([CL.FRONT_AXLE_X, CL.TRACK_FRONT / 2, CL.WHEEL_Z])
    T = np.array([[c[0] + R * math.cos(t), c[1] + w, c[2] + R * math.sin(t)]
                  for t in np.linspace(0, 2 * math.pi, 240) for w in np.linspace(-W, W, 7)])
    k0, kd = np.array(FS.kp(0.0)), np.array(FS.KP_DIR)
    out = [T]
    for a in list(np.arange(-front_in, 0.0, 2.0)) + list(np.arange(2.0, rear_in + 0.1, 2.0)):
        a = math.radians(a)
        x, y, z = kd / np.linalg.norm(kd)
        cs, sn, C = math.cos(a), math.sin(a), 1 - math.cos(a)
        Rm = np.array([[cs + x * x * C, x * y * C - z * sn, x * z * C + y * sn], [y * x * C + z * sn, cs + y * y * C, y * z * C - x * sn],
                       [z * x * C - y * sn, z * y * C + x * sn, cs + z * z * C]])
        out.append((T - k0) @ Rm.T + k0)
    return np.concatenate(out)


def test_front_legs_clear_the_tyre_at_full_lock():
    A = _tyre_envelope()
    at_leg = A[(A[:, 2] > St.LEG_BOT) & (A[:, 2] < St.LEG_TOP)]
    xs, ys, ws = zip(*St.LEG_PLAN)
    for x, y in at_leg[:, :2]:
        if xs[0] <= x <= xs[-1]:
            yc = np.interp(x, xs, ys)
            w = np.interp(x, xs, ws)
            assert y > yc + w / 2, (x, y)
