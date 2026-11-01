"""Fasteners match the standard tables. Run: python -m pytest tests -q"""
import pytest

from mgb import fasteners as F

IN = 25.4


@pytest.mark.parametrize("size", list(F.THREADS))
def test_across_flats_match_tables(size):
    assert abs(F.across_flats(F.hex_nut(size)) / IN - F.NUT[size][0]) < 1e-6
    assert abs(F.across_flats(F.hex_bolt(size, 1.0)) / IN - F.BOLT_HEAD[size][0]) < 1e-6


@pytest.mark.parametrize("size,series,tpi", [("1/4", "UNF", 28), ("5/16", "UNF", 24), ("3/8", "UNF", 24),
                                             ("7/16", "UNF", 20), ("1/4", "UNC", 20), ("3/8", "UNC", 16)])
def test_pitch_matches_b1_1(size, series, tpi):
    assert abs(F.pitch_mm(size, series) - IN / tpi) < 1e-9


def test_washer_dimensions():
    w = F.plain_washer("3/8")
    bb = w.bounding_box()
    assert abs(bb.size.X / IN - 0.812) < 1e-6 and abs(bb.size.Z / IN - 0.065) < 1e-6


def test_true_thread_bolt_is_valid_and_full_length():
    b = F.hex_bolt("5/16", 1.0, true_thread=True)
    assert b.is_valid
    assert abs(b.bounding_box().size.Z - (1.0 + 13 / 64) * IN) < 0.05
