"""Insert (criteria 1, 2, 3, 8, 11). Slow-ish: builds the insert once."""

import pytest

from cad import params as p
from cad.contents import contents_solids, key_short_leg_section
from cad.insert import insert_a, insert_b, pocket_section

VOLUME_TOLERANCE = 1e-3  # mm³: "no overlap"
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
