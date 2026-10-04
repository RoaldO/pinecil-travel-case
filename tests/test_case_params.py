"""Derived dimensions (spec criterion 9) and print limits (criterion 2)."""

import pytest

from cad import params as p


def test_case_length_is_the_sum_of_its_layers():
    ends = 2 * (p.END_CAP_THICKNESS + p.RING_END + p.INSERT_END_WALL)
    assert p.CASE_LENGTH == pytest.approx(ends + p.IRON_LENGTH + 2 * p.ITEM_END_CLEARANCE)


def test_insert_split_leaves_tip_grip():
    assert p.TIP_END_X - p.INSERT_SPLIT_X == pytest.approx(p.TIP_GRIP)


def test_shell_split_is_overlap_before_insert_split():
    assert p.INSERT_SPLIT_X - p.SHELL_SPLIT_X == pytest.approx(p.OVERLAP)


def test_key_short_leg_sits_just_past_the_tips():
    assert p.KEY_SHORT_X0 == pytest.approx(p.TIP_END_X + p.ITEM_CLEARANCE)
    assert p.KEY_SHORT_X1 - p.KEY_LONG_X0 == pytest.approx(p.KEY_LONG_LEG)


def test_shell_walls_hold_the_grooves():
    assert p.SHELL_TOP_WALL == pytest.approx(p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE + p.SHELL_FLOOR)
    assert p.SHELL_BOTTOM_WALL == pytest.approx(
        p.VELCRO_BOTTOM_LAYERS * p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE + p.SHELL_FLOOR)


def test_split_order():
    assert 0 < p.SHELL_SPLIT_X < p.INSERT_SPLIT_X < p.TIP_END_X < p.CASE_LENGTH
