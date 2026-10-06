"""shapely 2D sections -> build123d solids, in case coordinates."""

from __future__ import annotations

import math

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


def chamfer_cutter(section_yz: BaseGeometry, face: float, size: float, inward: int,
                   step: float, hole: bool = False, resolution: int = 16) -> Part:
    """Cutter for a 45° chamfer of ``size`` round the edge where the X-wise
    section ``section_yz`` (a solid's outline, or with ``hole`` a cavity)
    meets the end face at x = ``face``; ``inward`` (+1/-1) points from the
    face into the part. Built from ``step``-long slices at their face-side
    size (a step no more than a print layer prints as the chamfer)."""
    n = max(1, math.ceil(size / step - 1e-9))
    out = Part()
    for i in range(n):
        inset = size * (n - i) / n
        if hole:
            ring = section_yz.buffer(inset, resolution)
        else:
            ring = section_yz.buffer(1).difference(section_yz.buffer(-inset, resolution))
        a, b = face + inward * size * i / n, face + inward * size * (i + 1) / n
        out += extrude_x(ring, min(a, b), max(a, b))
    return out


def below_x(x: float) -> Part:
    """Half-space x < x (a big box), for splitting parts."""
    return Pos(x - BIG / 2, 0, 0) * Box(BIG, BIG, BIG)
