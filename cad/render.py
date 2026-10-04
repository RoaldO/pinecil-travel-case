"""Validation render: the artwork with its rib centrelines, and the resulting holes.

    uv run python -m cad.render   ->  build/logo-centerlines.svg (+ .png if inkscape)

Left panel: the original logo (one object, grey), piece ids P1.. and every rib
centreline in its own colour with its id L1... Right panel: the test plate as
modelled with the current RIB_WIDTH — holes white, centrelines thin.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from shapely.geometry import box
from shapely.ops import unary_union

from cad import params
from cad.pinecil_logo import centerlines_mm, holes_mm, outline_mm, pieces_svg, to_mm

BUILD = Path(__file__).resolve().parent.parent / "build"
COLORS = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#00a0a0",
          "#f032e6", "#9a6324", "#808000", "#000075"]
PX_PER_MM = 40


def _path(geom) -> str:
    """Shapely (multi)polygon in mm -> SVG path data (y flipped back to down)."""
    polys = getattr(geom, "geoms", [geom])
    d = []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = " L ".join(f"{x:.4f},{-y:.4f}" for x, y in ring.coords)
            d.append(f"M {pts} Z")
    return " ".join(d)


def _panel(dx: float, title: str, body: list[str]) -> str:
    return (
        f'<g transform="translate({dx},0)">'
        f'<text x="0" y="-13.6" font-size="1" text-anchor="middle">{title}</text>'
        + "".join(body)
        + "</g>"
    )


def render(rib_width: float = params.RIB_WIDTH,
           max_size: float = params.LOGO_MAX_SIZE) -> Path:
    outline = outline_mm(max_size)
    lines = centerlines_mm(max_size)
    minx, miny, maxx, maxy = outline.bounds

    # Panel 1: artwork + centrelines + ids.
    art = [f'<path d="{_path(outline)}" fill="#c8c8c8" id="pinecil-logo"/>']
    for piece in pieces_svg():
        c = to_mm(piece.polygon, max_size).representative_point()
        art.append(f'<text x="{c.x:.3f}" y="{-c.y:.3f}" font-size="0.7" '
                   f'text-anchor="middle" dominant-baseline="middle" '
                   f'fill="#555">{piece.id}</text>')
    for i, (lid, line) in enumerate(lines.items()):
        color = COLORS[i % len(COLORS)]
        (x0, y0), (x1, y1) = line.coords
        art.append(f'<line id="{lid}" x1="{x0:.4f}" y1="{-y0:.4f}" x2="{x1:.4f}" '
                   f'y2="{-y1:.4f}" stroke="{color}" stroke-width="0.12" '
                   f'stroke-linecap="round"/>')
        # Label beyond one end: "\" lines on the right, "/" lines on the left,
        # so labels of lines ending close together don't collide.
        ux, uy = (x1 - x0) / line.length, (y1 - y0) / line.length
        if y1 < y0:  # "\" line: falls to the right
            lx, ly = x1 + ux * 0.8, y1 + uy * 0.8
        else:
            lx, ly = x0 - ux * 0.8, y0 - uy * 0.8
        art.append(f'<text x="{lx:.3f}" y="{-ly:.3f}" font-size="0.9" '
                   f'font-weight="bold" fill="{color}" text-anchor="middle" '
                   f'dominant-baseline="middle">{lid}</text>')
    bbox = (f'<rect x="{minx:.4f}" y="{-maxy:.4f}" width="{maxx - minx:.4f}" '
            f'height="{maxy - miny:.4f}" fill="none" stroke="#999" '
            f'stroke-width="0.04" stroke-dasharray="0.3 0.2"/>')
    art.append(bbox)
    art.append(f'<text x="0" y="{-miny + 1.3:.3f}" font-size="0.7" '
               f'text-anchor="middle">{maxx - minx:.2f} × {maxy - miny:.2f} mm '
               f'(max {max_size:g})</text>')

    # Panel 2: test plate with the holes.
    m = params.PLATE_MARGIN
    plate = box(minx - m, miny - m, maxx + m, maxy + m)
    cut = plate.difference(unary_union(holes_mm(rib_width, max_size)))
    res = [f'<path d="{_path(cut)}" fill="#3a3a3a" fill-rule="evenodd"/>']
    for i, (lid, line) in enumerate(lines.items()):
        (x0, y0), (x1, y1) = line.coords
        res.append(f'<line x1="{x0:.4f}" y1="{-y0:.4f}" x2="{x1:.4f}" y2="{-y1:.4f}" '
                   f'stroke="{COLORS[i % len(COLORS)]}" stroke-width="0.03"/>')

    gap = 18 + 2 * m
    w, h = 2 * gap + 4, 2 * (maxy + m) + 4
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w * PX_PER_MM:.0f}" height="{h * PX_PER_MM:.0f}" '
        f'viewBox="{-gap / 2 - 2} {-h / 2} {w} {h}" font-family="sans-serif">'
        f'<rect x="{-gap / 2 - 2}" y="{-h / 2}" width="{w}" height="{h}" fill="white"/>'
        + _panel(0, "artwork + rib centrelines", art)
        + _panel(gap, f"plate, rib width {rib_width:g} mm", res)
        + "</svg>"
    )
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "logo-centerlines.svg"
    out.write_text(svg)
    if inkscape := shutil.which("inkscape"):
        subprocess.run([inkscape, str(out), "-o", str(out.with_suffix(".png"))],
                       check=True, capture_output=True)
    return out


if __name__ == "__main__":
    print(render())
