"""The PETG insert: solid trapezoid with a channel per item, split in A and B.

Tips and iron each get a bore that follows their pieces (+ ITEM_CLEARANCE).
An item slides into each insert from its split face, so at every depth the
bore also takes whatever passes it on the way in: in each insert a piece's
bore is the union of its own section and every deeper one. Tips: stepped in
A, the collar resting on the last shoulder; one sleeve-wide bore in B.

Outside the band width it runs up to the end caps (the glue end stop); in the
band width the band ring is cut away. Insert A stops INSERT_SPLIT_GAP short of
insert B so the shells always meet first, whatever the glue tolerance. Insert
B's face has an open pocket that takes the key's short leg.
"""

from __future__ import annotations

from functools import cache

from build123d import Part
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.band import BAND_HALF_WIDTH, ring_section, ring_solid
from cad.contents import key_short_leg_line, key_short_leg_section, pieces
from cad.profile import channel_sections, insert_profile
from cad.solids import below_x, extrude_x, extrude_y

TIP_NAMES = ("tip_bl", "tip_br", "tip_tl", "tip_tr")


def pocket_section() -> BaseGeometry:
    """YZ footprint of the pocket in insert B: key and short leg, hulled,
    grown by POCKET_CLEARANCE, kept INSERT_WALL inside the insert surface."""
    ch = channel_sections()
    parts = [ch["key"], key_short_leg_section(p.ITEM_CLEARANCE)]
    hull = unary_union(parts).convex_hull.buffer(p.POCKET_CLEARANCE, p.ARC_QUAD_SEGMENTS)
    return hull.intersection(insert_profile().buffer(-p.INSERT_WALL, p.ARC_QUAD_SEGMENTS))


def bore_pieces(name: str) -> list[tuple[float, float, BaseGeometry]]:
    """(x0, x1, YZ section) of the bore for a tip or the iron, split at
    INSERT_SPLIT_X; the end pieces run on to the cavity ends."""
    items = [(x0, x1, s.buffer(p.ITEM_CLEARANCE, p.ARC_QUAD_SEGMENTS))
             for x0, x1, s in pieces(name, keep_out=True)]
    first, last = items[0], items[-1]
    items[0] = (p.CAVITY_START_X, first[1], first[2])
    items[-1] = (last[0], min(last[1] + p.ITEM_END_CLEARANCE, p.CAVITY_END_X), last[2])
    split = p.INSERT_SPLIT_X
    in_a = [(x0, min(x1, split), s) for x0, x1, s in items if x0 < split]
    in_b = [(max(x0, split), x1, s) for x0, x1, s in items if x1 > split]
    out = []
    for deepest_first in (in_a, in_b[::-1]):
        passed = None
        for x0, x1, s in deepest_first:
            passed = s if passed is None else passed.union(s)
            out.append((x0, x1, passed))
    return sorted(out, key=lambda piece: piece[0])


def bore(name: str) -> Part:
    return Part() + [extrude_x(s, x0, x1) for x0, x1, s in bore_pieces(name)]


@cache
def channel_cuts() -> Part:
    """Everything cut out of the insert for the contents: item channels, key
    hole and the short-leg pocket."""
    ch = channel_sections()
    cuts = bore("iron")
    for name in TIP_NAMES:
        cuts += bore(name)
    cuts += extrude_x(ch["key"], p.KEY_LONG_X0 - p.ITEM_END_CLEARANCE, p.KEY_SHORT_X1)
    cuts += extrude_x(pocket_section(), p.INSERT_SPLIT_X,
                      p.KEY_SHORT_X1 + p.POCKET_CLEARANCE)
    # Where the band bends round the insert's ends its channel cuts diagonally
    # past the square channel ends; round those ends off so INSERT_WALL of
    # PETG always stays between band and items.
    near_band = extrude_y(ring_section().buffer(p.INSERT_WALL, p.ARC_QUAD_SEGMENTS),
                          BAND_HALF_WIDTH + p.INSERT_WALL)
    return cuts - near_band


@cache
def insert_solid() -> Part:
    """The whole insert, before splitting."""
    body = extrude_x(insert_profile(), p.END_CAP_THICKNESS,
                     p.CASE_LENGTH - p.END_CAP_THICKNESS)
    return body - ring_solid() - channel_cuts()


def key_align_groove() -> Part:
    """Shallow groove in insert A's face from the key hole along the short
    leg (as long as the leg), showing how to line the leg up; it may run
    through other channels."""
    face = p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP
    section = key_short_leg_line().buffer(p.KEY_ALIGN_GROOVE_WIDTH / 2, cap_style="flat")
    return extrude_x(section, face - p.KEY_ALIGN_GROOVE_DEPTH, face + 1)


@cache
def insert_a() -> Part:
    """Insert A stops INSERT_SPLIT_GAP short of insert B, so the shells
    always close first. Its face carries the key alignment groove."""
    return (insert_solid() & below_x(p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP)) - key_align_groove()


@cache
def insert_b() -> Part:
    return insert_solid() - below_x(p.INSERT_SPLIT_X)
