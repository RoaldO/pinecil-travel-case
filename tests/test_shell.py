"""Shell and logo (criteria 1, 2, 5, 6, 7). Builds shell and insert once."""

import pytest
from build123d import Plane, Vector

from cad import params as p
from cad.band import BAND_HALF_WIDTH, straight_run_z
from cad.contents import contents_solids
from cad.insert import insert_a, insert_b
from cad.pinecil_logo import holes_mm, outline_mm
from cad.shell import logo_plane, logo_z, shell_a, shell_b

VOLUME_TOLERANCE = 1e-3  # mm³: "no overlap"
SHELLS = {"shell A": shell_a, "shell B": shell_b}
PARTS = {**SHELLS, "insert A": insert_a, "insert B": insert_b}


@pytest.mark.parametrize("name", SHELLS)
def test_shell_is_one_valid_solid(name):
    part = SHELLS[name]()
    assert part.is_valid
    assert len(part.solids()) == 1


@pytest.mark.parametrize("name", SHELLS)
def test_shell_fits_the_printer_standing_up(name):
    size = SHELLS[name]().bounding_box().size
    assert size.X <= p.MAX_PRINT_HEIGHT
    assert max(size.Y, size.Z) <= p.PRINT_BED


@pytest.mark.parametrize("a, b", [("shell A", "insert A"), ("shell B", "insert B"),
                                  ("shell B", "insert A"), ("shell A", "insert B"),
                                  ("shell A", "shell B")])
def test_assembled_parts_do_not_overlap(a, b):
    assert (PARTS[a]() & PARTS[b]()).volume < VOLUME_TOLERANCE


@pytest.mark.parametrize("item", ["iron", "tip_bl", "tip_br", "tip_tl", "tip_tr", "key"])
def test_contents_do_not_hit_the_shell(item):
    solid = contents_solids()[item]
    for name, part in SHELLS.items():
        assert (solid & part()).volume < VOLUME_TOLERANCE, name


def test_logo_sits_on_the_straight_band_run():
    minx, miny, maxx, maxy = outline_mm().bounds
    lo, hi = straight_run_z()
    assert logo_z() + miny >= lo + p.LOGO_BAND_MARGIN
    assert logo_z() + maxy <= hi - p.LOGO_BAND_MARGIN
    assert max(-minx, maxx) <= BAND_HALF_WIDTH - p.LOGO_BAND_MARGIN


def test_logo_is_upright():
    """Logo +Y (towards the top piece P1) maps to case +Z."""
    assert logo_plane().y_dir == Vector(0, 0, 1)
    top_piece = max(holes_mm(), key=lambda h: h.centroid.y)
    assert top_piece.centroid.y > 0


def test_logo_cuts_through_shell_b_end_cap():
    def cap_area(part, x):
        return sum(f.area for f in part.intersect(Plane.YZ.offset(x)))

    plain = cap_area(shell_a(), p.END_CAP_THICKNESS / 2)
    with_logo = cap_area(shell_b(), p.CASE_LENGTH - p.END_CAP_THICKNESS / 2)
    assert plain - with_logo == pytest.approx(sum(h.area for h in holes_mm()), rel=1e-3)


def test_shell_b_mouth_has_an_inner_chamfer():
    """Right at shell B's mouth the PLA round the cavity is gone over (almost)
    the chamfer's size; past its depth the cavity wall is back."""
    from cad.profile import insert_cavity
    from cad.solids import extrude_x

    cavity = insert_cavity(p.SLIDE_CLEARANCE)
    rim = cavity.buffer(p.SHELL_B_MOUTH_CHAMFER - 0.25).difference(cavity)
    wall = cavity.buffer(0.1).difference(cavity)
    x = p.SHELL_SPLIT_X
    assert (extrude_x(rim, x + 0.02, x + 0.1) & shell_b()).volume < VOLUME_TOLERANCE
    deep = (x + p.SHELL_B_MOUTH_CHAMFER + 0.1, x + p.SHELL_B_MOUTH_CHAMFER + 0.3)
    assert (extrude_x(wall, *deep) & shell_b()).volume > VOLUME_TOLERANCE
