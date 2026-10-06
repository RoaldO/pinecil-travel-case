"""What goes in the case: simplified envelopes, placed in case coordinates.

Cross-section layout B (looking along X; Y across, Z up):

    bottom row:  tip  iron  tip      (bottoms level, on the insert floor)
    top row:     tip  key   tip      (top tips dropped onto the bottom row)

Along X every item starts at ``ITEM_START_X``. The L-shaped hex key's short leg
sits just past the tip ends, angled ``KEY_LEG_ANGLE`` down to ``KEY_LEG_SIDE``.

2D shapes are shapely geometry in the YZ plane (x = Y, y = Z).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache

from build123d import Box, Cylinder, Ellipse, Location, Part, Plane, Rot, extrude
from shapely import affinity
from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry

from cad import params as p

# Z of the bottom row's underside: shell bottom wall, glue gap, insert wall,
# channel clearance.
FLOOR_Z = p.SHELL_BOTTOM_WALL + p.GLUE_CLEARANCE + p.INSERT_WALL + p.ITEM_CLEARANCE
# Centre-to-centre gap between two neighbouring channels' items.
ITEM_GAP = 2 * p.ITEM_CLEARANCE + p.INSERT_WEB
DROP_TOLERANCE = 0.001  # mm, bisection tolerance when dropping items


@dataclass(frozen=True)
class Item:
    name: str
    section: BaseGeometry  # YZ cross-section of the item itself (no clearance)
    x0: float
    x1: float


def _ellipse(y: float, z: float, w: float, h: float) -> BaseGeometry:
    return affinity.scale(Point(y, z).buffer(1, p.ARC_QUAD_SEGMENTS), w / 2, h / 2)


def _circle(y: float, z: float, d: float) -> BaseGeometry:
    return Point(y, z).buffer(d / 2, p.ARC_QUAD_SEGMENTS)


def _drop(shape_at, placed: list[BaseGeometry]) -> BaseGeometry:
    """Lower ``shape_at(z)`` onto ``placed`` until it is ITEM_GAP away.

    Bisection between a height where it clearly clears everything and the
    floor, where it overlaps the bottom row.
    """
    def clear(z: float) -> bool:
        return min(shape_at(z).distance(o) for o in placed) >= ITEM_GAP

    lo = FLOOR_Z
    hi = FLOOR_Z + 4 * (p.IRON_HEIGHT + p.TIP_DIAMETER)
    while hi - lo > DROP_TOLERANCE:
        mid = (lo + hi) / 2
        if clear(mid):
            hi = mid
        else:
            lo = mid
    return shape_at(hi)


@cache
def layout() -> dict[str, Item]:
    """All items, keyed by name: iron, tip_bl, tip_br, tip_tl, tip_tr, key."""
    iron = _ellipse(0, FLOOR_Z + p.IRON_HEIGHT / 2, p.IRON_WIDTH, p.IRON_HEIGHT)
    side_y = p.IRON_WIDTH / 2 + ITEM_GAP + p.TIP_DIAMETER / 2
    tip_z = FLOOR_Z + p.TIP_DIAMETER / 2
    tip_bl = _circle(-side_y, tip_z, p.TIP_DIAMETER)
    tip_br = _circle(side_y, tip_z, p.TIP_DIAMETER)
    # Top tips leave room for the key to drop between them.
    top_y = p.KEY_HEX_CORNERS / 2 + ITEM_GAP + p.TIP_DIAMETER / 2 + 2 * DROP_TOLERANCE
    placed = [iron, tip_bl, tip_br]
    tip_tl = _drop(lambda z: _circle(-top_y, z, p.TIP_DIAMETER), placed)
    tip_tr = _drop(lambda z: _circle(top_y, z, p.TIP_DIAMETER), placed)
    key = _drop(lambda z: _circle(0, z, p.KEY_HEX_CORNERS), placed + [tip_tl, tip_tr])

    tips = (p.ITEM_START_X, p.TIP_END_X)
    return {
        "iron": Item("iron", iron, p.ITEM_START_X, p.ITEM_START_X + p.IRON_LENGTH),
        "tip_bl": Item("tip_bl", tip_bl, *tips),
        "tip_br": Item("tip_br", tip_br, *tips),
        "tip_tl": Item("tip_tl", tip_tl, *tips),
        "tip_tr": Item("tip_tr", tip_tr, *tips),
        "key": Item("key", key, p.KEY_LONG_X0, p.KEY_SHORT_X1),
    }


def key_axis() -> tuple[float, float]:
    """(y, z) of the key's long leg axis."""
    c = layout()["key"].section.centroid
    return c.x, c.y


def key_short_leg_line() -> LineString:
    """Centreline of the short leg in YZ, from the long-leg axis outward."""
    y, z = key_axis()
    a = math.radians(p.KEY_LEG_ANGLE)
    length = p.KEY_SHORT_LEG - p.KEY_HEX_CORNERS / 2
    return LineString([(y, z), (y + p.KEY_LEG_SIDE * length * math.cos(a),
                                z + length * math.sin(a))])


def key_short_leg_section(grow: float = 0.0) -> BaseGeometry:
    """YZ footprint of the short leg (+ ``grow``)."""
    return key_short_leg_line().buffer(p.KEY_HEX_CORNERS / 2 + grow, p.ARC_QUAD_SEGMENTS)


# --- 3D envelopes (for the viewer and interference tests) ----------------------


def _along_x(y: float, z: float, x0: float, x1: float, solid_xy) -> Part:
    """Place a solid built on the XY plane (extruded +Z) along X at (y, z)."""
    plane = Plane(origin=(x0, y, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return plane * solid_xy(x1 - x0)


def iron_solid() -> Part:
    item = layout()["iron"]
    c = item.section.centroid
    handle = _along_x(c.x, c.y, item.x0, item.x0 + p.IRON_HANDLE_LENGTH,
                      lambda L: extrude(Ellipse(p.IRON_WIDTH / 2, p.IRON_HEIGHT / 2), L))
    metal = _along_x(c.x, c.y, item.x0 + p.IRON_HANDLE_LENGTH, item.x1,
                     lambda L: Location((0, 0, L / 2)) * Cylinder(p.IRON_METAL_DIAMETER / 2, L))
    return handle + metal


def tip_segments() -> list[tuple[float, float, float]]:
    """(x0, x1, diameter) of a tip's coaxial pieces, base (white rings) first:
    the base steps, the collar, then everything up to the working end as one
    sleeve-diameter envelope."""
    out, x = [], p.ITEM_START_X
    for length, d in p.TIP_BASE_STEPS:
        out.append((x, x + length, d))
        x += length
    out.append((x, x + p.TIP_COLLAR_LENGTH, p.TIP_DIAMETER))
    out.append((x + p.TIP_COLLAR_LENGTH, p.TIP_END_X, p.TIP_SLEEVE_DIAMETER))
    return out


def tip_solid(name: str) -> Part:
    c = layout()[name].section.centroid
    return Part() + [
        _along_x(c.x, c.y, x0, x1,
                 lambda L, d=d: Location((0, 0, L / 2)) * Cylinder(d / 2, L))
        for x0, x1, d in tip_segments()
    ]


def key_solid() -> Part:
    item = layout()["key"]
    y, z = key_axis()
    long_leg = _along_x(y, z, item.x0, item.x1,
                        lambda L: Location((0, 0, L / 2)) * Cylinder(p.KEY_HEX_CORNERS / 2, L))
    (y0, z0), (y1, z1) = key_short_leg_line().coords
    length = math.hypot(y1 - y0, z1 - z0)
    short = Location((p.KEY_SHORT_X0 + p.KEY_HEX / 2, y0, z0)) * (
        Rot(math.degrees(math.atan2(z1 - z0, y1 - y0)), 0, 0)
        * Location((0, length / 2, 0))
        * Box(p.KEY_HEX, length, p.KEY_HEX)
    )
    return long_leg + short


def contents_solids() -> dict[str, Part]:
    out = {"iron": iron_solid(), "key": key_solid()}
    for name in ("tip_bl", "tip_br", "tip_tl", "tip_tr"):
        out[name] = tip_solid(name)
    return out
