"""The PETG insert: solid trapezoid with a channel per item, split in A and B.

Tips: a stepped bore in insert A (base steps, then collar-wide up to A's
face; the collar rests on the last shoulder) and one straight sleeve-wide bore
in insert B. Each bore only narrows going deeper, so tips slide in and out.

Outside the band width it runs up to the end caps (the glue end stop); in the
band width the band ring is cut away. Insert A stops INSERT_SPLIT_GAP short of
insert B so the shells always meet first, whatever the glue tolerance. Insert
B's face has an open pocket that takes the key's short leg.
"""

from __future__ import annotations

from functools import cache

from build123d import Part
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.band import BAND_HALF_WIDTH, ring_section, ring_solid
from cad.contents import key_short_leg_section, layout, tip_segments
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


def tip_channel_segments() -> list[tuple[float, float, float]]:
    """(x0, x1, item diameter) of a tip's bore, deepest in A first: the base
    steps, the collar width up to insert A's face, then the sleeve width
    through insert B. The collar rests on the shoulder at TIP_COLLAR_X."""
    base = tip_segments()[:len(p.TIP_BASE_STEPS)]
    out = [(x0, x1, d) for x0, x1, d in base]
    out[0] = (p.CAVITY_START_X, *out[0][1:])
    out.append((p.TIP_COLLAR_X, p.INSERT_SPLIT_X, p.TIP_DIAMETER))
    out.append((p.INSERT_SPLIT_X, p.TIP_END_X + p.ITEM_END_CLEARANCE, p.TIP_SLEEVE_DIAMETER))
    return out


def tip_channel(name: str) -> Part:
    """The bore for one tip, each piece ITEM_CLEARANCE wider than the tip."""
    c = layout()[name].section.centroid
    cut = Part()
    for x0, x1, d in tip_channel_segments():
        section = Point(c.x, c.y).buffer(d / 2 + p.ITEM_CLEARANCE, p.ARC_QUAD_SEGMENTS)
        cut += extrude_x(section, x0, x1)
    return cut


@cache
def channel_cuts() -> Part:
    """Everything cut out of the insert for the contents: item channels, key
    hole and the short-leg pocket."""
    ch = channel_sections()
    cuts = extrude_x(ch["iron"], p.CAVITY_START_X, p.CAVITY_END_X)
    for name in TIP_NAMES:
        cuts += tip_channel(name)
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


@cache
def insert_a() -> Part:
    """Insert A stops INSERT_SPLIT_GAP short of insert B, so the shells
    always close first."""
    return insert_solid() & below_x(p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP)


@cache
def insert_b() -> Part:
    return insert_solid() - below_x(p.INSERT_SPLIT_X)
