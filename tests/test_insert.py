"""Insert (criteria 1, 2, 3, 8, 11). Slow-ish: builds the insert once."""

import pytest

from cad import params as p
from cad.contents import contents_solids, key_short_leg_section, pieces
from cad.band import BAND_HALF_WIDTH, ring_section
from cad.insert import bore_pieces, channel_cuts, insert_a, insert_b, pocket_section
from cad.solids import extrude_x, extrude_y

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


def _hits(section, x0, x1, part) -> bool:
    """Does ``section`` (YZ) extruded over x0..x1 touch ``part``?"""
    return (extrude_x(section, x0, x1) & part).volume > VOLUME_TOLERANCE


SNUG = p.ITEM_CLEARANCE + 0.05  # a hair over the clearance (polygonised arcs)


@pytest.mark.parametrize("name", ["tip_bl", "tip_tr", "iron"])
def test_bores_only_narrow_going_deeper(name):
    """An item slides in from each insert's split face, so in each insert
    every bore piece must hold every deeper one."""
    segs = bore_pieces(name)
    in_a = [s for x0, _, s in segs if x0 < p.INSERT_SPLIT_X]
    in_b = [s for x0, _, s in segs if x0 >= p.INSERT_SPLIT_X][::-1]
    for deepest_first in (in_a, in_b):
        for deeper, shallower in zip(deepest_first, deepest_first[1:]):
            assert deeper.difference(shallower).area < 1e-6


@pytest.mark.parametrize("name", ["tip_bl", "tip_tr"])
def test_tip_bores_are_snug(name):
    """Base steps in A and the sleeve in B sit in a bore only ITEM_CLEARANCE
    wider: a slightly fatter probe already hits the insert."""
    ps = pieces(name)
    for x0, x1, s in ps[:len(p.TIP_BASE_STEPS) + 1]:  # base steps + collar
        assert _hits(s.buffer(SNUG), x0 + 0.5, min(x1, p.INSERT_SPLIT_X) - 0.5, insert_a())
    x0, x1, s = ps[-1]
    assert _hits(s.buffer(SNUG), p.INSERT_SPLIT_X + 0.5, x1 - 0.5, insert_b())


def test_iron_bore_follows_the_handle():
    """Every handle piece is held snug (at least at its sides and bottom) in
    the insert(s) it lies in. (Not every tip piece: the collar's seat is
    shallower in B than its wider ring, which passes it on the way in.)"""
    handle_end = p.ITEM_START_X + p.IRON_HANDLE_LENGTH
    for x0, x1, s in pieces("iron"):
        if x0 >= handle_end - 1e-6:
            continue
        for part, lo, hi in ((insert_a(), x0, min(x1, p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP)),
                             (insert_b(), max(x0, p.INSERT_SPLIT_X), x1)):
            if hi - lo > 1:
                assert _hits(s.buffer(SNUG), lo + 0.5, hi - 0.5, part), (x0, x1)


def test_iron_screw_head_gets_a_groove_up_to_insert_a_face_only():
    """The screw head passes all of insert A's bore on the way in (base
    first), so its groove runs from the screw to A's face; insert B never
    passes it."""
    from shapely.geometry import box

    from cad.contents import iron_axis

    _, z = iron_axis()
    d, h, _ = p.IRON_BODY_SECTION
    flat = z + h - d / 2
    groove = box(-0.5, flat + 0.2, 0.5, flat + p.IRON_SCREW_HEAD_HEIGHT)
    screw = p.ITEM_START_X + p.IRON_SCREW_AT
    mount_end = p.ITEM_START_X + p.IRON_MOUNT_SCREW_AT + p.IRON_MOUNT_SCREW_HEAD_DIAMETER / 2
    for x0, x1, s in bore_pieces("iron"):
        if x1 <= screw - p.IRON_SCREW_HEAD_DIAMETER / 2:
            continue  # deeper than the screw: no groove needed
        if p.INSERT_SPLIT_X <= x0 < mount_end:
            continue  # in B the mounting screw's (larger) groove runs here
        in_a = x0 < p.INSERT_SPLIT_X
        assert (groove.difference(s).area < 1e-6) == in_a, (x0, x1)


def test_tip_collar_and_base_are_in_insert_a():
    collar_end = p.TIP_COLLAR_X + p.TIP_COLLAR_PROFILE[-1][0]
    assert collar_end <= p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP


def test_iron_buttons_keep_extra_room():
    """Round each button the channel leaves ITEM_CLEARANCE +
    IRON_CONTROL_CLEARANCE across and IRON_CONTROL_CLEARANCE along X (bores
    get no clearance along X), so a rattling iron never taps them."""
    from shapely.geometry import box

    from cad.contents import iron_axis

    _, z = iron_axis()
    d, h, _ = p.IRON_BODY_SECTION
    flat = z + h - d / 2
    r = p.IRON_BUTTON_DIAMETER / 2
    room = (box(-r, flat, r, flat + p.IRON_BUTTON_HEIGHT)
            .buffer(p.IRON_CONTROL_CLEARANCE, join_style="mitre"))
    for at in p.IRON_BUTTONS_AT:
        x = p.ITEM_START_X + at
        along = r + p.IRON_CONTROL_CLEARANCE - 0.05
        assert not _hits(room.buffer(p.ITEM_CLEARANCE - 0.05), x - along, x + along,
                         insert_a()), at
        assert _hits(room.buffer(p.ITEM_CLEARANCE + 0.05), x - r, x + r, insert_a()), at


def test_iron_display_keeps_extra_room():
    """Above the (flush) display the channel leaves ITEM_CLEARANCE +
    IRON_CONTROL_CLEARANCE, and as much beside it."""
    from shapely.geometry import box

    from cad.contents import iron_axis

    _, z = iron_axis()
    d, h, _ = p.IRON_BODY_SECTION
    flat = z + h - d / 2
    w = p.IRON_DISPLAY_WIDTH / 2
    room = box(-w, flat - 0.5, w, flat).buffer(p.IRON_CONTROL_CLEARANCE, join_style="mitre")
    x0 = p.ITEM_START_X + p.IRON_DISPLAY_FROM - p.IRON_CONTROL_CLEARANCE + 0.05
    x1 = p.ITEM_START_X + p.IRON_DISPLAY_TO + p.IRON_CONTROL_CLEARANCE - 0.05
    assert not _hits(room.buffer(p.ITEM_CLEARANCE - 0.05), x0, x1, insert_a())
    assert _hits(room.buffer(p.ITEM_CLEARANCE + 0.05), x0, x1, insert_a())


def test_iron_mount_screw_grooves_insert_b_up_to_its_face_only():
    """The mounting screw sits in half B; insert B slides over it from the
    tip end, so its groove runs from the screw to B's face — not into A."""
    from shapely.geometry import box

    from cad.contents import iron_axis

    _, z = iron_axis()
    d, h, _ = p.IRON_BODY_SECTION
    flat = z + h - d / 2
    top = flat + p.IRON_MOUNT_SCREW_HEAD_HEIGHT
    groove = box(-0.5, top - 0.5, 0.5, top)
    screw_end = p.ITEM_START_X + p.IRON_MOUNT_SCREW_AT + p.IRON_MOUNT_SCREW_HEAD_DIAMETER / 2
    for x0, x1, s in bore_pieces("iron"):
        if x0 >= screw_end:
            continue  # deeper in B than the screw: no groove needed
        in_b = x0 >= p.INSERT_SPLIT_X
        assert (groove.difference(s).area < 1e-6) == in_b, (x0, x1)


def test_iron_foot_corners_groove_insert_b_up_to_its_face_only():
    """The foot (half square under the round side) is in half B: its corners
    groove insert B's bore from the foot to B's face, not insert A's."""
    import math

    from shapely.geometry import Point

    from cad.contents import iron_axis

    y, z = iron_axis()
    r = p.IRON_BODY_SECTION[0] / 2
    fr = p.IRON_FOOT_CORNER_RADIUS
    inset = (fr - 0.1) / math.sqrt(2)  # just inside the foot's rounded corner
    corner = Point(y + r - fr + inset, z - r + fr - inset)
    foot_end = p.ITEM_START_X + p.IRON_FOOT_TO
    for x0, x1, s in bore_pieces("iron"):
        if x0 >= foot_end:
            continue
        in_b = x0 >= p.INSERT_SPLIT_X
        assert s.contains(corner) == in_b, (x0, x1)


def test_key_align_groove_in_insert_a_face_along_the_short_leg():
    """A shallow groove in A's face along the short leg: material gone just
    under the face along the leg's line, untouched below the groove depth."""
    from shapely.geometry import Point

    from cad.contents import key_short_leg_line
    from cad.solids import extrude_x

    face = p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP
    line = key_short_leg_line()
    for t in (0.15, 0.9):  # near the key hole and near the leg's end: in PETG
        probe = Point(line.interpolate(t, normalized=True).coords[0]).buffer(0.2)
        just_under = extrude_x(probe, face - p.KEY_ALIGN_GROOVE_DEPTH + 0.1, face - 0.1)
        below = extrude_x(probe, face - p.KEY_ALIGN_GROOVE_DEPTH - 0.5,
                          face - p.KEY_ALIGN_GROOVE_DEPTH - 0.1)
        assert (just_under & insert_a()).volume < VOLUME_TOLERANCE, t
        assert (below & insert_a()).volume > VOLUME_TOLERANCE, t
