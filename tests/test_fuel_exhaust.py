"""Exhaust and fuel supply datums (P11a) must keep the clearances they were derived for."""
import math

from mgb import car_layout as CL, exhaust_layout as E, fuel_supply_layout as L, rear_axle_layout as A
from mgb import underbody_layout as U

IN = 25.4


def _lowest(route, r):
    return min(p[2] for p in route) - r


def test_exhaust_keeps_the_published_ground_clearance():
    floor = CL.GROUND_Z + CL.GROUND_CLEARANCE - 1.0
    for route in [E.FRONT_ROUTE, E.INTER_ROUTE, E.TAIL_ROUTE]:
        assert _lowest(route, E.PIPE_OD / 2) >= floor
    assert E.CS_Z - E.CS_H / 2 >= floor                       # centre silencer underside
    assert E.RS_Z - E.RS_D / 2 >= floor


def test_exhaust_passes_under_the_left_handbrake_rod():
    x, z = E.rod_left(E.UNDER_ROD[1])
    assert abs(x - E.UNDER_ROD[0]) < 15.0
    assert E.UNDER_ROD[2] + E.PIPE_OD / 2 < z - 4.0 - 5.0      # rod radius and a gap


def test_rear_silencer_between_tank_and_spring():
    assert E.RS_Y - E.RS_D / 2 > L.TANK_Y[1] + 20.0
    assert E.RS_Y + E.RS_D / 2 < A.SPRING_Y - A.SPRING_W / 2 - 20.0


def test_tank_holds_ten_gallons():
    from parts.fuel import tank as T
    assert 43.0 < T.volume_litres() < 48.0                    # 10 Imp gal = 45.5 litres


def test_main_pipe_ends_at_the_feed_union():
    end = L.MAIN_ROUTE[-1]
    assert math.isclose(end[1], L.FEED_Y) and math.isclose(end[2], L.FEED_Z)
    from parts.fuel import pipes as P3
    assert math.isclose(P3.FEED_END[0], L.FEED_END_X) and math.isclose(P3.FEED_END[1], L.FEED_Y)
    assert math.isclose(P3.FEED_END[2], L.FEED_Z)


def test_pump_sits_on_the_heelboard_ahead_of_the_right_spring():
    assert L.PUMP_Y0 < 0                                       # right-hand side (Haynes Ch 3 Sec 5)
    assert L.PUMP_X < U.HEELBOARD_X                            # axle side of the heelboard
    front_eye_x = A.AX + 22.5 * IN                             # P9's spring front eye (rear_suspension_layout)
    assert L.PUMP_X - 50.0 > front_eye_x                       # ahead of the spring's front end
