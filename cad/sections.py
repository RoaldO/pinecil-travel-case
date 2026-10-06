"""Section renders straight from the 3D model, for checking by eye.

    uv run python -m cad.sections   ->  build/sections.svg (+ .png via inkscape)

Cross-sections (YZ) at a few X positions and one long section (XZ) through
the middle, every part in its own colour, assembled (case closed).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from build123d import Edge, GeomType, Plane

from cad import params as p
from cad.band import band_solid
from cad.contents import contents_solids, layout
from cad.insert import insert_a, insert_b
from cad.shell import shell_a, shell_b

BUILD = Path(__file__).resolve().parent.parent / "build"
SAMPLES_PER_CURVE = 24  # points per curved edge in the SVG
PX_PER_MM = 8
GAP = 12.0  # mm between panels

COLOURS = {  # part name -> fill
    "shell A": "#222222", "shell B": "#444444",
    "insert A": "#e91e63", "insert B": "#f06292",
    "band": "#1e88e5",
    "iron": "#2e7d32", "key": "#555555",
    "tip_bl": "#c08a2e", "tip_br": "#c08a2e", "tip_tl": "#c08a2e", "tip_tr": "#c08a2e",
}


def parts() -> dict:
    out = {"shell A": shell_a(), "shell B": shell_b(), "insert A": insert_a(),
           "insert B": insert_b(), "band": band_solid()}
    out.update(contents_solids())
    return out


def _edge_points(edge: Edge) -> list:
    if edge.geom_type == GeomType.LINE:
        return [edge.position_at(0)]
    return [edge.position_at(i / SAMPLES_PER_CURVE) for i in range(SAMPLES_PER_CURVE)]


def _face_path(face, to_2d) -> str:
    d = []
    for wire in [face.outer_wire(), *face.inner_wires()]:
        pts = [to_2d(v) for e in wire.order_edges() for v in _edge_points(e)]
        d.append("M " + " L ".join(f"{a:.3f},{-b:.3f}" for a, b in pts) + " Z")
    return " ".join(d)


def _panel(all_parts: dict, plane: Plane, to_2d, title: str) -> tuple[str, tuple]:
    paths, xs, ys = [], [], []
    for name, solid in all_parts.items():
        for face in solid.intersect(plane) or []:
            paths.append(f'<path d="{_face_path(face, to_2d)}" fill="{COLOURS[name]}" '
                         f'fill-rule="evenodd" stroke="#fff" stroke-width="0.05"/>')
            bb = face.bounding_box()
            for v in (bb.min, bb.max):
                a, b = to_2d(v)
                xs.append(a)
                ys.append(-b)
    box = (min(xs), min(ys), max(xs), max(ys))
    paths.append(f'<text x="{(box[0] + box[2]) / 2:.2f}" y="{box[1] - 3:.2f}" '
                 f'font-size="3" text-anchor="middle">{title}</text>')
    return "".join(paths), box


def render() -> Path:
    all_parts = parts()
    yz = lambda v: (v.Y, v.Z)  # noqa: E731
    first_step = p.TIP_BASE_STEPS[0][0]
    cross = [
        (p.ITEM_START_X + first_step / 2, "punt-voet ø%g" % p.TIP_BASE_STEPS[0][1]),
        (p.ITEM_START_X + first_step + p.TIP_BASE_STEPS[1][0] / 2,
         "punt-voet ø%g" % p.TIP_BASE_STEPS[1][1]),
        ((p.TIP_COLLAR_X + p.SHELL_SPLIT_X) / 2, "kraag"),
        ((p.SHELL_SPLIT_X + p.INSERT_SPLIT_X) / 2, "overlap"),
        (p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP - p.KEY_ALIGN_GROOVE_DEPTH / 2,
         "voorkant A (groefje, magneten)"),
        (p.INSERT_SPLIT_X + 0.1, "voorkant B (trechter, magneten)"),
        ((p.INSERT_SPLIT_X + p.TIP_END_X) / 2, "punt-einden in B"),
        ((p.KEY_SHORT_X0 + p.KEY_SHORT_X1) / 2, "kuiltje + haakse poot"),
        (p.CAVITY_END_X - 20, "punt van de bout"),
        (p.CASE_LENGTH - p.END_CAP_THICKNESS / 2, "kopse kant B (logo)"),
    ]
    panels, x_cursor, top, bottom = [], 0.0, 0.0, 0.0
    for x, title in cross:
        body, (x0, y0, x1, y1) = _panel(all_parts, Plane.YZ.offset(x), yz,
                                        f"x = {x:.1f} — {title}")
        panels.append(f'<g transform="translate({x_cursor - x0:.2f},0)">{body}</g>')
        x_cursor += (x1 - x0) + GAP
        top, bottom = min(top, y0), max(bottom, y1)
    tip_y = layout()["tip_bl"].section.centroid.x
    long_dy, long_w = bottom, 0.0
    for y, title in ((0.0, "lengtedoorsnede y = 0 (dicht)"),
                     (tip_y, f"lengtedoorsnede y = {tip_y:.1f}, door de onderste punten (dicht)")):
        body, (lx0, ly0, lx1, ly1) = _panel(
            all_parts, Plane.XZ.offset(-y), lambda v: (v.X, v.Z), title)
        long_dy += GAP - ly0
        panels.append(f'<g transform="translate({-lx0:.2f},{long_dy:.2f})">{body}</g>')
        long_dy += ly1
        long_w = max(long_w, lx1 - lx0)
    width = max(x_cursor, long_w) + GAP
    height = long_dy - top + GAP
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * PX_PER_MM:.0f}" '
           f'height="{height * PX_PER_MM:.0f}" viewBox="{-GAP / 2} {top - GAP / 2} {width} {height}" '
           f'font-family="sans-serif"><rect x="{-GAP / 2}" y="{top - GAP / 2}" '
           f'width="{width}" height="{height}" fill="white"/>' + "".join(panels) + "</svg>")
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "sections.svg"
    out.write_text(svg)
    to_png(out)
    return out


def to_png(svg: Path) -> None:
    """svg -> png next to it, if inkscape is installed."""
    if inkscape := shutil.which("inkscape"):
        subprocess.run([inkscape, str(svg), "-o", str(svg.with_suffix(".png"))],
                       check=True, capture_output=True)


if __name__ == "__main__":
    print(render())
