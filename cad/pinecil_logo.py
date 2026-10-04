"""Pinecil logo (the PINE64 pinecone) as 2D geometry, plus its rib centrelines.

The artwork is 10 separate pieces (triangles / rhombi / the stemmed base). The
gaps between them — the *ribs* — run along 6 straight lattice lines that cross
on the vertical axis. We recover those centrelines from the artwork itself:

1. every piece's long straight edges are collected;
2. two edges of different pieces that are parallel and close face each other
   across a gap — the line midway between them is a rib centreline segment;
3. collinear segments (a lattice line runs through several gaps) are merged.

The holes are then the original pieces minus a band of ``rib_width`` around
each centreline, so widening the ribs never moves the logo's outer outline.

Everything is computed in SVG units (y down) and converted to mm (y up, logo
bounding box centred on the origin) at the end.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from svgpathtools import Line, parse_path

from cad import params

SVG_PATH = Path(__file__).with_name("pinecil_logo.svg")
SVG_NS = "{http://www.w3.org/2000/svg}"

# Edge detection, in SVG units (the artwork is 54 x 73 units).
MIN_EDGE_LENGTH = 2.0  # shorter segments are corner roundings
MAX_EDGE_BOW = 0.05  # max deviation from the chord, as a fraction of its length
# Two edges face each other across a rib when:
MAX_EDGE_ANGLE = math.radians(8)  # ...they are this close to parallel,
MAX_GAP = 4.0  # ...this close together,
MIN_OVERLAP = 0.5  # ...and overlap this much along their length.
# Rib segments belong to the same lattice line when:
MERGE_ANGLE = math.radians(4)
MERGE_OFFSET = 1.0

Point = tuple[float, float]


@dataclass(frozen=True)
class Piece:
    id: str
    polygon: Polygon
    edges: tuple[tuple[Point, Point], ...]


@dataclass(frozen=True)
class Centerline:
    id: str
    p0: Point
    p1: Point
    gap: float  # width of the original gap along this line
    between: tuple[tuple[str, str], ...]  # piece-id pairs it separates

    @property
    def line(self) -> LineString:
        return LineString([self.p0, self.p1])


# --- SVG parsing -------------------------------------------------------------


def _translate(elem: ET.Element) -> Point:
    m = re.fullmatch(r"\s*translate\(([^)]*)\)\s*", elem.get("transform", ""))
    if not m:
        return 0.0, 0.0
    nums = [float(v) for v in re.split(r"[\s,]+", m.group(1).strip())]
    return nums[0], nums[1] if len(nums) > 1 else 0.0


def _flatten(seg, tx: float, ty: float) -> list[Point]:
    n = 1 if isinstance(seg, Line) else max(4, math.ceil(seg.length() / 0.25))
    return [
        ((z := seg.point(i / n)).real + tx, z.imag + ty) for i in range(n)
    ]


def _straight_edge(seg, tx: float, ty: float) -> tuple[Point, Point] | None:
    a, b = seg.start, seg.end
    length = abs(b - a)
    if length < MIN_EDGE_LENGTH:
        return None
    if not isinstance(seg, Line):
        chord = LineString([(a.real, a.imag), (b.real, b.imag)])
        bow = max(
            chord.distance(LineString([(z.real, z.imag)] * 2))
            for z in (seg.point(i / 16) for i in range(1, 16))
        )
        if bow > MAX_EDGE_BOW * length:
            return None
    return (a.real + tx, a.imag + ty), (b.real + tx, b.imag + ty)


@cache
def pieces_svg() -> tuple[Piece, ...]:
    """The logo pieces in SVG units, ids P1.. ordered top-to-bottom, left-to-right."""
    raw = []
    for elem in ET.parse(SVG_PATH).getroot().iter(f"{SVG_NS}path"):
        tx, ty = _translate(elem)
        path = parse_path(elem.get("d"))
        pts = [p for seg in path for p in _flatten(seg, tx, ty)]
        edges = tuple(e for seg in path if (e := _straight_edge(seg, tx, ty)))
        raw.append((Polygon(pts).buffer(0), edges))
    raw.sort(key=lambda r: (round(r[0].centroid.y), r[0].centroid.x))
    return tuple(Piece(f"P{i}", poly, edges) for i, (poly, edges) in enumerate(raw, 1))


# --- Centrelines -------------------------------------------------------------


def _unit(p: Point, q: Point) -> Point:
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def _rib_segment(e1, e2):
    """Midline between two facing edges, or None if they don't face each other."""
    d1, d2 = _unit(*e1), _unit(*e2)
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) > math.sin(MAX_EDGE_ANGLE):
        return None
    if d1[0] * d2[0] + d1[1] * d2[1] < 0:
        d2 = (-d2[0], -d2[1])
    d = _unit((0, 0), (d1[0] + d2[0], d1[1] + d2[1]))
    n = (-d[1], d[0])
    off1 = sum(n[i] * (e1[0][i] + e1[1][i]) / 2 for i in range(2))
    off2 = sum(n[i] * (e2[0][i] + e2[1][i]) / 2 for i in range(2))
    gap = abs(off2 - off1)
    if gap > MAX_GAP:
        return None
    t1 = sorted(d[0] * p[0] + d[1] * p[1] for p in e1)
    t2 = sorted(d[0] * p[0] + d[1] * p[1] for p in e2)
    if min(t1[1], t2[1]) - max(t1[0], t2[0]) < MIN_OVERLAP:
        return None
    off, t0, t1 = (off1 + off2) / 2, min(t1[0], t2[0]), max(t1[1], t2[1])
    p0 = (n[0] * off + d[0] * t0, n[1] * off + d[1] * t0)
    p1 = (n[0] * off + d[0] * t1, n[1] * off + d[1] * t1)
    return p0, p1, gap


def _perp_dist(p: Point, origin: Point, d: Point) -> float:
    return abs((p[0] - origin[0]) * d[1] - (p[1] - origin[1]) * d[0])


def _fit_line(segments) -> tuple[Point, Point]:
    """Total-least-squares line through all segment endpoints, spanning them."""
    pts = [p for s in segments for p in s[:2]]
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    theta = 0.5 * math.atan2(2 * sxy, sxx - syy)
    d = (math.cos(theta), math.sin(theta))
    if d[0] < 0:
        d = (-d[0], -d[1])
    ts = [(p[0] - mx) * d[0] + (p[1] - my) * d[1] for p in pts]
    return (
        (mx + d[0] * min(ts), my + d[1] * min(ts)),
        (mx + d[0] * max(ts), my + d[1] * max(ts)),
    )


@cache
def centerlines_svg() -> tuple[Centerline, ...]:
    """Rib centrelines in SVG units, ids L1.. (merged collinear rib segments)."""
    pieces = pieces_svg()
    segments = []  # (p0, p1, gap, (piece ids))
    for i, a in enumerate(pieces):
        for b in pieces[i + 1 :]:
            for e1 in a.edges:
                for e2 in b.edges:
                    if seg := _rib_segment(e1, e2):
                        segments.append((*seg, (a.id, b.id)))

    # A lattice line runs through several gaps: group collinear segments.
    groups: list[list] = []
    for seg in segments:
        mid = ((seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2)
        d = _unit(seg[0], seg[1])
        for g in groups:
            g0, g1 = _fit_line(g)
            gd = _unit(g0, g1)
            parallel = abs(gd[0] * d[1] - gd[1] * d[0]) < math.sin(MERGE_ANGLE)
            if parallel and _perp_dist(mid, g0, gd) < MERGE_OFFSET:
                g.append(seg)
                break
        else:
            groups.append([seg])

    lines = []
    for g in groups:
        p0, p1 = _fit_line(g)
        gap = sum(s[2] for s in g) / len(g)
        lines.append((p0, p1, gap, tuple(sorted({s[3] for s in g}))))
    # Stable ids: "\" lines (falling to the right in the drawing) first, then
    # "/" lines, each top to bottom by where they cross the logo's axis.
    axis_x = unary_union([p.polygon for p in pieces]).centroid.x

    def key(line):
        (x0, y0), (x1, y1), *_ = line
        slope = (y1 - y0) / (x1 - x0)
        return (slope < 0, y0 + slope * (axis_x - x0))

    lines.sort(key=key)
    return tuple(Centerline(f"L{i}", *line) for i, line in enumerate(lines, 1))


# --- mm conversion -----------------------------------------------------------


def _to_mm_params(max_size: float):
    minx, miny, maxx, maxy = unary_union([p.polygon for p in pieces_svg()]).bounds
    scale = max_size / max(maxx - minx, maxy - miny)
    return scale, (minx + maxx) / 2, (miny + maxy) / 2


def to_mm(geom, max_size: float = params.LOGO_MAX_SIZE):
    """SVG-unit shapely geometry -> mm, y up, logo bbox centred on the origin."""
    scale, cx, cy = _to_mm_params(max_size)
    geom = affinity.translate(geom, -cx, -cy)
    return affinity.scale(geom, scale, -scale, origin=(0, 0))


def scale_mm(max_size: float = params.LOGO_MAX_SIZE) -> float:
    """mm per SVG unit."""
    return _to_mm_params(max_size)[0]


def outline_mm(max_size: float = params.LOGO_MAX_SIZE):
    """The original artwork (all pieces as one geometry), in mm."""
    return to_mm(unary_union([p.polygon for p in pieces_svg()]), max_size)


def centerlines_mm(max_size: float = params.LOGO_MAX_SIZE) -> dict[str, LineString]:
    return {c.id: to_mm(c.line, max_size) for c in centerlines_svg()}


def holes_mm(
    rib_width: float = params.RIB_WIDTH, max_size: float = params.LOGO_MAX_SIZE
) -> list[Polygon]:
    """The logo holes in mm: each piece minus a ``rib_width`` band per centreline.

    Within its own length a band cuts every piece (so corners that approach a
    rib where two ribs meet at the outline are cut too). Past its ends it is
    extended to clear rounded corners, but that extension only cuts the pieces
    the line actually separates — otherwise it would nick a neighbour.
    """
    bands: dict[str, list] = {p.id: [] for p in pieces_svg()}
    for c in centerlines_svg():
        line = to_mm(c.line, max_size)
        (x0, y0), (x1, y1) = line.coords
        ux, uy = _unit((x0, y0), (x1, y1))
        ext = LineString(
            [(x0 - ux * rib_width, y0 - uy * rib_width),
             (x1 + ux * rib_width, y1 + uy * rib_width)]
        )
        core = line.buffer(rib_width / 2, cap_style="flat")
        extended = ext.buffer(rib_width / 2, cap_style="flat")
        separated = {pid for pair in c.between for pid in pair}
        for pid, cuts in bands.items():
            cuts.append(extended if pid in separated else core)
    holes = []
    for piece in pieces_svg():
        cut = to_mm(piece.polygon, max_size).difference(
            unary_union(bands[piece.id])
        )
        holes.extend(getattr(cut, "geoms", [cut]))
    return [h for h in holes if not h.is_empty]
