"""2D cross-sections (YZ plane, shapely): channels, insert and shell profiles.

Insert: the smallest symmetric rounded trapezoid that keeps INSERT_WALL around
every channel and magnet hole. Shell: the same trapezoid grown by GLUE_CLEARANCE +
SHELL_SIDE_WALL at the sides and out to the top/bottom wall thickness, with z=0
at its bottom face.
"""

from __future__ import annotations

import math
from functools import cache

from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.contents import layout

FIT_RESOLUTION = 0.01  # mm, bisection tolerance for the trapezoid fit
TOP_SEARCH_COARSE = 0.5  # mm, first pass over the top half-width
TOP_SEARCH_FINE = 0.05  # mm, second pass around the best coarse value
AREA_TOLERANCE = 1e-6  # mm², ignore numerical slivers when testing a fit


def rounded_trapezoid(bottom_hw: float, top_hw: float, z0: float, z1: float,
                      radius: float) -> BaseGeometry:
    """Symmetric trapezoid (half-widths at z0 and z1) with rounded corners."""
    core = Polygon([(-bottom_hw, z0), (bottom_hw, z0), (top_hw, z1), (-top_hw, z1)])
    return core.buffer(-radius, join_style="mitre").buffer(radius, p.ARC_QUAD_SEGMENTS)


def _fits(outer: BaseGeometry, inner: BaseGeometry) -> bool:
    return inner.difference(outer).area < AREA_TOLERANCE


@cache
def channel_sections() -> dict[str, BaseGeometry]:
    """Each item's YZ section grown by ITEM_CLEARANCE."""
    return {k: v.section.buffer(p.ITEM_CLEARANCE, p.ARC_QUAD_SEGMENTS) for k, v in layout().items()}


def magnet_hole_radius() -> float:
    return p.MAGNET_DIAMETER / 2 + p.MAGNET_CLEARANCE


@cache
def magnet_spots() -> tuple[tuple[float, float], ...]:
    """(y, z) of the magnet holes: the two bottom corners — on the floor,
    INSERT_WALL outboard of the bottom tips' channels — and one centred in
    the top, level with the top tips' channels."""
    ch = channel_sections()
    r = magnet_hole_radius()
    tip = ch["tip_br"]
    c = tip.centroid
    tip_r = (tip.bounds[2] - tip.bounds[0]) / 2
    z = tip.bounds[1] + r
    dz = c.y - z
    y = c.x + math.sqrt((tip_r + p.INSERT_WALL + r) ** 2 - dz ** 2)
    top = ch["tip_tl"].bounds[3] - r
    return (-y, z), (y, z), (0.0, top)


def magnet_section() -> BaseGeometry:
    """YZ footprint of the magnet holes."""
    return unary_union([Point(y, z).buffer(magnet_hole_radius(), p.ARC_QUAD_SEGMENTS)
                        for y, z in magnet_spots()])


@cache
def insert_trapezoid() -> tuple[float, float, float, float]:
    """(bottom_hw, top_hw, z0, z1) of the insert's core trapezoid."""
    # The trapezoid is convex, so fitting the convex hull is exact and far cheaper.
    need = (unary_union([*channel_sections().values(), magnet_section()])
            .buffer(p.INSERT_WALL, p.ARC_QUAD_SEGMENTS).convex_hull)
    # Bottom is exact by construction (the bottom row stands on it); the
    # polygonised channels would put it a hair higher.
    z0 = p.SHELL_BOTTOM_WALL + p.GLUE_CLEARANCE
    z1 = need.bounds[3]
    r = p.INSERT_CORNER_RADIUS
    max_hw = need.bounds[2] + 2 * r  # no useful trapezoid is wider than this

    def min_bottom(top: float) -> float | None:
        """Smallest bottom half-width that fits for this top, or None."""
        lo, hi = top, 3 * max_hw
        if not _fits(rounded_trapezoid(hi, top, z0, z1, r), need):
            return None
        while hi - lo > FIT_RESOLUTION:
            mid = (lo + hi) / 2
            if _fits(rounded_trapezoid(mid, top, z0, z1, r), need):
                hi = mid
            else:
                lo = mid
        return hi

    def search(tops) -> tuple[float, float, float] | None:
        best = None
        for top in tops:
            bottom = min_bottom(top)
            if bottom is not None and (best is None or bottom + top < best[0]):
                best = (bottom + top, bottom, top)  # area ∝ bottom + top
        return best

    n = int(max_hw / TOP_SEARCH_COARSE)
    best = search(i * TOP_SEARCH_COARSE for i in range(1, n + 1))
    centre = best[2]
    m = int(TOP_SEARCH_COARSE / TOP_SEARCH_FINE)
    best = search(centre + i * TOP_SEARCH_FINE for i in range(-m, m + 1)) or best
    _, bottom_hw, top_hw = best
    top_hw = _widen_for_flush_groove(bottom_hw, top_hw, z0, z1)
    return bottom_hw, top_hw + p.TOP_EXTRA_WIDTH / 2, z0, z1


def _widen_for_flush_groove(bottom_hw: float, top_hw: float, z0: float, z1: float) -> float:
    """Smallest top half-width >= ``top_hw`` at which the band's edges still
    lie a full layer deep in the top groove (a wider strap widens the top)."""
    def flush(top: float) -> bool:
        shell = _shell_around((bottom_hw, top, z0, z1))
        return groove_edge_walls(shell)[0] >= p.VELCRO_THICKNESS

    if flush(top_hw):
        return top_hw
    lo, hi = top_hw, top_hw + band_half_width()
    while hi - lo > FIT_RESOLUTION:
        mid = (lo + hi) / 2
        if flush(mid):
            hi = mid
        else:
            lo = mid
    return hi


def insert_profile() -> BaseGeometry:
    b, t, z0, z1 = insert_trapezoid()
    return rounded_trapezoid(b, t, z0, z1, p.INSERT_CORNER_RADIUS)


def _grown_trapezoid(trap, side: float, bottom: float, top: float):
    """Insert trapezoid ``trap`` with its sides moved out by ``side``
    (perpendicular) and its bottom/top faces moved out by ``bottom``/``top``."""
    b, t, z0, z1 = trap
    slope = (b - t) / (z1 - z0)  # half-width lost per mm of height
    shift = side * math.hypot(1, slope)  # horizontal shift of a slanted side
    nz0, nz1 = z0 - bottom, z1 + top
    nb = b + shift + slope * bottom
    nt = t + shift - slope * top
    return nb, nt, nz0, nz1


def shell_profile() -> BaseGeometry:
    """Outer contour of the shell (z=0 at the bottom face)."""
    return _shell_around(insert_trapezoid())


def _shell_around(trap) -> BaseGeometry:
    side = p.GLUE_CLEARANCE + p.SHELL_SIDE_WALL
    nb, nt, nz0, nz1 = _grown_trapezoid(
        trap,
        side,
        p.GLUE_CLEARANCE + p.SHELL_BOTTOM_WALL,
        p.GLUE_CLEARANCE + p.SHELL_TOP_WALL,
    )
    return rounded_trapezoid(nb, nt, nz0, nz1, p.INSERT_CORNER_RADIUS + side)


def insert_cavity(clearance: float) -> BaseGeometry:
    """Insert profile grown by ``clearance`` (the hole in the shell)."""
    return insert_profile().buffer(clearance, p.ARC_QUAD_SEGMENTS)


def case_height() -> float:
    return shell_profile().bounds[3]


def band_half_width() -> float:
    """Half the width of the band channel (band + clearance)."""
    return p.VELCRO_WIDTH / 2 + p.VELCRO_CLEARANCE


def groove_edge_walls(shell: BaseGeometry | None = None) -> tuple[float, float]:
    """(top, bottom): height of the shell's surface above / below the groove
    floor at the groove's edges. The band lies flush only if these are at
    least one band layer (top) and VELCRO_BOTTOM_LAYERS layers (bottom)."""
    shell = shell_profile() if shell is None else shell
    _, z0, _, z1 = shell.bounds
    edge = LineString([(band_half_width(), z0 - 1), (band_half_width(), z1 + 1)])
    _, lo, _, hi = shell.intersection(edge).bounds
    return hi - (z1 - p.RING_TOP), p.RING_BOTTOM - (lo - z0)
