"""Suspension, steering and wheel datums (P9) must agree with the published figures they come from."""
import math

from mgb import car_layout as CL, front_suspension_layout as F, rear_axle_layout as A, rear_suspension_layout as R
from mgb import steering_layout as S, wheel_layout as W

IN = 25.4


def test_front_damper_arm_centres_are_8_in():
    sy, sz = F.DAMPER_SHAFT[1], F.DAMPER_SHAFT[2]
    fy, fz = F.TOP_FULCRUM[1], F.TOP_FULCRUM[2]
    assert abs(math.hypot(fy - sy, fz - sz) - 8.0 * IN) < 1e-6


def test_rear_damper_arm_is_5_1_4_in():
    assert abs((R.DAMPER_SHAFT[0] - R.LINK_X) - 5.25 * IN) < 1e-6


def test_king_pin_inclination_and_castor():
    dx, dy, dz = F.KP_DIR
    assert abs(math.degrees(math.atan2(-dy, dz)) - 8.0) < 1e-6      # top inboard
    assert abs(math.degrees(math.atan2(-dx, dz)) - 7.0) < 1e-6      # top rearward


def test_crossmember_lowest_point_is_the_published_ground_clearance():
    assert abs((F.XM_LOW_Z - CL.GROUND_Z) - 4.2 * IN) < 1e-6
    assert F.XM_DIP_TOP < CL.SUMP_BOTTOM_Z                          # passes under the sump


def test_front_spring_is_compressed_below_its_free_height():
    assert 150.0 < F.SPRING_INSTALLED < 9.9 * IN


def test_wheels_sit_on_the_hub_cones_front_and_rear():
    assert F.EXT_COLLAR_Y[0] < F.WHEEL_PLANE_Y < F.EXT_COLLAR_Y[1]
    assert abs((F.WHEEL_PLANE_Y - F.EXT_COLLAR_Y[0]) - (CL.TRACK_REAR / 2 - A.EXT_COLLAR_Y[0])) < 0.5
    assert F.EXT_SPLINE == A.EXT_SPLINE and F.EXT_TPI == A.EXT_TPI
    assert F.SPINNER_HAND == A.SPINNER_HAND


def test_tyre_is_the_car_layout_tyre():
    assert abs(2 * W.TYRE_R - CL.TYRE_D) < 1e-6
    assert abs(W.SECTION_W - 5.60 * IN) < 1e-6


def test_rear_spring_sits_on_the_axle_seat():
    assert abs((R.TOP_Z + R.PLATE18_T + R.PAD19_T) - (A.AZ + A.SEAT_FACE_Z)) < 1e-6
    assert R.UBOLT_DY - R.UBOLT_ROD_R > A.SPRING_W / 2 + 5.0         # U-bolt legs clear of the axle seat's sides


def test_pinion_and_column_share_one_axis():
    a = S.col(S.PINION_T[0])
    b = S.col(S.WHEEL_T)
    d = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in d))
    assert all(abs(d[i] / n - S.COLUMN_DIR[i]) < 1e-9 for i in range(3))
    assert S.WHEEL_CENTRE[1] < 0                                       # right-hand drive
