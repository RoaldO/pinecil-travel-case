import itertools

import pytest
from shapely.ops import unary_union

from cad import params
from cad.build import logo_plate
from cad.pinecil_logo import centerlines_svg, holes_mm, outline_mm, pieces_svg


def test_artwork_has_ten_pieces():
    assert len(pieces_svg()) == 10


def test_six_lattice_centerlines_each_separating_two_piece_pairs():
    lines = centerlines_svg()
    assert [c.id for c in lines] == [f"L{i}" for i in range(1, 7)]
    assert all(len(c.between) == 2 for c in lines)


@pytest.mark.parametrize("max_size", [params.LOGO_MAX_SIZE, 15.0, 25.0])
def test_logo_fits_max_size(max_size):
    minx, miny, maxx, maxy = outline_mm(max_size).bounds
    assert max(maxx - minx, maxy - miny) == pytest.approx(max_size)


@pytest.mark.parametrize("rib_width", [0.8, 1.2, 1.6])
def test_holes_stay_within_outline_and_ribs_are_rib_width(rib_width):
    holes = holes_mm(rib_width)
    assert len(holes) == 10
    outline = outline_mm()
    assert unary_union(holes).difference(outline).area < 1e-9
    # Pieces separated by a rib are at least rib_width apart.
    gaps = [a.distance(b) for a, b in itertools.combinations(holes, 2)]
    assert min(gaps) == pytest.approx(rib_width, abs=0.02)


def test_narrow_rib_width_keeps_artwork_gaps():
    """Below the artwork's own gap the ribs keep their original width."""
    assert unary_union(holes_mm(0.1)).area == pytest.approx(
        outline_mm().area, rel=1e-6
    )


def test_wider_ribs_never_grow_the_logo():
    narrow, wide = unary_union(holes_mm(0.8)), unary_union(holes_mm(1.5))
    assert wide.area < narrow.area
    assert wide.difference(narrow).area < 1e-9


def test_plate_is_one_valid_solid_with_logo_area_removed():
    plate = logo_plate()
    assert plate.is_valid
    assert len(plate.solids()) == 1
    bb = plate.bounding_box()
    full = bb.size.X * bb.size.Y * params.PLATE_THICKNESS
    removed = unary_union(holes_mm()).area * params.PLATE_THICKNESS
    assert plate.volume == pytest.approx(full - removed, rel=1e-3)
