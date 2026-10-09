"""Band ring: continuous channel (criterion 10), floors under grooves (4)."""

import pytest
from shapely.geometry import LineString

from cad import params as p
from cad.band import inner_block, ring_section, straight_run_z
from cad.profile import case_height, insert_profile

# Round items are polygons, so the insert's bottom sits a hair off.
FLOOR_TOLERANCE = 0.01


def test_ring_is_one_closed_loop():
    ring = ring_section()
    assert ring.geom_type == "Polygon"
    assert len(ring.interiors) == 1


def _runs(line) -> list[float]:
    """Lengths of the ring's pieces along ``line``, in order along it."""
    cut = ring_section().intersection(line)
    return [g.length for g in getattr(cut, "geoms", [cut])]


def test_ring_runs_are_measured_thick_enough():
    """Measured across each straight run: one band layer (+ clearance) on
    top and behind both end caps, VELCRO_BOTTOM_LAYERS on the bottom."""
    one = p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE
    bottom_need = p.VELCRO_BOTTOM_LAYERS * p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE
    _, z0, _, z1 = ring_section().bounds
    bottom, top = _runs(LineString([(p.CASE_LENGTH / 2, z0 - 1), (p.CASE_LENGTH / 2, z1 + 1)]))
    end_a, end_b = _runs(LineString([(-1, (z0 + z1) / 2), (p.CASE_LENGTH + 1, (z0 + z1) / 2)]))
    assert top >= one - 1e-6
    assert bottom >= bottom_need - 1e-6
    assert min(end_a, end_b) >= one - 1e-6


def test_ring_is_thick_enough_everywhere_to_thread_the_band():
    """Shrinking by just under half a band layer must keep a closed loop: no
    pinch anywhere, the bends included."""
    one = p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE
    core = ring_section().buffer(-(one / 2 - 0.01))
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
