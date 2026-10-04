"""build123d geometry: the Pinecil logo as a cutter, and a test plate.

    uv run python -m cad.build   ->  build/logo-plate.step + build/logo-plate.stl

``logo_cutter`` is the reusable part: the travel case will subtract it from its
lid later. The test plate exists to print-check rib width until then.
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


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    plate = logo_plate()
    export_step(plate, str(BUILD / "logo-plate.step"))
    export_stl(plate, str(BUILD / "logo-plate.stl"))
    bb = plate.bounding_box()
    print(f"logo-plate: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm, "
          f"rib width {params.RIB_WIDTH} mm -> {BUILD}")


if __name__ == "__main__":
    main()
