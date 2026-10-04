"""The velcro band channel ("band ring").

In side view (XZ) the band follows the gap between two almost-concentric
rounded blocks: the outer block is the case without its end caps; the inner
block is one band layer smaller at the top and the ends and
VELCRO_BOTTOM_LAYERS layers smaller at the bottom. Outer minus inner is the
ring; extruded across the band width it is subtracted from shell and insert.
That one cut makes the flush top groove, the deeper bottom groove, the bends
and the channel behind the end caps.
"""

from __future__ import annotations

from functools import cache

from build123d import Part
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

from cad import params as p
from cad.profile import case_height
from cad.solids import extrude_y

BAND_HALF_WIDTH = p.VELCRO_WIDTH / 2 + p.VELCRO_CLEARANCE


def _rounded_box(x0: float, z0: float, x1: float, z1: float, r: float) -> BaseGeometry:
    return box(x0, z0, x1, z1).buffer(-r, join_style="mitre").buffer(r, p.ARC_QUAD_SEGMENTS)


def outer_block() -> BaseGeometry:
    return _rounded_box(p.END_CAP_THICKNESS, 0.0,
                        p.CASE_LENGTH - p.END_CAP_THICKNESS, case_height(),
                        p.BAND_BEND_RADIUS + p.RING_END)


def inner_block() -> BaseGeometry:
    return _rounded_box(p.END_CAP_THICKNESS + p.RING_END, p.RING_BOTTOM,
                        p.CASE_LENGTH - p.END_CAP_THICKNESS - p.RING_END,
                        case_height() - p.RING_TOP,
                        p.BAND_BEND_RADIUS)


def ring_section() -> BaseGeometry:
    """The band channel in side view (XZ plane: x = X, y = Z)."""
    return outer_block().difference(inner_block())


def straight_run_z() -> tuple[float, float]:
    """Z range of the straight vertical part of the band behind the end caps."""
    return (p.RING_BOTTOM + p.BAND_BEND_RADIUS,
            case_height() - p.RING_TOP - p.BAND_BEND_RADIUS)


@cache
def ring_solid() -> Part:
    """The band channel as a solid, to subtract from shell and insert."""
    return extrude_y(ring_section(), BAND_HALF_WIDTH)


@cache
def band_solid() -> Part:
    """The velcro itself (no clearance), for the viewer."""
    half = p.VELCRO_WIDTH / 2
    c = p.VELCRO_CLEARANCE / 2
    section = (_rounded_box(p.END_CAP_THICKNESS + c, c,
                            p.CASE_LENGTH - p.END_CAP_THICKNESS - c, case_height(),
                            p.BAND_BEND_RADIUS + p.RING_END - c)
               .difference(inner_block().buffer(c, p.ARC_QUAD_SEGMENTS)))
    return extrude_y(section, half)
