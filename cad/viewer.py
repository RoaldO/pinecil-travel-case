"""Bake the current geometry into the standalone 3D viewer.

    uv run python -m cad.viewer   ->  build/travel-case-viewer.html

Reads docs/viewer/travel-case-viewer.html as the template, exports every part
as binary STL, base64-embeds them in place of "__GEOM__", fills the spec
sheet ("__SPECS__") from the parameters, and writes one self-contained file.
"""

from __future__ import annotations

import base64
import json
import tempfile
from pathlib import Path

from build123d import Part, export_stl

from cad import params as p
from cad.band import band_solid
from cad.contents import contents_solids
from cad.insert import insert_a, insert_b
from cad.profile import case_height, shell_profile
from cad.shell import shell_a, shell_b

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "docs" / "viewer" / "travel-case-viewer.html"
OUT = ROOT / "build" / "travel-case-viewer.html"


def _stl_b64(shape: Part) -> str:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "part.stl"
        export_stl(shape, str(path))
        return base64.b64encode(path.read_bytes()).decode()


def specs() -> dict[str, str]:
    minx, _, maxx, _ = shell_profile().bounds
    return {
        "Case": f"{p.CASE_LENGTH:.1f} × {maxx - minx:.1f} × {case_height():.1f} mm",
        "Shell A / B": f"{p.SHELL_SPLIT_X:.1f} / {p.CASE_LENGTH - p.SHELL_SPLIT_X:.1f} mm",
        "Insert A / B": f"{p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP - p.INSERT_START_X:.1f} / "
                        f"{p.INSERT_END_X - p.INSERT_SPLIT_X:.1f} mm",
        "Overlap": f"{p.OVERLAP:g} mm",
        "Velcro": f"{p.VELCRO_WIDTH:g} × {p.VELCRO_THICKNESS:g} mm",
        "Logo": f"{p.LOGO_MAX_SIZE:g} mm, ribs {p.RIB_WIDTH:g}",
    }


def main() -> None:
    contents = contents_solids()
    shapes = {
        "shellA": shell_a(), "shellB": shell_b(),
        "insertA": insert_a(), "insertB": insert_b(),
        "band": band_solid(),
        "contents": Part() + list(contents.values()),
    }
    geom = {name: _stl_b64(shape) for name, shape in shapes.items()}
    html = (TEMPLATE.read_text()
            .replace('"__GEOM__"', json.dumps(geom))
            .replace('"__SPECS__"', json.dumps(specs())))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"wrote {OUT}  ({len(html.encode()) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
