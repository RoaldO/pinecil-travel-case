"""Insert and shell profiles."""

import pytest

from cad import params as p
from cad.contents import key_short_leg_section
from cad.profile import (channel_sections, groove_edge_walls, insert_profile,
                         insert_trapezoid, shell_profile)

WALL_TOLERANCE = 0.01  # mm, polygonised arcs


def test_channels_keep_insert_wall_to_the_surface():
    inner = insert_profile().buffer(-p.INSERT_WALL + 1e-3)
    for name, ch in channel_sections().items():
        assert ch.difference(inner).area < 1e-6, name


def test_short_leg_fits_inside_the_insert():
    leg = key_short_leg_section(p.ITEM_CLEARANCE)
    assert leg.difference(insert_profile().buffer(-p.INSERT_WALL + 1e-3)).area < 1e-6


def test_profiles_are_symmetric_and_shell_starts_at_z0():
    for prof in (insert_profile(), shell_profile()):
        minx, _, maxx, _ = prof.bounds
        assert minx == pytest.approx(-maxx, abs=1e-6)
    assert shell_profile().bounds[1] == pytest.approx(0, abs=1e-9)


def test_shell_contains_insert_with_side_wall():
    gap = shell_profile().exterior.distance(insert_profile())
    assert gap >= p.GLUE_CLEARANCE + p.SHELL_SIDE_WALL - 0.01


def test_bottom_is_wider_than_top():
    prof = shell_profile()
    _, z0, _, z1 = prof.bounds
    from shapely.geometry import LineString
    width = lambda z: prof.intersection(LineString([(-999, z), (999, z)])).length  # noqa: E731
    assert width(z0 + (z1 - z0) * 0.25) > width(z0 + (z1 - z0) * 0.75)


@pytest.fixture
def fresh_profiles():
    """Clear the cached fit before and after a test that changes params."""
    insert_trapezoid.cache_clear()
    yield
    insert_trapezoid.cache_clear()


@pytest.mark.parametrize("velcro_width", [p.VELCRO_WIDTH, 25.0])
def test_band_edges_lie_flush_in_the_grooves(monkeypatch, fresh_profiles, velcro_width):
    """A wider strap must widen the top instead of standing proud at its edges."""
    monkeypatch.setattr(p, "VELCRO_WIDTH", velcro_width)
    top, bottom = groove_edge_walls()
    assert top >= p.VELCRO_THICKNESS - WALL_TOLERANCE
    assert bottom >= p.VELCRO_BOTTOM_LAYERS * p.VELCRO_THICKNESS - WALL_TOLERANCE
