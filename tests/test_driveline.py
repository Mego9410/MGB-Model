"""Driveline datums (P6, P7) must agree with the published figures they come from."""
from mgb import propshaft_layout as P, rear_axle_layout as A


def test_propshaft_fits_inside_its_haynes_travel():
    assert P.LEN_COMPRESSED < P.INSTALLED_LEN < P.LEN_EXTENDED
    assert P.ENGAGED_EXTENDED > 20.0                     # the stub stays in the sleeve fully extended


def test_axle_ratio_is_the_published_one():
    assert round(A.Z_CROWN / A.Z_PINION, 3) == 3.909


def test_hub_threads_are_handed_by_side():
    assert A.HUB_NUT_HAND[1] != A.HUB_NUT_HAND[-1]
    assert A.SPINNER_HAND[-1] == "left"                  # right-hand side of the car: left-hand spinner thread


def test_wheel_centre_planes_on_the_track():
    from mgb import car_layout as CL
    assert A.EXT_COLLAR_Y[0] < CL.TRACK_REAR / 2 < A.EXT_COLLAR_Y[1]
