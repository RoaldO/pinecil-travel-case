"""build123d geometry: the Pinecil logo as a cutter, a test plate, and the
export of every printable part.

    uv run python -m cad.build   ->  build/<part>.step + build/<part>.stl
                                     for logo-plate, shell-a, shell-b,
                                     insert-a, insert-b

``logo_cutter`` is the reusable part: shell B subtracts it from its end cap.
The test plate exists to print-check rib width.
"""

from __future__ import annotations

from pathlib import Path

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Part,
    Polygon,
    export_step,
    export_stl,
    extrude,
)

from cad import params
from cad.pinecil_logo import holes_mm, outline_mm

BUILD = Path(__file__).resolve().parent.parent / "build"


def logo_cutter(
    depth: float,
    rib_width: float = params.RIB_WIDTH,
    max_size: float = params.LOGO_MAX_SIZE,
) -> Part:
    """The logo holes extruded from z=0 to z=depth, centred on the origin."""
    with BuildPart() as cutter:
        with BuildSketch():
            for hole in holes_mm(rib_width, max_size):
                Polygon(*hole.exterior.coords[:-1], align=None)
        extrude(amount=depth)
    return cutter.part


def logo_plate(
    rib_width: float = params.RIB_WIDTH,
    max_size: float = params.LOGO_MAX_SIZE,
    thickness: float = params.PLATE_THICKNESS,
    margin: float = params.PLATE_MARGIN,
) -> Part:
    minx, miny, maxx, maxy = outline_mm(max_size).bounds
    body = Box(
        maxx - minx + 2 * margin, maxy - miny + 2 * margin, thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body - logo_cutter(thickness, rib_width, max_size)


def case_parts() -> dict[str, Part]:
    """Every printable case part, keyed by output file stem."""
    # Imported here: cad.shell imports logo_cutter from this module.
    from cad.insert import insert_a, insert_b
    from cad.shell import shell_a, shell_b

    return {"shell-a": shell_a(), "shell-b": shell_b(),
            "insert-a": insert_a(), "insert-b": insert_b()}


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    parts = {"logo-plate": logo_plate(), **case_parts()}
    for stem, part in parts.items():
        export_step(part, str(BUILD / f"{stem}.step"))
        export_stl(part, str(BUILD / f"{stem}.stl"))
        bb = part.bounding_box()
        print(f"{stem:11s} {bb.size.X:6.1f} x {bb.size.Y:5.1f} x {bb.size.Z:5.1f} mm")
    print(f"-> {BUILD}")


if __name__ == "__main__":
    main()
