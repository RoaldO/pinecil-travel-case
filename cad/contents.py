"""What goes in the case: simplified envelopes, placed in case coordinates.

Cross-section layout B (looking along X; Y across, Z up):

    bottom row:  tip  iron  tip      (bottoms level, on the insert floor)
    top row:     tip  key   tip      (top tips dropped onto the bottom row)

Along X every item starts at ``ITEM_START_X`` with its base: the tips' white
rings and the iron's handle lie deep in half A. The L-shaped hex
key's short leg sits just past the tip ends, angled ``KEY_LEG_ANGLE`` down to
``KEY_LEG_SIDE``.

Tips and iron are stacks of coaxial pieces (``pieces``); their layout
section is the envelope of all pieces.

2D shapes are shapely geometry in the YZ plane (x = Y, y = Z).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache

from build123d import Box, Cylinder, Location, Part, Plane, Rot
from shapely.geometry import LineString, Point, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.solids import extrude_x

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


def tombstone(y: float, z: float, d: float, h: float, r: float) -> BaseGeometry:
    """Iron handle section with its axis at (y, z): a half circle of diameter
    ``d`` below the axis, a ``d``-wide block above it up to a total height
    ``h``, the block's top corners rounded with radius ``r``."""
    top = z + h - d / 2
    block = (box(y - d / 2, 2 * z - top, y + d / 2, top)  # mirrored, so only
             .buffer(-r, join_style="mitre")             # the top corners
             .buffer(r, p.ARC_QUAD_SEGMENTS))             # stay rounded
    upper = block.intersection(box(y - d, z, y + d, top + 1))
    return unary_union([upper, _circle(y, z, d)])


def _circle(y: float, z: float, d: float) -> BaseGeometry:
    return Point(y, z).buffer(d / 2, p.ARC_QUAD_SEGMENTS)


def _drop(shape_at, placed: list[BaseGeometry]) -> BaseGeometry:
    """Lower ``shape_at(z)`` onto ``placed`` until it is ITEM_GAP away.

    Bisection between a height where it clearly clears everything and the
    floor, where it overlaps the bottom row.
    """
    def clear(z: float) -> bool:
        return min(shape_at(z).distance(o) for o in placed) >= ITEM_GAP

    return shape_at(_bisect(clear, FLOOR_Z, FLOOR_Z + 4 * (_iron_height() + p.TIP_DIAMETER)))


def _bisect(ok, lo: float, hi: float) -> float:
    """Smallest t in [lo, hi] (to DROP_TOLERANCE) with ok(t); ok(hi) holds."""
    while hi - lo > DROP_TOLERANCE:
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


_HANDLE_SECTIONS = (p.IRON_BODY_SECTION, p.IRON_GRIP_SECTION)


def _iron_radius() -> float:
    return max(d for d, _, _ in _HANDLE_SECTIONS) / 2


def _iron_height() -> float:
    return max(h - d / 2 for d, h, _ in _HANDLE_SECTIONS) + _iron_radius()


def iron_axis() -> tuple[float, float]:
    """(y, z) of the iron's axis (= its tip's axis): the lowest point of the
    widest half circle stands on the floor."""
    return 0.0, FLOOR_Z + _iron_radius()


def tip_profile_past_base() -> list[tuple[float, float]]:
    """(length, diameter) of a tip from its collar's base to its working end:
    the collar profile (tapers as TAPER_STEP steps at their wider end), then
    the sleeve."""
    out = []
    for (x0, d0), (x1, d1) in zip(p.TIP_COLLAR_PROFILE, p.TIP_COLLAR_PROFILE[1:]):
        if x1 <= x0:
            continue  # a step
        n = 1 if d0 == d1 else max(1, math.ceil((x1 - x0) / p.TAPER_STEP - 1e-9))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            out.append(((x1 - x0) / n, max(d0 + (d1 - d0) * t0, d0 + (d1 - d0) * t1)))
    collar = p.TIP_COLLAR_PROFILE[-1][0]
    rest = p.TIP_LENGTH - sum(length for length, _ in p.TIP_BASE_STEPS) - collar
    return out + [(rest, p.TIP_SLEEVE_DIAMETER)]


def _iron_piece_sections(y: float, z: float, keep_out: bool = False
                         ) -> list[tuple[float, BaseGeometry]]:
    """(length, section) of the iron's pieces, from its handle's base to its
    tip. Each feature covers a stretch of the iron (from the base); a piece's
    section is the union of every feature covering it. With ``keep_out`` the
    controls (buttons, display) are grown by IRON_CONTROL_CLEARANCE, along X
    too: the room the channel must leave them."""
    body_d, body_h, _ = p.IRON_BODY_SECTION
    flat = z + body_h - body_d / 2  # the flat face (display, buttons)

    def bump(at: float, diameter: float, height: float, extra: float = 0.0):
        """Round thing on the flat face, centred across it, as its square
        envelope along X (+ ``extra`` all round, outside the body)."""
        r = diameter / 2 + extra
        return (at - r, at + r, box(y - r, flat - 1, y + r, flat + height + extra))

    extra = p.IRON_CONTROL_CLEARANCE if keep_out else 0.0
    # half square below the axis, its bottom corners rounded (built mirrored
    # so only those corners round off)
    fr, half = p.IRON_FOOT_CORNER_RADIUS, body_d / 2
    foot = (box(y - half, z - half, y + half, z + half)
            .buffer(-fr, join_style="mitre").buffer(fr, p.ARC_QUAD_SEGMENTS)
            .intersection(box(y - half, z - half, y + half, z)))
    features = [
        (0, p.IRON_HANDLE_LENGTH, tombstone(y, z, *p.IRON_BODY_SECTION)),
        (p.IRON_GRIP_FROM, p.IRON_GRIP_FROM + p.IRON_GRIP_LENGTH,
         tombstone(y, z, *p.IRON_GRIP_SECTION)),
        bump(p.IRON_SCREW_AT, p.IRON_SCREW_HEAD_DIAMETER, p.IRON_SCREW_HEAD_HEIGHT),
        bump(p.IRON_MOUNT_SCREW_AT, p.IRON_MOUNT_SCREW_HEAD_DIAMETER,
             p.IRON_MOUNT_SCREW_HEAD_HEIGHT),
        (p.IRON_FOOT_FROM, p.IRON_FOOT_TO, foot),
        *(bump(at, p.IRON_BUTTON_DIAMETER, p.IRON_BUTTON_HEIGHT, extra)
          for at in p.IRON_BUTTONS_AT),
    ]
    # its tip: the collar's base right against the handle's front (the tip's
    # own base is inside the handle)
    x = p.IRON_HANDLE_LENGTH
    for length, d in tip_profile_past_base():
        features.append((x, x + length, _circle(y, z, d)))
        x += length
    if keep_out:  # the display is flush: it only adds room above it
        w = p.IRON_DISPLAY_WIDTH / 2 + extra
        features.append((p.IRON_DISPLAY_FROM - extra, p.IRON_DISPLAY_TO + extra,
                         box(y - w, flat - 1, y + w, flat + extra)))
    cuts = sorted({x for f in features for x in f[:2]})
    return [(b - a, unary_union([s for f0, f1, s in features if f0 <= a and f1 >= b]))
            for a, b in zip(cuts, cuts[1:])]


@cache
def layout() -> dict[str, Item]:
    """All items, keyed by name: iron, tip_bl, tip_br, tip_tl, tip_tr, key."""
    # with the controls' keep-out: the room the iron's channel takes
    iron = unary_union([s for _, s in _iron_piece_sections(*iron_axis(), keep_out=True)])
    tip_z = FLOOR_Z + p.TIP_DIAMETER / 2
    side_y = _bisect(lambda y: _circle(y, tip_z, p.TIP_DIAMETER).distance(iron) >= ITEM_GAP,
                     0, iron.bounds[2] + ITEM_GAP + p.TIP_DIAMETER)
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


def pieces(name: str, keep_out: bool = False) -> list[tuple[float, float, BaseGeometry]]:
    """(x0, x1, YZ section) of a tip's or the iron's coaxial pieces, in
    ascending X, base first. ``keep_out``: with the extra room round the
    iron's controls (for its channel)."""
    item = layout()[name]
    c = item.section.centroid
    if name == "iron":
        lengths_sections = _iron_piece_sections(*iron_axis(), keep_out=keep_out)
    else:
        lengths_sections = [(length, _circle(c.x, c.y, d)) for length, d in p.TIP_BASE_STEPS]
        lengths_sections += [(length, _circle(c.x, c.y, d))
                             for length, d in tip_profile_past_base()]
    out, x = [], item.x0
    for length, section in lengths_sections:
        out.append((x, x + length, section))
        x += length
    return out


def _stack(name: str) -> Part:
    return Part() + [extrude_x(s, x0, x1) for x0, x1, s in pieces(name)]


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
    out = {"iron": _stack("iron"), "key": key_solid()}
    for name in ("tip_bl", "tip_br", "tip_tl", "tip_tr"):
        out[name] = _stack(name)
    return out
