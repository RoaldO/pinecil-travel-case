"""Insert (criteria 1, 2, 3, 8, 11). Slow-ish: builds the insert once."""

import pytest

from cad import params as p
from cad.contents import contents_solids, key_short_leg_section
from cad.band import BAND_HALF_WIDTH, ring_section
from cad.insert import (channel_cuts, insert_a, insert_b, pocket_section,
                        tip_channel_segments)
from cad.solids import extrude_y

VOLUME_TOLERANCE = 1e-3  # mm³: "no overlap"
WALL_TOLERANCE = 0.01  # mm, polygonised arcs
INSERTS = {"insert A": insert_a, "insert B": insert_b}


@pytest.mark.parametrize("name", INSERTS)
def test_insert_is_one_valid_solid(name):
    part = INSERTS[name]()
    assert part.is_valid
    assert len(part.solids()) == 1


@pytest.mark.parametrize("name", INSERTS)
def test_insert_fits_the_printer_standing_up(name):
    size = INSERTS[name]().bounding_box().size
    assert size.X <= p.MAX_PRINT_HEIGHT
    assert max(size.Y, size.Z) <= p.PRINT_BED


def test_inserts_do_not_overlap():
    assert (insert_a() & insert_b()).volume < VOLUME_TOLERANCE


@pytest.mark.parametrize("item", ["iron", "tip_bl", "tip_br", "tip_tl", "tip_tr", "key"])
def test_contents_do_not_hit_the_inserts(item):
    solid = contents_solids()[item]
    for name, part in INSERTS.items():
        assert (solid & part()).volume < VOLUME_TOLERANCE, name


def test_key_short_leg_is_free_when_opened():
    leg = key_short_leg_section(0)
    assert leg.difference(pocket_section()).area < 1e-6
    # entirely past insert A's face (and so past shell A too)
    assert p.KEY_SHORT_X0 > p.INSERT_SPLIT_X > p.SHELL_SPLIT_X


def test_inserts_leave_a_gap_so_the_shells_close_first():
    gap = insert_b().bounding_box().min.X - insert_a().bounding_box().max.X
    assert gap == pytest.approx(p.INSERT_SPLIT_GAP)
    assert insert_b().bounding_box().min.X == pytest.approx(p.INSERT_SPLIT_X)


def test_inserts_rest_on_the_end_caps():
    assert insert_a().bounding_box().min.X == pytest.approx(p.END_CAP_THICKNESS)
    assert insert_b().bounding_box().max.X == pytest.approx(p.CASE_LENGTH - p.END_CAP_THICKNESS)


def test_channels_keep_insert_wall_from_the_band_bends():
    """Where the band bends round the insert's ends, at least INSERT_WALL of
    PETG must stay between the band channel and every item channel."""
    near_band = extrude_y(ring_section().buffer(p.INSERT_WALL - WALL_TOLERANCE),
                          BAND_HALF_WIDTH)
    assert (channel_cuts() & near_band).volume < VOLUME_TOLERANCE


@pytest.mark.parametrize("name", ["tip_bl", "tip_tr"])
def test_tip_channel_follows_the_base_steps(name):
    """Each base step sits in a bore only ITEM_CLEARANCE wider (+ a hair for
    polygonised arcs): a slightly fatter cylinder already hits insert A."""
    from build123d import Cylinder, Location, Plane

    from cad.contents import layout, tip_segments

    c = layout()[name].section.centroid
    for x0, x1, d in tip_segments()[:len(p.TIP_BASE_STEPS)]:
        plane = Plane(origin=(x0 + 0.5, c.x, c.y), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        r = d / 2 + p.ITEM_CLEARANCE + 0.05
        probe = plane * (Location((0, 0, (x1 - x0 - 1) / 2)) * Cylinder(r, x1 - x0 - 1))
        assert (probe & insert_a()).volume > VOLUME_TOLERANCE, (x0, d)


def test_tip_bores_only_narrow_going_deeper():
    """A tip slides in from each insert's face: in A the bore widens toward
    the face, in B it may only narrow away from it."""
    segs = tip_channel_segments()
    in_a = [d for x0, _, d in segs if x0 < p.INSERT_SPLIT_X]
    in_b = [d for x0, _, d in segs if x0 >= p.INSERT_SPLIT_X]
    assert in_a == sorted(in_a)
    assert in_b == sorted(in_b, reverse=True)


def test_tip_collar_and_base_are_in_insert_a():
    collar_end = p.TIP_COLLAR_X + p.TIP_COLLAR_LENGTH
    assert collar_end <= p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP


def test_tip_sleeve_bore_in_insert_b_is_snug():
    """Insert B holds the tip end in a bore only ITEM_CLEARANCE wider."""
    from build123d import Cylinder, Location, Plane

    from cad.contents import layout

    c = layout()["tip_tl"].section.centroid
    x0, x1 = p.INSERT_SPLIT_X + 0.5, p.TIP_END_X
    plane = Plane(origin=(x0, c.x, c.y), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    r = p.TIP_SLEEVE_DIAMETER / 2 + p.ITEM_CLEARANCE + 0.05
    probe = plane * (Location((0, 0, (x1 - x0) / 2)) * Cylinder(r, x1 - x0))
    assert (probe & insert_b()).volume > VOLUME_TOLERANCE
