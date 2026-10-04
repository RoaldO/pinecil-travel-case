"""Band ring: continuous channel (criterion 10), floors under grooves (4)."""

import pytest

from cad import params as p
from cad.band import inner_block, ring_section, straight_run_z
from cad.profile import case_height, insert_profile

# Round items are polygons, so the insert's bottom sits a hair off.
FLOOR_TOLERANCE = 0.01


def test_ring_is_one_closed_loop():
    ring = ring_section()
    assert ring.geom_type == "Polygon"
    assert len(ring.interiors) == 1


def test_ring_is_thick_enough_everywhere_to_thread_the_band():
    """Shrinking by just under half the thinnest run must keep a closed loop."""
    thinnest = min(p.RING_END, p.RING_TOP, p.RING_BOTTOM)
    assert thinnest >= p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE - 1e-9
    core = ring_section().buffer(-(thinnest / 2 - 0.01))
    assert core.geom_type == "Polygon" and len(core.interiors) == 1


def test_shell_floor_under_both_grooves():
    _, insert_bottom, _, insert_top = insert_profile().bounds
    _, inner_bottom, _, inner_top = inner_block().bounds
    assert inner_top - (insert_top + p.GLUE_CLEARANCE) == pytest.approx(p.SHELL_FLOOR, abs=FLOOR_TOLERANCE)
    assert (insert_bottom - p.GLUE_CLEARANCE) - inner_bottom == pytest.approx(p.SHELL_FLOOR, abs=FLOOR_TOLERANCE)


def test_top_groove_is_flush():
    assert ring_section().bounds[3] == pytest.approx(case_height())


def test_straight_run_is_inside_the_case():
    lo, hi = straight_run_z()
    assert 0 < lo < hi < case_height()
