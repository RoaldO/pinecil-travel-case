"""The PETG insert: solid trapezoid with a channel per item, split in A and B.

Outside the band width it runs up to the end caps (the glue end stop); in the
band width the band ring is cut away. Insert A stops INSERT_SPLIT_GAP short of
insert B so the shells always meet first, whatever the glue tolerance. Insert
B's face has an open grip pocket that takes the protruding tip ends and the
key's short leg.
"""

from __future__ import annotations

from functools import cache

from build123d import Part
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.band import BAND_HALF_WIDTH, ring_section, ring_solid
from cad.contents import key_short_leg_section
from cad.profile import channel_sections, insert_profile
from cad.solids import below_x, extrude_x, extrude_y

TIP_NAMES = ("tip_bl", "tip_br", "tip_tl", "tip_tr")


def pocket_section() -> BaseGeometry:
    """YZ footprint of the grip pocket: top tips, key and short leg, hulled,
    grown by POCKET_CLEARANCE, kept INSERT_WALL inside the insert surface."""
    ch = channel_sections()
    parts = [ch["tip_tl"], ch["tip_tr"], ch["key"],
             key_short_leg_section(p.ITEM_CLEARANCE)]
    hull = unary_union(parts).convex_hull.buffer(p.POCKET_CLEARANCE, p.ARC_QUAD_SEGMENTS)
    return hull.intersection(insert_profile().buffer(-p.INSERT_WALL, p.ARC_QUAD_SEGMENTS))


@cache
def channel_cuts() -> Part:
    """Everything cut out of the insert for the contents: item channels, key
    hole and grip pocket."""
    ch = channel_sections()
    cuts = extrude_x(ch["iron"], p.CAVITY_START_X, p.CAVITY_END_X)
    for name in TIP_NAMES:
        cuts += extrude_x(ch[name], p.CAVITY_START_X, p.TIP_END_X + p.ITEM_END_CLEARANCE)
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
