"""shapely 2D sections -> build123d solids, in case coordinates."""

from __future__ import annotations

from build123d import Box, Face, Part, Pos, Wire, extrude
from shapely.geometry.base import BaseGeometry

BIG = 1000.0  # larger than any part; for half-space cuts


def _faces(section: BaseGeometry, to_3d) -> list[Face]:
    def wire(ring) -> Wire:
        return Wire.make_polygon([to_3d(a, b) for a, b in ring.coords[:-1]], close=True)

    return [Face(wire(poly.exterior), [wire(h) for h in poly.interiors])
            for poly in getattr(section, "geoms", [section])]


def extrude_x(section_yz: BaseGeometry, x0: float, x1: float) -> Part:
    """Extrude a YZ section (shapely x = Y, y = Z) from x0 to x1."""
    faces = _faces(section_yz, lambda y, z: (x0, y, z))
    return Part() + [extrude(f, x1 - x0, dir=(1, 0, 0)) for f in faces]


def extrude_y(section_xz: BaseGeometry, half_width: float) -> Part:
    """Extrude an XZ section (shapely x = X, y = Z) over y in ±half_width."""
    faces = _faces(section_xz, lambda x, z: (x, half_width, z))
    return Part() + [extrude(f, 2 * half_width, dir=(0, -1, 0)) for f in faces]


def below_x(x: float) -> Part:
    """Half-space x < x (a big box), for splitting parts."""
    return Pos(x - BIG / 2, 0, 0) * Box(BIG, BIG, BIG)
