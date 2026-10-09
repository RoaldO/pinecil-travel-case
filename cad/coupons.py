"""Test-print coupons: thin slices of the real parts where the fit matters.

    uv run python -m cad.coupons   ->  build/coupons/*.stl (+ .step),
                                       coupons.svg (+ .png): bottom and top

Each coupon is a part cut between two X positions, turned the way the real
part prints (axis up, the same face on the bed), so overhangs and elephant's
foot match. Try the real tips, iron, key and magnets in them, then correct
the clearances in cad/params.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from build123d import Part, Plane, Pos, Rot, export_step, export_stl

from cad import params as p
from cad.insert import insert_a, insert_b
from cad.shell import shell_a, shell_b
from cad.solids import below_x

OUT = Path(__file__).resolve().parent.parent / "build" / "coupons"
COUPON = 8.0  # mm, default slice thickness


@dataclass(frozen=True)
class Coupon:
    stem: str
    part: object  # callable -> Part
    colour: str  # cad.sections colour key
    x0: float
    x1: float
    bed_low_x: bool  # True: the part prints with its low-X end on the bed
    tests: str


def coupons() -> list[Coupon]:
    face_a = p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP
    return [
        Coupon("1-insert-a-collar", insert_a, "insert A", p.TIP_COLLAR_X - 4, p.TIP_COLLAR_X + 6, True,
               "tip bores 5.7 -> collar seat -> ring; iron tombstone bore with the "
               "display / button / screw grooves"),
        Coupon("2a-insert-a-face", insert_a, "insert A", face_a - COUPON, face_a, True,
               "slides into 2b; lead-in, magnets, key hole + alignment groove"),
        Coupon("2b-shell-b-mouth", shell_b, "shell B", p.SHELL_SPLIT_X, p.SHELL_SPLIT_X + COUPON, False,
               "takes 2a: slide clearance, mouth chamfer"),
        Coupon("3-insert-b-face", insert_b, "insert B", p.INSERT_SPLIT_X, p.INSERT_SPLIT_X + COUPON, False,
               "clicks onto 2a (magnets); funnel with the real key; tip-end bores; "
               "mounting-screw and foot grooves"),
        Coupon("4a-shell-a-end", shell_a, "shell A", 0.0, COUPON, True,
               "takes 4b: glue clearance, PLA end stops beside the band, band channel"),
        Coupon("4b-insert-a-end", insert_a, "insert A", p.INSERT_START_X,
               p.INSERT_START_X + COUPON, True,
               "glues into 4a: flat print face (no bridge), bed chamfer, end stop"),
    ]


def slice_part(c: Coupon) -> Part:
    """The coupon, turned so it prints like its part: on the bed at z = 0,
    centred on the origin."""
    slab = below_x(c.x1) - below_x(c.x0)
    piece = c.part() & slab
    piece = (Rot(0, -90, 0) if c.bed_low_x else Rot(0, 90, 0)) * piece
    bb = piece.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * piece


def overview(parts: dict[Coupon, Part]) -> Path:
    """coupons.svg (+ .png): each coupon's bottom (on the bed) and top, seen
    from above."""
    from cad.sections import GAP, PX_PER_MM, _panel, to_png

    rows, y_cursor, width = [], 0.0, 0.0
    for c, part in parts.items():
        h = part.bounding_box().size.Z
        x_cursor, row_h = 0.0, 0.0
        for z, side in ((0.05, "onder (bed)"), (h - 0.05, "boven")):
            body, (x0, y0, x1, y1) = _panel({c.colour: part}, Plane.XY.offset(z),
                                            lambda v: (v.X, v.Y), f"{c.stem} — {side}")
            rows.append(f'<g transform="translate({x_cursor - x0:.2f},{y_cursor - y0:.2f})">'
                        f'{body}</g>')
            x_cursor += (x1 - x0) + GAP
            row_h = max(row_h, y1 - y0)
        y_cursor += row_h + GAP
        width = max(width, x_cursor)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * PX_PER_MM:.0f}" '
           f'height="{y_cursor * PX_PER_MM:.0f}" viewBox="{-GAP / 2} {-GAP} {width} {y_cursor}" '
           f'font-family="sans-serif"><rect x="{-GAP / 2}" y="{-GAP}" width="{width}" '
           f'height="{y_cursor}" fill="white"/>' + "".join(rows) + "</svg>")
    out = OUT / "coupons.svg"
    out.write_text(svg)
    to_png(out)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {}
    for c in coupons():
        part = parts[c] = slice_part(c)
        export_stl(part, str(OUT / f"{c.stem}.stl"))
        export_step(part, str(OUT / f"{c.stem}.step"))
        bb = part.bounding_box()
        print(f"{c.stem:18s} {bb.size.X:5.1f} x {bb.size.Y:5.1f} x {bb.size.Z:4.1f} mm  {c.tests}")
    print(overview(parts))
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
