# Pinecil Travel Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the four printable parts of the Pinecil V2 travel case (shell A/B in PLA, insert A/B in PETG) parametrically in build123d, with section renders and an interactive 3D viewer to check them.

**Architecture:** 2D cross-sections are computed in shapely (item layout → channels → fitted rounded-trapezoid insert profile → shell profile; band ring in side view), then extruded and combined into solids with build123d. Every dimension lives in `cad/params.py`; derived values are computed there or from the profiles. Each module has one job and is tested on its own; 3D tests check validity, print size, non-overlap and the spec's fit criteria.

**Tech Stack:** Python ≥ 3.11 via `uv`, build123d 0.11, shapely ≥ 2, svgpathtools, pytest; three.js r128 (CDN) in the viewer; `make` targets.

**Spec:** `docs/superpowers/specs/2026-10-04-travel-case-design.md` (decisions D1–D13, parameters, acceptance criteria 1–12). Plain-language model: `docs/model.md`.

## Global Constraints

- Python only through `uv` (`uv run …`); never the system Python. `make`, not `just`.
- No magic numbers: every dimension is a named constant in `cad/params.py`; derived values are computed, never typed (spec D13).
- Coordinates: X along the case from half A's end face (x = 0); Z up from the wide bottom face (z = 0); Y across, y = 0 the symmetry plane.
- Printer: `MAX_PRINT_HEIGHT` = 180, `PRINT_BED` = 180 (mm). Every part prints standing (axis vertical).
- Commit after every task (`git commit`, no push). Each commit message ends with the line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Existing logo code (`cad/pinecil_logo.py`, `cad/render.py`, `tests/test_logo.py`) stays as is; `cad/build.py` is only extended.
- Run the full suite with `make test` at the end of every task; all earlier tests must stay green.

## Review Focus

1. **A changed parameter breaks the fit silently** — e.g. bigger `TIP_DIAMETER` or `VELCRO_THICKNESS`. Expect: the layout, profiles and lengths regrow and the acceptance tests still pass or fail loudly. Pinned by `test_layout_is_symmetric`, `test_channels_keep_insert_wall_to_the_surface`, `test_short_leg_clears_the_iron` (Tasks 2–3) — all computed from params, none hard-code sizes.
2. **The key's short leg hits the iron or leaves the insert** at another `KEY_LEG_ANGLE` / `KEY_LEG_SIDE`. Expect a failing test, not a silent clash. Pinned by `test_short_leg_clears_the_iron` (Task 2) and `test_short_leg_fits_inside_the_insert` (Task 3).
3. **The band can't be threaded after gluing** (ring pinched somewhere, e.g. at the bends). Expect the ring to stay a closed loop at least one band + clearance thick. Pinned by `test_ring_is_thick_enough_everywhere_to_thread_the_band` (Task 4).
4. **Parts overlap when assembled or a part splits into islands** after a boolean (e.g. the pocket cuts an insert in two). Expect one valid solid per part and zero overlap volume. Pinned by `test_*_is_one_valid_solid` and `test_assembled_parts_do_not_overlap` (Tasks 5–6).
5. **Logo shows the band's bend or ends up upside down / sideways.** Expect it centred on the straight band run, upright. Pinned by `test_logo_sits_on_the_straight_band_run` and `test_logo_is_upright` (Task 6).

## File structure

| File | Responsibility |
|---|---|
| `cad/params.py` (modify) | all case parameters + derived values |
| `cad/contents.py` (new) | item envelopes: 2D layout B, key short leg, 3D solids |
| `cad/profile.py` (new) | channel sections, fitted insert trapezoid, shell profile |
| `cad/solids.py` (new) | shapely section → build123d extrusions, half-space helper |
| `cad/band.py` (new) | band ring (outer − inner rounded block), band solid |
| `cad/insert.py` (new) | insert solid, grip pocket, split A/B |
| `cad/shell.py` (new) | shell solid, overlap clearance, logo on B, split A/B |
| `cad/build.py` (modify) | export every part as STEP + STL |
| `cad/sections.py` (new) | section renders from the 3D model |
| `cad/viewer.py`, `docs/viewer/travel-case-viewer.html` (new) | standalone 3D viewer |
| `tests/test_case_params.py`, `test_contents.py`, `test_profile.py`, `test_band.py`, `test_insert.py`, `test_shell.py`, `test_outputs.py` (new) | one per module |
| `Makefile`, `README.md`, `CLAUDE.md`, `TODO.md` (modify) | targets and docs |

---

### Task 1: Case parameters

**Files:**
- Modify: `cad/params.py` (add `import math` after the docstring; append the case block at the end)
- Test: `tests/test_case_params.py`

**Interfaces:**
- Produces (module constants in `cad.params`): all spec parameters, plus derived `KEY_HEX_CORNERS`, `RING_END`, `RING_TOP`, `RING_BOTTOM`, `SHELL_TOP_WALL`, `SHELL_BOTTOM_WALL`, `CAVITY_LENGTH`, `CAVITY_START_X`, `CAVITY_END_X`, `CASE_LENGTH`, `ITEM_START_X`, `TIP_END_X`, `INSERT_SPLIT_X`, `SHELL_SPLIT_X`, `KEY_SHORT_X0`, `KEY_SHORT_X1`, `KEY_LONG_X0`, and `ARC_QUAD_SEGMENTS`.

- [ ] **Step 1: Write the failing test** — create `tests/test_case_params.py`:

```python
"""Derived dimensions (spec criterion 9) and print limits (criterion 2)."""

import pytest

from cad import params as p


def test_case_length_is_the_sum_of_its_layers():
    ends = 2 * (p.END_CAP_THICKNESS + p.RING_END + p.INSERT_END_WALL)
    assert p.CASE_LENGTH == pytest.approx(ends + p.IRON_LENGTH + 2 * p.ITEM_END_CLEARANCE)


def test_insert_split_leaves_tip_grip():
    assert p.TIP_END_X - p.INSERT_SPLIT_X == pytest.approx(p.TIP_GRIP)


def test_shell_split_is_overlap_before_insert_split():
    assert p.INSERT_SPLIT_X - p.SHELL_SPLIT_X == pytest.approx(p.OVERLAP)


def test_key_short_leg_sits_just_past_the_tips():
    assert p.KEY_SHORT_X0 == pytest.approx(p.TIP_END_X + p.ITEM_CLEARANCE)
    assert p.KEY_SHORT_X1 - p.KEY_LONG_X0 == pytest.approx(p.KEY_LONG_LEG)


def test_shell_walls_hold_the_grooves():
    assert p.SHELL_TOP_WALL == pytest.approx(p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE + p.SHELL_FLOOR)
    assert p.SHELL_BOTTOM_WALL == pytest.approx(
        p.VELCRO_BOTTOM_LAYERS * p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE + p.SHELL_FLOOR)


def test_split_order():
    assert 0 < p.SHELL_SPLIT_X < p.INSERT_SPLIT_X < p.TIP_END_X < p.CASE_LENGTH
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_case_params.py -q`
Expected: FAIL — `AttributeError: module 'cad.params' has no attribute 'END_CAP_THICKNESS'`.

- [ ] **Step 3: Implement** — in `cad/params.py` insert after the module docstring (line 1):

```python

import math
```

and append at the end of the file:

```python

# =============================================================================
# Travel case — see docs/model.md (plain language) and
# docs/superpowers/specs/2026-10-04-travel-case-design.md (decisions).
# Coordinates: X along the case from half A's end face (x=0), Z up from the
# wide bottom face (z=0), Y across with y=0 the symmetry plane.
# =============================================================================

# --- Contents (simplified envelopes) ------------------------------------------

IRON_LENGTH = 159.0  # with tip, measured
IRON_HANDLE_LENGTH = 103.0  # spec sheet
IRON_WIDTH = 17.4  # measured, lies wide (Y)
IRON_HEIGHT = 14.4  # measured (Z)
IRON_METAL_DIAMETER = 5.0  # assumed; the thin part past the handle

TIP_LENGTH = 90.0  # measured
TIP_DIAMETER = 11.0  # widest, measured

KEY_LONG_LEG = 46.0  # measured
KEY_SHORT_LEG = 16.0  # measured
KEY_HEX = 1.46  # measured, across flats

# --- Insert (PETG) -------------------------------------------------------------

ITEM_CLEARANCE = 0.4  # item -> channel wall, radial
ITEM_END_CLEARANCE = 1.0  # item end -> cavity end
INSERT_WEB = 1.2  # min PETG between two channels
INSERT_WALL = 1.2  # min PETG between a channel and the insert surface
INSERT_END_WALL = 1.6  # insert end walls
INSERT_CORNER_RADIUS = 3.0  # rounded-trapezoid corners
TOP_EXTRA_WIDTH = 0.0  # widen the top flat (e.g. for more margin beside the groove)

TIP_GRIP = 11.0  # tips protrude this far past insert A's split face
KEY_LEG_ANGLE = -15.0  # short leg, degrees from horizontal (negative = down)
KEY_LEG_SIDE = 1  # +1 / -1: which side (Y) the short leg points to
POCKET_CLEARANCE = 1.0  # grip pocket in insert B around tip ends + short leg

# --- Shell (PLA) and fits ------------------------------------------------------

SHELL_SIDE_WALL = 1.6
SHELL_FLOOR = 1.2  # PLA left under a velcro groove
END_CAP_THICKNESS = 2.0  # the logo is cut through this
GLUE_CLEARANCE = 0.2  # insert -> its own shell half
SLIDE_CLEARANCE = 0.2  # insert A -> shell B, in the overlap
OVERLAP = 20.0  # insert A protrudes this far from shell A
# Axial gap left between insert A and insert B when the case is closed, so
# print/glue tolerance on the inserts can never stop the shells from closing.
INSERT_SPLIT_GAP = 0.5

# --- Velcro --------------------------------------------------------------------

VELCRO_WIDTH = 20.0  # to be confirmed with the real strip
VELCRO_THICKNESS = 2.0  # one layer, to be confirmed
VELCRO_CLEARANCE = 0.3  # added to the band channel's thickness and width
VELCRO_BOTTOM_LAYERS = 2  # the strip ends overlap on the bottom
BAND_BEND_RADIUS = 5.0  # inner radius of the band's bends

# --- Logo on the case, print limits --------------------------------------------

LOGO_BAND_MARGIN = 1.0  # logo -> start of the band bends / band edge
MAX_PRINT_HEIGHT = 180.0
PRINT_BED = 180.0

# --- Derived (computed — never type these) -------------------------------------

KEY_HEX_CORNERS = KEY_HEX / math.cos(math.radians(30))  # across corners

RING_END = VELCRO_THICKNESS + VELCRO_CLEARANCE  # band channel behind end caps
RING_TOP = VELCRO_THICKNESS + VELCRO_CLEARANCE
RING_BOTTOM = VELCRO_BOTTOM_LAYERS * VELCRO_THICKNESS + VELCRO_CLEARANCE

SHELL_TOP_WALL = RING_TOP + SHELL_FLOOR
SHELL_BOTTOM_WALL = RING_BOTTOM + SHELL_FLOOR

CAVITY_LENGTH = IRON_LENGTH + 2 * ITEM_END_CLEARANCE
CAVITY_START_X = END_CAP_THICKNESS + RING_END + INSERT_END_WALL
CAVITY_END_X = CAVITY_START_X + CAVITY_LENGTH
CASE_LENGTH = CAVITY_END_X + INSERT_END_WALL + RING_END + END_CAP_THICKNESS

ITEM_START_X = CAVITY_START_X + ITEM_END_CLEARANCE  # iron and all tips start here
TIP_END_X = ITEM_START_X + TIP_LENGTH
INSERT_SPLIT_X = TIP_END_X - TIP_GRIP
SHELL_SPLIT_X = INSERT_SPLIT_X - OVERLAP

KEY_SHORT_X0 = TIP_END_X + ITEM_CLEARANCE  # short leg, side facing half A
KEY_SHORT_X1 = KEY_SHORT_X0 + KEY_HEX
KEY_LONG_X0 = KEY_SHORT_X1 - KEY_LONG_LEG  # long leg runs back into insert A

# --- Modelling resolution -------------------------------------------------------

# Line segments per quarter circle for every round 2D shape. 16 -> a 64-gon:
# max deviation r * (1 - cos(pi/64)) ≈ 0.007 mm at r = 5.5. Higher = slower.
ARC_QUAD_SEGMENTS = 16
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_case_params.py -q` → 6 passed. Then `make test` → all green.

- [ ] **Step 5: Commit**

```bash
git add cad/params.py tests/test_case_params.py
git commit -m "Case parameters: contents, insert, shell, velcro, derived lengths

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Contents layout

**Files:**
- Create: `cad/contents.py`
- Test: `tests/test_contents.py`

**Interfaces:**
- Consumes: `cad.params` (Task 1).
- Produces: `FLOOR_Z: float`, `ITEM_GAP: float`, `Item(name, section, x0, x1)` (frozen dataclass; `section` is a shapely YZ geometry, shapely x = case Y, shapely y = case Z), `layout() -> dict[str, Item]` with keys `iron, tip_bl, tip_br, tip_tl, tip_tr, key`; `key_axis() -> (y, z)`; `key_short_leg_line() -> LineString`; `key_short_leg_section(grow=0.0) -> shapely geometry`; `contents_solids() -> dict[str, Part]` (same keys as `layout()`).

- [ ] **Step 1: Write the failing test** — create `tests/test_contents.py`:

```python
"""Item layout in the cross-section (spec criterion 3, 2D part)."""

import itertools

import pytest

from cad import params as p
from cad.contents import ITEM_GAP, key_short_leg_section, layout


def test_layout_has_all_items():
    assert set(layout()) == {"iron", "tip_bl", "tip_br", "tip_tl", "tip_tr", "key"}


def test_items_keep_a_web_between_channels():
    sections = {k: v.section for k, v in layout().items()}
    for (a, ga), (b, gb) in itertools.combinations(sections.items(), 2):
        assert ga.distance(gb) >= ITEM_GAP - 1e-3, (a, b)


def test_layout_is_symmetric():
    items = layout()
    for left, right in (("tip_bl", "tip_br"), ("tip_tl", "tip_tr")):
        l, r = items[left].section.centroid, items[right].section.centroid
        assert l.x == pytest.approx(-r.x, abs=1e-6)
        assert l.y == pytest.approx(r.y, abs=1e-6)
    assert items["iron"].section.centroid.x == pytest.approx(0, abs=1e-6)
    assert items["key"].section.centroid.x == pytest.approx(0, abs=1e-6)


def test_short_leg_clears_the_iron():
    leg = key_short_leg_section(0)
    assert leg.distance(layout()["iron"].section) >= 2 * p.ITEM_CLEARANCE
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_contents.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cad.contents'`.

- [ ] **Step 3: Implement** — create `cad/contents.py`:

```python
"""What goes in the case: simplified envelopes, placed in case coordinates.

Cross-section layout B (looking along X; Y across, Z up):

    bottom row:  tip  iron  tip      (bottoms level, on the insert floor)
    top row:     tip  key   tip      (top tips dropped onto the bottom row)

Along X every item starts at ``ITEM_START_X``. The L-shaped hex key's short leg
sits just past the tip ends, angled ``KEY_LEG_ANGLE`` down to ``KEY_LEG_SIDE``.

2D shapes are shapely geometry in the YZ plane (x = Y, y = Z).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache

from build123d import Box, Cylinder, Ellipse, Location, Part, Plane, Rot, extrude
from shapely import affinity
from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry

from cad import params as p

# Z of the bottom row's underside: shell bottom wall, glue gap, insert wall,
# channel clearance.
FLOOR_Z = p.SHELL_BOTTOM_WALL + p.GLUE_CLEARANCE + p.INSERT_WALL + p.ITEM_CLEARANCE
# Centre-to-centre gap between two neighbouring channels' items.
ITEM_GAP = 2 * p.ITEM_CLEARANCE + p.INSERT_WEB
DROP_TOLERANCE = 0.001  # mm, bisection tolerance when dropping items


@dataclass(frozen=True)
class Item:
    name: str
    section: BaseGeometry  # YZ cross-section of the item itself (no clearance)
    x0: float
    x1: float


def _ellipse(y: float, z: float, w: float, h: float) -> BaseGeometry:
    return affinity.scale(Point(y, z).buffer(1, p.ARC_QUAD_SEGMENTS), w / 2, h / 2)


def _circle(y: float, z: float, d: float) -> BaseGeometry:
    return Point(y, z).buffer(d / 2, p.ARC_QUAD_SEGMENTS)


def _drop(shape_at, placed: list[BaseGeometry]) -> BaseGeometry:
    """Lower ``shape_at(z)`` onto ``placed`` until it is ITEM_GAP away.

    Bisection between a height where it clearly clears everything and the
    floor, where it overlaps the bottom row.
    """
    def clear(z: float) -> bool:
        return min(shape_at(z).distance(o) for o in placed) >= ITEM_GAP

    lo = FLOOR_Z
    hi = FLOOR_Z + 4 * (p.IRON_HEIGHT + p.TIP_DIAMETER)
    while hi - lo > DROP_TOLERANCE:
        mid = (lo + hi) / 2
        if clear(mid):
            hi = mid
        else:
            lo = mid
    return shape_at(hi)


@cache
def layout() -> dict[str, Item]:
    """All items, keyed by name: iron, tip_bl, tip_br, tip_tl, tip_tr, key."""
    iron = _ellipse(0, FLOOR_Z + p.IRON_HEIGHT / 2, p.IRON_WIDTH, p.IRON_HEIGHT)
    side_y = p.IRON_WIDTH / 2 + ITEM_GAP + p.TIP_DIAMETER / 2
    tip_z = FLOOR_Z + p.TIP_DIAMETER / 2
    tip_bl = _circle(-side_y, tip_z, p.TIP_DIAMETER)
    tip_br = _circle(side_y, tip_z, p.TIP_DIAMETER)
    # Top tips leave room for the key to drop between them.
    top_y = p.KEY_HEX_CORNERS / 2 + ITEM_GAP + p.TIP_DIAMETER / 2 + 2 * DROP_TOLERANCE
    placed = [iron, tip_bl, tip_br]
    tip_tl = _drop(lambda z: _circle(-top_y, z, p.TIP_DIAMETER), placed)
    tip_tr = _drop(lambda z: _circle(top_y, z, p.TIP_DIAMETER), placed)
    key = _drop(lambda z: _circle(0, z, p.KEY_HEX_CORNERS), placed + [tip_tl, tip_tr])

    tips = (p.ITEM_START_X, p.TIP_END_X)
    return {
        "iron": Item("iron", iron, p.ITEM_START_X, p.ITEM_START_X + p.IRON_LENGTH),
        "tip_bl": Item("tip_bl", tip_bl, *tips),
        "tip_br": Item("tip_br", tip_br, *tips),
        "tip_tl": Item("tip_tl", tip_tl, *tips),
        "tip_tr": Item("tip_tr", tip_tr, *tips),
        "key": Item("key", key, p.KEY_LONG_X0, p.KEY_SHORT_X1),
    }


def key_axis() -> tuple[float, float]:
    """(y, z) of the key's long leg axis."""
    c = layout()["key"].section.centroid
    return c.x, c.y


def key_short_leg_line() -> LineString:
    """Centreline of the short leg in YZ, from the long-leg axis outward."""
    y, z = key_axis()
    a = math.radians(p.KEY_LEG_ANGLE)
    length = p.KEY_SHORT_LEG - p.KEY_HEX_CORNERS / 2
    return LineString([(y, z), (y + p.KEY_LEG_SIDE * length * math.cos(a),
                                z + length * math.sin(a))])


def key_short_leg_section(grow: float = 0.0) -> BaseGeometry:
    """YZ footprint of the short leg (+ ``grow``)."""
    return key_short_leg_line().buffer(p.KEY_HEX_CORNERS / 2 + grow, p.ARC_QUAD_SEGMENTS)


# --- 3D envelopes (for the viewer and interference tests) ----------------------


def _along_x(y: float, z: float, x0: float, x1: float, solid_xy) -> Part:
    """Place a solid built on the XY plane (extruded +Z) along X at (y, z)."""
    plane = Plane(origin=(x0, y, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return plane * solid_xy(x1 - x0)


def iron_solid() -> Part:
    item = layout()["iron"]
    c = item.section.centroid
    handle = _along_x(c.x, c.y, item.x0, item.x0 + p.IRON_HANDLE_LENGTH,
                      lambda L: extrude(Ellipse(p.IRON_WIDTH / 2, p.IRON_HEIGHT / 2), L))
    metal = _along_x(c.x, c.y, item.x0 + p.IRON_HANDLE_LENGTH, item.x1,
                     lambda L: Location((0, 0, L / 2)) * Cylinder(p.IRON_METAL_DIAMETER / 2, L))
    return handle + metal


def tip_solid(name: str) -> Part:
    item = layout()[name]
    c = item.section.centroid
    return _along_x(c.x, c.y, item.x0, item.x1,
                    lambda L: Location((0, 0, L / 2)) * Cylinder(p.TIP_DIAMETER / 2, L))


def key_solid() -> Part:
    item = layout()["key"]
    y, z = key_axis()
    long_leg = _along_x(y, z, item.x0, item.x1,
                        lambda L: Location((0, 0, L / 2)) * Cylinder(p.KEY_HEX_CORNERS / 2, L))
    (y0, z0), (y1, z1) = key_short_leg_line().coords
    length = math.hypot(y1 - y0, z1 - z0)
    short = Location((p.KEY_SHORT_X0 + p.KEY_HEX / 2, y0, z0)) * (
        Rot(math.degrees(math.atan2(z1 - z0, y1 - y0)), 0, 0)
        * Location((0, length / 2, 0))
        * Box(p.KEY_HEX, length, p.KEY_HEX)
    )
    return long_leg + short


def contents_solids() -> dict[str, Part]:
    out = {"iron": iron_solid(), "key": key_solid()}
    for name in ("tip_bl", "tip_br", "tip_tl", "tip_tr"):
        out[name] = tip_solid(name)
    return out
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_contents.py -q` → 4 passed (layout takes ~2 s). Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add cad/contents.py tests/test_contents.py
git commit -m "Contents: layout B, L-key short leg, item envelopes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Insert and shell profiles

**Files:**
- Create: `cad/profile.py`
- Test: `tests/test_profile.py`

**Interfaces:**
- Consumes: `layout()`, `key_short_leg_section()` (Task 2).
- Produces: `rounded_trapezoid(bottom_hw, top_hw, z0, z1, radius)`, `channel_sections() -> dict[str, geom]`, `insert_trapezoid() -> (bottom_hw, top_hw, z0, z1)`, `insert_profile()`, `shell_profile()`, `insert_cavity(clearance)`, `case_height() -> float`. All YZ shapely geometry.

- [ ] **Step 1: Write the failing test** — create `tests/test_profile.py`:

```python
"""Insert and shell profiles."""

import pytest

from cad import params as p
from cad.contents import key_short_leg_section
from cad.profile import channel_sections, insert_profile, shell_profile


def test_channels_keep_insert_wall_to_the_surface():
    inner = insert_profile().buffer(-p.INSERT_WALL + 1e-3)
    for name, ch in channel_sections().items():
        assert ch.difference(inner).area < 1e-6, name


def test_short_leg_fits_inside_the_insert():
    leg = key_short_leg_section(p.ITEM_CLEARANCE)
    assert leg.difference(insert_profile().buffer(-p.INSERT_WALL + 1e-3)).area < 1e-6


def test_profiles_are_symmetric_and_shell_starts_at_z0():
    for prof in (insert_profile(), shell_profile()):
        minx, _, maxx, _ = prof.bounds
        assert minx == pytest.approx(-maxx, abs=1e-6)
    assert shell_profile().bounds[1] == pytest.approx(0, abs=1e-9)


def test_shell_contains_insert_with_side_wall():
    gap = shell_profile().exterior.distance(insert_profile())
    assert gap >= p.GLUE_CLEARANCE + p.SHELL_SIDE_WALL - 0.01


def test_bottom_is_wider_than_top():
    prof = shell_profile()
    _, z0, _, z1 = prof.bounds
    from shapely.geometry import LineString
    width = lambda z: prof.intersection(LineString([(-999, z), (999, z)])).length  # noqa: E731
    assert width(z0 + (z1 - z0) * 0.25) > width(z0 + (z1 - z0) * 0.75)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_profile.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cad.profile'`.

- [ ] **Step 3: Implement** — create `cad/profile.py`:

```python
"""2D cross-sections (YZ plane, shapely): channels, insert and shell profiles.

Insert: the smallest symmetric rounded trapezoid that keeps INSERT_WALL around
every channel. Shell: the same trapezoid grown by GLUE_CLEARANCE +
SHELL_SIDE_WALL at the sides and out to the top/bottom wall thickness, with z=0
at its bottom face.
"""

from __future__ import annotations

import math
from functools import cache

from shapely.geometry import Polygon
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


@cache
def insert_trapezoid() -> tuple[float, float, float, float]:
    """(bottom_hw, top_hw, z0, z1) of the insert's core trapezoid."""
    # The trapezoid is convex, so fitting the convex hull is exact and far cheaper.
    need = (unary_union(list(channel_sections().values()))
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
    return bottom_hw, top_hw + p.TOP_EXTRA_WIDTH / 2, z0, z1


def insert_profile() -> BaseGeometry:
    b, t, z0, z1 = insert_trapezoid()
    return rounded_trapezoid(b, t, z0, z1, p.INSERT_CORNER_RADIUS)


def _grown_trapezoid(side: float, bottom: float, top: float):
    """Insert trapezoid with its sides moved out by ``side`` (perpendicular)
    and its bottom/top faces moved out by ``bottom``/``top``."""
    b, t, z0, z1 = insert_trapezoid()
    slope = (b - t) / (z1 - z0)  # half-width lost per mm of height
    shift = side * math.hypot(1, slope)  # horizontal shift of a slanted side
    nz0, nz1 = z0 - bottom, z1 + top
    nb = b + shift + slope * bottom
    nt = t + shift - slope * top
    return nb, nt, nz0, nz1


def shell_profile() -> BaseGeometry:
    """Outer contour of the shell (z=0 at the bottom face)."""
    side = p.GLUE_CLEARANCE + p.SHELL_SIDE_WALL
    nb, nt, nz0, nz1 = _grown_trapezoid(
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_profile.py -q` → 5 passed. Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add cad/profile.py tests/test_profile.py
git commit -m "Profiles: fitted rounded-trapezoid insert, shell with groove walls

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Band ring

**Files:**
- Create: `cad/solids.py`, `cad/band.py`
- Test: `tests/test_band.py`

**Interfaces:**
- Consumes: `case_height()` (Task 3).
- Produces: `solids.extrude_x(section_yz, x0, x1) -> Part`, `solids.extrude_y(section_xz, half_width) -> Part`, `solids.below_x(x) -> Part`; `band.BAND_HALF_WIDTH`, `outer_block()`, `inner_block()`, `ring_section()` (XZ shapely), `straight_run_z() -> (z_lo, z_hi)`, `ring_solid() -> Part`, `band_solid() -> Part`.

- [ ] **Step 1: Write the failing test** — create `tests/test_band.py`:

```python
"""Band ring: continuous channel (criterion 10), floors under grooves (4)."""

import pytest

from cad import params as p
from cad.band import inner_block, ring_section, straight_run_z
from cad.profile import case_height, insert_profile

# Round items are polygons, so the insert's bottom sits a hair off.
FLOOR_TOLERANCE = 0.01


def test_ring_is_one_closed_loop():
    ring = ring_section()
    assert ring.geom_type == "Polygon"
    assert len(ring.interiors) == 1


def test_ring_is_thick_enough_everywhere_to_thread_the_band():
    """Shrinking by just under half the thinnest run must keep a closed loop."""
    thinnest = min(p.RING_END, p.RING_TOP, p.RING_BOTTOM)
    assert thinnest >= p.VELCRO_THICKNESS + p.VELCRO_CLEARANCE - 1e-9
    core = ring_section().buffer(-(thinnest / 2 - 0.01))
    assert core.geom_type == "Polygon" and len(core.interiors) == 1


def test_shell_floor_under_both_grooves():
    _, insert_bottom, _, insert_top = insert_profile().bounds
    _, inner_bottom, _, inner_top = inner_block().bounds
    assert inner_top - (insert_top + p.GLUE_CLEARANCE) == pytest.approx(p.SHELL_FLOOR, abs=FLOOR_TOLERANCE)
    assert (insert_bottom - p.GLUE_CLEARANCE) - inner_bottom == pytest.approx(p.SHELL_FLOOR, abs=FLOOR_TOLERANCE)


def test_top_groove_is_flush():
    assert ring_section().bounds[3] == pytest.approx(case_height())


def test_straight_run_is_inside_the_case():
    lo, hi = straight_run_z()
    assert 0 < lo < hi < case_height()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_band.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cad.band'`.

- [ ] **Step 3: Implement** — create `cad/solids.py`:

```python
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
```

and `cad/band.py`:

```python
"""The velcro band channel ("band ring").

In side view (XZ) the band follows the gap between two almost-concentric
rounded blocks: the outer block is the case without its end caps; the inner
block is one band layer smaller at the top and the ends and
VELCRO_BOTTOM_LAYERS layers smaller at the bottom. Outer minus inner is the
ring; extruded across the band width it is subtracted from shell and insert.
That one cut makes the flush top groove, the deeper bottom groove, the bends
and the channel behind the end caps.
"""

from __future__ import annotations

from functools import cache

from build123d import Part
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

from cad import params as p
from cad.profile import case_height
from cad.solids import extrude_y

BAND_HALF_WIDTH = p.VELCRO_WIDTH / 2 + p.VELCRO_CLEARANCE


def _rounded_box(x0: float, z0: float, x1: float, z1: float, r: float) -> BaseGeometry:
    return box(x0, z0, x1, z1).buffer(-r, join_style="mitre").buffer(r, p.ARC_QUAD_SEGMENTS)


def outer_block() -> BaseGeometry:
    return _rounded_box(p.END_CAP_THICKNESS, 0.0,
                        p.CASE_LENGTH - p.END_CAP_THICKNESS, case_height(),
                        p.BAND_BEND_RADIUS + p.RING_END)


def inner_block() -> BaseGeometry:
    return _rounded_box(p.END_CAP_THICKNESS + p.RING_END, p.RING_BOTTOM,
                        p.CASE_LENGTH - p.END_CAP_THICKNESS - p.RING_END,
                        case_height() - p.RING_TOP,
                        p.BAND_BEND_RADIUS)


def ring_section() -> BaseGeometry:
    """The band channel in side view (XZ plane: x = X, y = Z)."""
    return outer_block().difference(inner_block())


def straight_run_z() -> tuple[float, float]:
    """Z range of the straight vertical part of the band behind the end caps."""
    return (p.RING_BOTTOM + p.BAND_BEND_RADIUS,
            case_height() - p.RING_TOP - p.BAND_BEND_RADIUS)


@cache
def ring_solid() -> Part:
    """The band channel as a solid, to subtract from shell and insert."""
    return extrude_y(ring_section(), BAND_HALF_WIDTH)


@cache
def band_solid() -> Part:
    """The velcro itself (no clearance), for the viewer."""
    half = p.VELCRO_WIDTH / 2
    c = p.VELCRO_CLEARANCE / 2
    section = (_rounded_box(p.END_CAP_THICKNESS + c, c,
                            p.CASE_LENGTH - p.END_CAP_THICKNESS - c, case_height(),
                            p.BAND_BEND_RADIUS + p.RING_END - c)
               .difference(inner_block().buffer(c, p.ARC_QUAD_SEGMENTS)))
    return extrude_y(section, half)
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_band.py -q` → 5 passed. Quick 3D sanity check:

```bash
uv run python -c "from cad.band import *; r = ring_solid(); print(r.is_valid, round(r.volume), round(ring_section().area * 2 * BAND_HALF_WIDTH))"
```

Expected: `True` and two equal volumes (~25417). Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add cad/solids.py cad/band.py tests/test_band.py
git commit -m "Band ring: almost-concentric rounded blocks, extruded across the band

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Insert

**Files:**
- Create: `cad/insert.py`
- Test: `tests/test_insert.py`

**Interfaces:**
- Consumes: `ring_solid()` (Task 4), `channel_sections()`, `insert_profile()` (Task 3), `key_short_leg_section()` (Task 2), `extrude_x`, `below_x` (Task 4).
- Produces: `pocket_section()` (YZ shapely), `insert_solid()`, `insert_a()` (ends `INSERT_SPLIT_GAP` before `INSERT_SPLIT_X`), `insert_b()` (starts at `INSERT_SPLIT_X`) — cached `Part`s.

- [ ] **Step 1: Write the failing test** — create `tests/test_insert.py`:

```python
"""Insert (criteria 1, 2, 3, 8, 11). Slow-ish: builds the insert once."""

import pytest

from cad import params as p
from cad.contents import contents_solids, key_short_leg_section
from cad.insert import insert_a, insert_b, pocket_section

VOLUME_TOLERANCE = 1e-3  # mm³: "no overlap"
INSERTS = {"insert A": insert_a, "insert B": insert_b}


@pytest.mark.parametrize("name", INSERTS)
def test_insert_is_one_valid_solid(name):
    part = INSERTS[name]()
    assert part.is_valid
    assert len(part.solids()) == 1


@pytest.mark.parametrize("name", INSERTS)
def test_insert_fits_the_printer_standing_up(name):
    size = INSERTS[name]().bounding_box().size
    assert size.X <= p.MAX_PRINT_HEIGHT
    assert max(size.Y, size.Z) <= p.PRINT_BED


def test_inserts_do_not_overlap():
    assert (insert_a() & insert_b()).volume < VOLUME_TOLERANCE


@pytest.mark.parametrize("item", ["iron", "tip_bl", "tip_br", "tip_tl", "tip_tr", "key"])
def test_contents_do_not_hit_the_inserts(item):
    solid = contents_solids()[item]
    for name, part in INSERTS.items():
        assert (solid & part()).volume < VOLUME_TOLERANCE, name


def test_key_short_leg_is_free_when_opened():
    leg = key_short_leg_section(0)
    assert leg.difference(pocket_section()).area < 1e-6
    # entirely past insert A's face (and so past shell A too)
    assert p.KEY_SHORT_X0 > p.INSERT_SPLIT_X > p.SHELL_SPLIT_X


def test_inserts_leave_a_gap_so_the_shells_close_first():
    gap = insert_b().bounding_box().min.X - insert_a().bounding_box().max.X
    assert gap == pytest.approx(p.INSERT_SPLIT_GAP)
    assert insert_b().bounding_box().min.X == pytest.approx(p.INSERT_SPLIT_X)


def test_inserts_rest_on_the_end_caps():
    assert insert_a().bounding_box().min.X == pytest.approx(p.END_CAP_THICKNESS)
    assert insert_b().bounding_box().max.X == pytest.approx(p.CASE_LENGTH - p.END_CAP_THICKNESS)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_insert.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cad.insert'`.

- [ ] **Step 3: Implement** — create `cad/insert.py`:

```python
"""The PETG insert: solid trapezoid with a channel per item, split in A and B.

Outside the band width it runs up to the end caps (the glue end stop); in the
band width the band ring is cut away. Insert A stops INSERT_SPLIT_GAP short of
insert B so the shells always meet first, whatever the glue tolerance. Insert B's face has an open grip pocket
that takes the protruding tip ends and the key's short leg.
"""

from __future__ import annotations

from functools import cache

from build123d import Part
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.band import ring_solid
from cad.contents import key_short_leg_section
from cad.profile import channel_sections, insert_profile
from cad.solids import below_x, extrude_x

TIP_NAMES = ("tip_bl", "tip_br", "tip_tl", "tip_tr")


def pocket_section() -> BaseGeometry:
    """YZ footprint of the grip pocket: top tips, key and short leg, hulled,
    grown by POCKET_CLEARANCE, kept INSERT_WALL inside the insert surface."""
    ch = channel_sections()
    parts = [ch["tip_tl"], ch["tip_tr"], ch["key"],
             key_short_leg_section(p.ITEM_CLEARANCE)]
    hull = unary_union(parts).convex_hull.buffer(p.POCKET_CLEARANCE, p.ARC_QUAD_SEGMENTS)
    return hull.intersection(insert_profile().buffer(-p.INSERT_WALL, p.ARC_QUAD_SEGMENTS))


@cache
def insert_solid() -> Part:
    """The whole insert, before splitting."""
    ch = channel_sections()
    body = extrude_x(insert_profile(), p.END_CAP_THICKNESS,
                     p.CASE_LENGTH - p.END_CAP_THICKNESS)
    body -= ring_solid()
    body -= extrude_x(ch["iron"], p.CAVITY_START_X, p.CAVITY_END_X)
    for name in TIP_NAMES:
        body -= extrude_x(ch[name], p.CAVITY_START_X, p.TIP_END_X + p.ITEM_END_CLEARANCE)
    body -= extrude_x(ch["key"], p.KEY_LONG_X0 - p.ITEM_END_CLEARANCE, p.KEY_SHORT_X1)
    body -= extrude_x(pocket_section(), p.INSERT_SPLIT_X,
                      p.KEY_SHORT_X1 + p.POCKET_CLEARANCE)
    return body


@cache
def insert_a() -> Part:
    """Insert A stops INSERT_SPLIT_GAP short of insert B, so the shells
    always close first."""
    return insert_solid() & below_x(p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP)


@cache
def insert_b() -> Part:
    return insert_solid() - below_x(p.INSERT_SPLIT_X)
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_insert.py -q` → 14 passed (~5 s). Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add cad/insert.py tests/test_insert.py
git commit -m "Insert: channels, key hole, grip pocket, end stop, split A/B

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Shell with logo

**Files:**
- Create: `cad/shell.py`
- Test: `tests/test_shell.py`

**Interfaces:**
- Consumes: `logo_cutter(depth)` from `cad.build` (existing), `ring_solid()`, `straight_run_z()` (Task 4), `insert_cavity()`, `shell_profile()` (Task 3), `extrude_x`, `below_x`.
- Produces: `LOGO_CUT_OVERRUN`, `logo_z() -> float`, `logo_plane() -> Plane`, `shell_solid()`, `shell_a()`, `shell_b()` (cached `Part`s).

- [ ] **Step 1: Write the failing test** — create `tests/test_shell.py`:

```python
"""Shell and logo (criteria 1, 2, 5, 6, 7). Builds shell and insert once."""

import pytest
from build123d import Plane, Vector

from cad import params as p
from cad.band import BAND_HALF_WIDTH, straight_run_z
from cad.contents import contents_solids
from cad.insert import insert_a, insert_b
from cad.pinecil_logo import holes_mm, outline_mm
from cad.shell import logo_plane, logo_z, shell_a, shell_b

VOLUME_TOLERANCE = 1e-3  # mm³: "no overlap"
SHELLS = {"shell A": shell_a, "shell B": shell_b}
PARTS = {**SHELLS, "insert A": insert_a, "insert B": insert_b}


@pytest.mark.parametrize("name", SHELLS)
def test_shell_is_one_valid_solid(name):
    part = SHELLS[name]()
    assert part.is_valid
    assert len(part.solids()) == 1


@pytest.mark.parametrize("name", SHELLS)
def test_shell_fits_the_printer_standing_up(name):
    size = SHELLS[name]().bounding_box().size
    assert size.X <= p.MAX_PRINT_HEIGHT
    assert max(size.Y, size.Z) <= p.PRINT_BED


@pytest.mark.parametrize("a, b", [("shell A", "insert A"), ("shell B", "insert B"),
                                  ("shell B", "insert A"), ("shell A", "insert B"),
                                  ("shell A", "shell B")])
def test_assembled_parts_do_not_overlap(a, b):
    assert (PARTS[a]() & PARTS[b]()).volume < VOLUME_TOLERANCE


@pytest.mark.parametrize("item", ["iron", "tip_bl", "tip_br", "tip_tl", "tip_tr", "key"])
def test_contents_do_not_hit_the_shell(item):
    solid = contents_solids()[item]
    for name, part in SHELLS.items():
        assert (solid & part()).volume < VOLUME_TOLERANCE, name


def test_logo_sits_on_the_straight_band_run():
    minx, miny, maxx, maxy = outline_mm().bounds
    lo, hi = straight_run_z()
    assert logo_z() + miny >= lo + p.LOGO_BAND_MARGIN
    assert logo_z() + maxy <= hi - p.LOGO_BAND_MARGIN
    assert max(-minx, maxx) <= BAND_HALF_WIDTH - p.LOGO_BAND_MARGIN


def test_logo_is_upright():
    """Logo +Y (towards the top piece P1) maps to case +Z."""
    assert logo_plane().y_dir == Vector(0, 0, 1)
    top_piece = max(holes_mm(), key=lambda h: h.centroid.y)
    assert top_piece.centroid.y > 0


def test_logo_cuts_through_shell_b_end_cap():
    def cap_area(part, x):
        return sum(f.area for f in part.intersect(Plane.YZ.offset(x)))

    plain = cap_area(shell_a(), p.END_CAP_THICKNESS / 2)
    with_logo = cap_area(shell_b(), p.CASE_LENGTH - p.END_CAP_THICKNESS / 2)
    assert plain - with_logo == pytest.approx(sum(h.area for h in holes_mm()), rel=1e-3)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_shell.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cad.shell'`.

- [ ] **Step 3: Implement** — create `cad/shell.py`:

```python
"""The PLA shell: rounded-trapezoid tube with end caps, split in A and B.

The insert cavity has GLUE_CLEARANCE, and SLIDE_CLEARANCE in the overlap zone
of shell B where insert A slides in. The band ring cuts the grooves and the
channel behind the end caps. Shell B's end cap carries the logo, upright
(logo top -> +Z) and centred on the band's straight vertical run.
"""

from __future__ import annotations

from functools import cache

from build123d import Part, Plane

from cad import params as p
from cad.band import ring_solid, straight_run_z
from cad.build import logo_cutter
from cad.profile import insert_cavity, shell_profile
from cad.solids import below_x, extrude_x

# The logo cutter starts this far inside the band channel and pokes the same
# distance out of the end face, so it cuts cleanly through the end cap.
LOGO_CUT_OVERRUN = p.RING_END / 2


def logo_z() -> float:
    lo, hi = straight_run_z()
    return (lo + hi) / 2


def logo_plane() -> Plane:
    """Logo sketch plane on shell B's end cap: logo +Y -> case +Z, logo
    extrusion -> case +X (outward). Seen from outside the logo is upright."""
    x = p.CASE_LENGTH - p.END_CAP_THICKNESS - LOGO_CUT_OVERRUN
    return Plane(origin=(x, 0, logo_z()), x_dir=(0, 1, 0), z_dir=(1, 0, 0))


@cache
def shell_solid() -> Part:
    body = extrude_x(shell_profile(), 0.0, p.CASE_LENGTH)
    body -= extrude_x(insert_cavity(p.GLUE_CLEARANCE), p.END_CAP_THICKNESS,
                      p.CASE_LENGTH - p.END_CAP_THICKNESS)
    body -= extrude_x(insert_cavity(p.SLIDE_CLEARANCE), p.SHELL_SPLIT_X, p.INSERT_SPLIT_X)
    body -= ring_solid()
    return body


@cache
def shell_a() -> Part:
    return shell_solid() & below_x(p.SHELL_SPLIT_X)


@cache
def shell_b() -> Part:
    cutter = logo_plane() * logo_cutter(p.END_CAP_THICKNESS + 2 * LOGO_CUT_OVERRUN)
    return shell_solid() - below_x(p.SHELL_SPLIT_X) - cutter
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_shell.py -q` → 18 passed (~8 s). Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add cad/shell.py tests/test_shell.py
git commit -m "Shell: groove walls, overlap slide fit, logo through cap B, split A/B

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Export and section renders

**Files:**
- Modify: `cad/build.py` (docstring; replace `main()`; add `case_parts()`)
- Create: `cad/sections.py`
- Modify: `Makefile`
- Test: `tests/test_outputs.py` (first two tests; the viewer tests are added in Task 8)

**Interfaces:**
- Consumes: `shell_a/b` (Task 6), `insert_a/b` (Task 5), `band_solid` (Task 4), `contents_solids` (Task 2).
- Produces: `cad.build.case_parts() -> dict[str, Part]` (keys `shell-a, shell-b, insert-a, insert-b`); `cad.sections.render() -> Path` (writes `build/sections.svg`, plus `.png` when inkscape exists); make targets `build`, `sections`.

- [ ] **Step 1: Write the failing test** — create `tests/test_outputs.py`:

```python
"""Smoke tests for the generated outputs: exports, section render, viewer."""

from cad import params as p
from cad.build import case_parts
from cad.sections import render


def test_case_parts_are_the_four_printables():
    assert set(case_parts()) == {"shell-a", "shell-b", "insert-a", "insert-b"}


def test_sections_render_draws_every_part():
    svg = render().read_text()
    for colour in ("#222222", "#444444", "#e91e63", "#f06292", "#1e88e5", "#2e7d32"):
        assert colour in svg
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_outputs.py -q`
Expected: FAIL — `ImportError: cannot import name 'case_parts' from 'cad.build'`.

- [ ] **Step 3: Implement**

In `cad/build.py` replace the module docstring with:

```python
"""build123d geometry: the Pinecil logo as a cutter, a test plate, and the
export of every printable part.

    uv run python -m cad.build   ->  build/<part>.step + build/<part>.stl
                                     for logo-plate, shell-a, shell-b,
                                     insert-a, insert-b

``logo_cutter`` is the reusable part: shell B subtracts it from its end cap.
The test plate exists to print-check rib width.
"""
```

and replace everything from `def main() -> None:` to the end of the file with:

```python
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
```

Create `cad/sections.py`:

```python
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
from cad.contents import contents_solids
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
    cross = [
        (p.ITEM_START_X + p.TIP_LENGTH / 3, "in helft A"),
        ((p.SHELL_SPLIT_X + p.INSERT_SPLIT_X) / 2, "overlap"),
        ((p.KEY_SHORT_X0 + p.KEY_SHORT_X1) / 2, "kuiltje + haakse poot"),
        (p.CASE_LENGTH - p.END_CAP_THICKNESS / 2, "kopse kant B (logo)"),
    ]
    panels, x_cursor, top, bottom = [], 0.0, 0.0, 0.0
    for x, title in cross:
        body, (x0, y0, x1, y1) = _panel(all_parts, Plane.YZ.offset(x), yz,
                                        f"x = {x:.1f} — {title}")
        panels.append(f'<g transform="translate({x_cursor - x0:.2f},0)">{body}</g>')
        x_cursor += (x1 - x0) + GAP
        top, bottom = min(top, y0), max(bottom, y1)
    long_body, (lx0, ly0, lx1, ly1) = _panel(
        all_parts, Plane.XZ, lambda v: (v.X, v.Z), "lengtedoorsnede y = 0 (dicht)")
    long_dy = bottom - ly0 + GAP
    panels.append(f'<g transform="translate({-lx0:.2f},{long_dy:.2f})">{long_body}</g>')
    width = max(x_cursor, lx1 - lx0) + GAP
    height = (long_dy + ly1) - top + GAP
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * PX_PER_MM:.0f}" '
           f'height="{height * PX_PER_MM:.0f}" viewBox="{-GAP / 2} {top - GAP / 2} {width} {height}" '
           f'font-family="sans-serif"><rect x="{-GAP / 2}" y="{top - GAP / 2}" '
           f'width="{width}" height="{height}" fill="white"/>' + "".join(panels) + "</svg>")
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "sections.svg"
    out.write_text(svg)
    if inkscape := shutil.which("inkscape"):
        subprocess.run([inkscape, str(out), "-o", str(out.with_suffix(".png"))],
                       check=True, capture_output=True)
    return out


if __name__ == "__main__":
    print(render())
```

In `Makefile` change the `.PHONY` line and add two targets after `render`:

```make
.PHONY: test build render sections viewer clean
```

```make
sections:
	uv run python -m cad.sections
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_outputs.py -q` → 2 passed. Then:

```bash
make build      # prints 5 parts: logo-plate, shell-a 65.9, shell-b 106.9, insert-a 83.4, insert-b 84.9 long
make sections   # build/sections.svg + .png
```

Open `build/sections.png` and check by eye: four cross-sections (in half A, overlap, pocket + short leg, end cap B with an upright logo) and the long section with the band ring. Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add cad/build.py cad/sections.py Makefile tests/test_outputs.py
git commit -m "Export all case parts; section renders from the 3D model

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: 3D viewer

**Files:**
- Create: `docs/viewer/travel-case-viewer.html` (template), `cad/viewer.py`
- Modify: `Makefile`, `tests/test_outputs.py`

**Interfaces:**
- Consumes: everything from Tasks 2–6.
- Produces: `cad.viewer.TEMPLATE`, `cad.viewer.specs() -> dict[str, str]`, `cad.viewer.main()` (writes `build/travel-case-viewer.html`); make target `viewer`.

- [ ] **Step 1: Write the failing test** — append to `tests/test_outputs.py` (and add `from cad.viewer import TEMPLATE, specs` to its imports):

```python
def test_viewer_template_has_both_tokens():
    html = TEMPLATE.read_text()
    assert '"__GEOM__"' in html and '"__SPECS__"' in html


def test_viewer_specs_come_from_the_model():
    s = specs()
    assert s["Overlap"] == f"{p.OVERLAP:g} mm"
    assert s["Case"].startswith(f"{p.CASE_LENGTH:.1f} ×")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_outputs.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cad.viewer'`.

- [ ] **Step 3: Implement** — create `docs/viewer/travel-case-viewer.html` (adapted from the gridfinity-airbrush-bin viewer):

```html
<title>Pinecil Travel Case</title>
<meta name="description" content="Interactive 3D viewer for the Pinecil V2 travel case — toggle shell, insert, velcro and contents, and pull the halves apart." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" />
<style>
  :root {
    --stage-bg: #e7eaee;
    --stage-grid: #c3cad3;
    --panel: #f7f8faee;
    --panel-solid: #f7f8fa;
    --edge: #d0d6dd;
    --ink: #1b2733;
    --ink-soft: #5b6b7a;
    --ink-faint: #8794a1;
    --accent: #2f6fb0;
    --accent-ink: #ffffff;
    --shell: #2b2f36;
    --insert: #e91e63;
    --band: #1e88e5;
    --contents: #3f9a5a;
    --shadow: 0 1px 2px rgba(20,35,50,.08), 0 8px 24px rgba(20,35,50,.10);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --stage-bg: #14171b;
      --stage-grid: #2b313a;
      --panel: #1c2027e6;
      --panel-solid: #1c2027;
      --edge: #2d343d;
      --ink: #dbe0e6;
      --ink-soft: #97a2ad;
      --ink-faint: #6a747f;
      --accent: #4b90d4;
      --accent-ink: #0d1116;
      --shell: #6b7380;
    --insert: #f0508a;
    --band: #4ba3ee;
    --contents: #55b874;
      --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.45);
    }
  }
  :root[data-theme="dark"] {
    --stage-bg: #14171b;
    --stage-grid: #2b313a;
    --panel: #1c2027e6;
    --panel-solid: #1c2027;
    --edge: #2d343d;
    --ink: #dbe0e6;
    --ink-soft: #97a2ad;
    --ink-faint: #6a747f;
    --accent: #4b90d4;
    --accent-ink: #0d1116;
    --shell: #6b7380;
    --insert: #f0508a;
    --band: #4ba3ee;
    --contents: #55b874;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.45);
  }

  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0;
    background: var(--stage-bg);
    color: var(--ink);
    font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
    overflow: hidden;
  }
  #stage { position: fixed; inset: 0; display: block; touch-action: none; cursor: grab; }
  #stage:active { cursor: grabbing; }

  .hud { position: fixed; z-index: 5; }

  /* title block — top left, drafting convention */
  .titleblock {
    top: 16px; left: 16px;
    background: var(--panel);
    backdrop-filter: blur(8px);
    border: 1px solid var(--edge);
    border-radius: 3px;
    box-shadow: var(--shadow);
    padding: 12px 14px;
    max-width: min(78vw, 340px);
  }
  .titleblock h1 {
    margin: 0;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: .01em;
    text-wrap: balance;
  }
  .titleblock .sub {
    margin-top: 3px;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 11px;
    color: var(--ink-soft);
    letter-spacing: .02em;
  }
  .specs {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--edge);
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 3px 14px;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 11px;
    line-height: 1.45;
  }
  .specs dt { color: var(--ink-faint); text-transform: uppercase; letter-spacing: .05em; font-size: 10px; padding-top: 1px; }
  .specs dd { margin: 0; color: var(--ink); font-variant-numeric: tabular-nums; }

  /* layer toggles — top right */
  .layers {
    top: 16px; right: 16px;
    display: flex; flex-direction: column; gap: 6px; align-items: stretch;
  }
  .chip {
    -webkit-appearance: none; appearance: none;
    font: 500 12px/1 "IBM Plex Sans", sans-serif;
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px;
    background: var(--panel);
    backdrop-filter: blur(8px);
    color: var(--ink);
    border: 1px solid var(--edge);
    border-radius: 3px;
    box-shadow: var(--shadow);
    cursor: pointer;
    text-align: left;
    transition: border-color .12s, background .12s;
  }
  .chip:hover { border-color: var(--ink-faint); }
  .chip .sw { width: 11px; height: 11px; border-radius: 2px; flex: none; border: 1px solid rgba(0,0,0,.15); }
  .chip .key { color: var(--ink-faint); font-family: "IBM Plex Mono", monospace; font-size: 10px; margin-left: auto; }
  .chip[aria-pressed="false"] { color: var(--ink-faint); background: transparent; box-shadow: none; }
  .chip[aria-pressed="false"] .sw { opacity: .3; }
  .chip:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

  /* view presets — bottom right */
  .views {
    bottom: 16px; right: 16px;
    display: flex; gap: 6px;
    background: var(--panel);
    backdrop-filter: blur(8px);
    border: 1px solid var(--edge);
    border-radius: 3px;
    box-shadow: var(--shadow);
    padding: 5px;
  }
  .views button {
    -webkit-appearance: none; appearance: none;
    font: 500 11px/1 "IBM Plex Mono", monospace;
    letter-spacing: .04em;
    text-transform: uppercase;
    padding: 7px 10px;
    background: transparent;
    color: var(--ink-soft);
    border: 0; border-radius: 2px;
    cursor: pointer;
  }
  .views button:hover { background: color-mix(in srgb, var(--accent) 14%, transparent); color: var(--ink); }
  .views button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }

  /* hint — bottom left */
  .hint {
    bottom: 16px; left: 16px;
    font-family: "IBM Plex Mono", monospace;
    font-size: 10px;
    color: var(--ink-faint);
    letter-spacing: .03em;
    line-height: 1.6;
    pointer-events: none;
  }
  .hint b { color: var(--ink-soft); font-weight: 500; }

  @media (max-width: 640px) {
    .specs { display: none; }
    .hint { display: none; }
    .titleblock { max-width: 60vw; }
  }

  .explode { display: flex; align-items: center; gap: 8px; margin-top: 10px; font: 500 11px "IBM Plex Mono", monospace; color: var(--ink-soft); }
  .explode input { flex: 1; accent-color: var(--accent); }

  .loading {
    position: fixed; inset: 0; display: grid; place-items: center;
    font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--ink-soft);
    background: var(--stage-bg);
    z-index: 10;
  }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<canvas id="stage"></canvas>

<div class="hud titleblock">
  <h1>Pinecil V2 travel case</h1>
  <div class="sub">tube · PLA shell + PETG insert · velcro loop</div>
  <dl class="specs" id="specs"></dl>
  <label class="explode">open <input type="range" id="explode" min="0" max="120" value="0" step="1" /> <span id="explode-val">0 mm</span></label>
</div>

<div class="hud layers" id="layers">
  <button class="chip" data-layer="shellA" aria-pressed="true"><span class="sw" style="background:var(--shell)"></span> Shell A <span class="key">1</span></button>
  <button class="chip" data-layer="shellB" aria-pressed="true"><span class="sw" style="background:var(--shell)"></span> Shell B (logo) <span class="key">2</span></button>
  <button class="chip" data-layer="insertA" aria-pressed="true"><span class="sw" style="background:var(--insert)"></span> Insert A <span class="key">3</span></button>
  <button class="chip" data-layer="insertB" aria-pressed="true"><span class="sw" style="background:var(--insert)"></span> Insert B <span class="key">4</span></button>
  <button class="chip" data-layer="band" aria-pressed="true"><span class="sw" style="background:var(--band)"></span> Velcro <span class="key">5</span></button>
  <button class="chip" data-layer="contents" aria-pressed="true"><span class="sw" style="background:var(--contents)"></span> Iron, tips, key <span class="key">6</span></button>
  <button class="chip" data-layer="grid" aria-pressed="true"><span class="sw" style="background:var(--stage-grid)"></span> Grid <span class="key">7</span></button>
</div>

<div class="hud views" id="views">
  <button data-view="iso">Iso</button>
  <button data-view="top">Top</button>
  <button data-view="front">Front</button>
  <button data-view="side">Side</button>
</div>

<div class="hud hint">
  <b>drag</b> orbit &nbsp;·&nbsp; <b>wheel</b> zoom &nbsp;·&nbsp; <b>shift-drag</b> pan
</div>

<div class="loading" id="loading">building geometry…</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
  const GEOM = "__GEOM__";
  const SPECS = "__SPECS__";
</script>
<script>
(function () {
  "use strict";
  const $ = (s) => document.querySelector(s);

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  // ---- binary STL -> BufferGeometry ------------------------------------------
  function parseSTL(b64) {
    const bin = atob(b64);
    const len = bin.length;
    const buf = new ArrayBuffer(len);
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    const dv = new DataView(buf);
    const tris = dv.getUint32(80, true);
    const pos = new Float32Array(tris * 9);
    let o = 84;
    for (let t = 0; t < tris; t++) {
      o += 12; // skip face normal
      for (let v = 0; v < 3; v++) {
        pos[t * 9 + v * 3 + 0] = dv.getFloat32(o, true);
        pos[t * 9 + v * 3 + 1] = dv.getFloat32(o + 4, true);
        pos[t * 9 + v * 3 + 2] = dv.getFloat32(o + 8, true);
        o += 12;
      }
      o += 2; // attribute byte count
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.computeVertexNormals();
    return g;
  }

  // ---- scene ----------------------------------------------------------------
  const canvas = $("#stage");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 1, 4000);
  camera.up.set(0, 0, 1); // Z is up, CAD convention

  const NAMES = ["shellA", "shellB", "insertA", "insertB", "band", "contents"];
  const geoms = {};
  NAMES.forEach((n) => (geoms[n] = parseSTL(GEOM[n])));

  // recenter on the closed case's bounding box
  const bb = new THREE.Box3();
  ["shellA", "shellB"].forEach((n) => { geoms[n].computeBoundingBox(); bb.union(geoms[n].boundingBox); });
  const ctr = new THREE.Vector3();
  bb.getCenter(ctr);
  const size = new THREE.Vector3();
  bb.getSize(size);
  const radius = size.length() / 2;
  Object.values(geoms).forEach((g) => g.translate(-ctr.x, -ctr.y, -ctr.z));

  function mat(colorVar) {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(cssVar(colorVar)), metalness: 0.0, roughness: 0.62,
    });
  }

  const COLOR = { shellA: "--shell", shellB: "--shell", insertA: "--insert", insertB: "--insert", band: "--band", contents: "--contents" };
  const meshes = {};
  NAMES.forEach((n) => { meshes[n] = new THREE.Mesh(geoms[n], mat(COLOR[n])); scene.add(meshes[n]); });

  // half B (shell B + insert B) slides along +X when "opening"
  const movesWithB = ["shellB", "insertB"];

  // grid at the case's bottom face (z = 0)
  const bedZ = -ctr.z;
  const grid = new THREE.GridHelper(300, 30, new THREE.Color(cssVar("--stage-grid")), new THREE.Color(cssVar("--stage-grid")));
  grid.rotation.x = Math.PI / 2;
  grid.position.z = bedZ - 0.05;
  grid.material.transparent = true;
  grid.material.opacity = 0.5;
  scene.add(grid);

  // lights
  const hemi = new THREE.HemisphereLight(0xffffff, 0x404652, 0.55);
  scene.add(hemi);
  const key = new THREE.DirectionalLight(0xffffff, 0.85);
  key.position.set(120, -160, 220);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 0.35);
  fill.position.set(-160, 120, 90);
  scene.add(fill);

  function applyThemeColors() {
    renderer.setClearColor(new THREE.Color(cssVar("--stage-bg")), 1);
    NAMES.forEach((n) => meshes[n].material.color.set(cssVar(COLOR[n])));
    grid.material.color = new THREE.Color(cssVar("--stage-grid"));
  }
  applyThemeColors();
  const mq = matchMedia("(prefers-color-scheme: dark)");
  mq.addEventListener && mq.addEventListener("change", applyThemeColors);

  // ---- hand-rolled orbit --------------------------------------------------
  const target = new THREE.Vector3(0, 0, 0);
  let theta = Math.PI * 0.28, phi = Math.PI * 0.36, dist = radius * 3.1;
  const MINP = 0.05, MAXP = Math.PI - 0.05;

  function setView(name) {
    if (name === "iso") { theta = Math.PI * 0.28; phi = Math.PI * 0.36; }
    else if (name === "top") { theta = -Math.PI / 2; phi = 0.001; }
    else if (name === "front") { theta = -Math.PI / 2; phi = Math.PI / 2; }
    else if (name === "side") { theta = 0; phi = Math.PI / 2; }
    dist = radius * (name === "top" ? 2.7 : 3.1);
    target.set(0, 0, 0);
  }

  function updateCamera() {
    phi = Math.max(MINP, Math.min(MAXP, phi));
    const sp = Math.sin(phi);
    camera.position.set(
      target.x + dist * sp * Math.cos(theta),
      target.y + dist * sp * Math.sin(theta),
      target.z + dist * Math.cos(phi)
    );
    camera.lookAt(target);
  }

  let drag = null;
  canvas.addEventListener("pointerdown", (e) => {
    drag = { x: e.clientX, y: e.clientY, pan: e.shiftKey || e.button === 1 };
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    drag.x = e.clientX; drag.y = e.clientY;
    if (drag.pan) {
      const s = dist * 0.0016;
      const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
      const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
      target.addScaledVector(right, -dx * s);
      target.addScaledVector(up, dy * s);
    } else {
      theta -= dx * 0.008;
      phi -= dy * 0.008;
    }
    updateCamera();
  });
  const endDrag = () => { drag = null; };
  canvas.addEventListener("pointerup", endDrag);
  canvas.addEventListener("pointercancel", endDrag);
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    dist *= Math.pow(1.0016, e.deltaY);
    dist = Math.max(radius * 1.2, Math.min(radius * 8, dist));
    updateCamera();
  }, { passive: false });

  // ---- controls ---------------------------------------------------------
  const targets = { grid: [grid] };
  NAMES.forEach((n) => (targets[n] = [meshes[n]]));
  document.querySelectorAll(".chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      const on = btn.getAttribute("aria-pressed") === "true";
      btn.setAttribute("aria-pressed", String(!on));
      targets[btn.dataset.layer].forEach((m) => (m.visible = !on));
    });
  });
  document.querySelectorAll("#views button").forEach((btn) => {
    btn.addEventListener("click", () => { setView(btn.dataset.view); updateCamera(); });
  });
  const keys = ["shellA", "shellB", "insertA", "insertB", "band", "contents", "grid"];
  addEventListener("keydown", (e) => {
    const i = parseInt(e.key, 10) - 1;
    if (i >= 0 && i < keys.length) document.querySelector(`.chip[data-layer="${keys[i]}"]`).click();
    const vmap = { i: "iso", t: "top", f: "front", s: "side" };
    if (vmap[e.key]) { setView(vmap[e.key]); updateCamera(); }
  });
  const slider = $("#explode");
  slider.addEventListener("input", () => {
    const d = Number(slider.value);
    movesWithB.forEach((n) => (meshes[n].position.x = d));
    $("#explode-val").textContent = d + " mm";
  });
  // spec sheet from the model's parameters
  const dl = $("#specs");
  Object.entries(SPECS).forEach(([k, v]) => {
    const dt = document.createElement("dt"); dt.textContent = k;
    const dd = document.createElement("dd"); dd.textContent = v;
    dl.append(dt, dd);
  });

  // ---- resize + loop ---------------------------------------------------
  function resize() {
    const w = innerWidth, h = innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  addEventListener("resize", resize);
  resize();
  setView("iso");
  updateCamera();

  function loop() {
    requestAnimationFrame(loop);
    renderer.render(scene, camera);
  }
  loop();
  $("#loading").remove();
})();
</script>
```

Create `cad/viewer.py`:

```python
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
        "Insert A / B": f"{p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP - p.END_CAP_THICKNESS:.1f} / "
                        f"{p.CASE_LENGTH - p.END_CAP_THICKNESS - p.INSERT_SPLIT_X:.1f} mm",
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
```

Add to `Makefile` after `sections`:

```make
viewer:
	uv run python -m cad.viewer
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_outputs.py -q` → 4 passed. Then `make viewer` → `wrote build/travel-case-viewer.html (~2 MB)`. Check it renders (headless):

```bash
google-chrome --headless=new --disable-gpu --use-angle=swiftshader --enable-unsafe-swiftshader \
  --window-size=1400,900 --virtual-time-budget=8000 \
  --screenshot=build/viewer-shot.png "file://$PWD/build/travel-case-viewer.html"
```

Expected screenshot: dark case on a grid, blue band in the top groove, logo on the end face, spec sheet top-left (Case 172.8 × 60.1 × 37.9 mm). Then `make test`.

- [ ] **Step 5: Commit**

```bash
git add docs/viewer/travel-case-viewer.html cad/viewer.py Makefile tests/test_outputs.py
git commit -m "Standalone 3D viewer: layers, explode slider, spec sheet

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Docs

**Files:**
- Modify: `README.md`, `CLAUDE.md`, `TODO.md`

- [ ] **Step 1: README** — replace the opening paragraph and the Layout/Build sections. New opening (after the title):

```markdown
A 3D-printable travel case for a **Pinecil V2** soldering iron with 4 spare tips
and the M2 hex key: a rounded-trapezoid tube, black PLA shell + PETG insert,
closed by one loop of double-sided velcro. The Pinecil logo (the PINE64
pinecone) is cut through the cap's end face.

**Tracking:** `TODO.md` in this repo.

Geometry is authored in [build123d](https://github.com/gumyr/build123d). The
model in plain language (Dutch): [`docs/model.md`](docs/model.md). Decisions
and acceptance criteria: the
[design spec](docs/superpowers/specs/2026-10-04-travel-case-design.md).
```

New Layout section:

```markdown
## Layout

- `cad/params.py` — every dimension; derived lengths are computed
- `cad/contents.py` — iron, tips and key: layout B and envelopes
- `cad/profile.py` — channel sections, fitted insert trapezoid, shell profile
- `cad/band.py` — the velcro band ring (grooves + channel behind the end caps)
- `cad/insert.py`, `cad/shell.py` — the printable parts, split in A and B
- `cad/solids.py` — 2D section → 3D extrusion helpers
- `cad/pinecil_logo.py`, `cad/pinecil_logo.svg` — the logo (see below)
- `cad/build.py` — exports; `logo_cutter()`; logo test plate
- `cad/sections.py`, `cad/viewer.py`, `docs/viewer/` — section renders, 3D viewer
- `cad/render.py` — logo centreline validation render
- `tests/` — geometry assertions, one file per module
```

New Build section:

~~~markdown
## Build

```sh
make test       # pytest (~20 s)
make build      # build/{shell-a,shell-b,insert-a,insert-b,logo-plate}.{step,stl}
make sections   # build/sections.svg (+ .png) — cross-sections from the 3D model
make viewer     # build/travel-case-viewer.html — standalone 3D viewer
make render     # build/logo-centerlines.svg — logo rib centrelines
```

Print every part standing (axis vertical); shell B end-cap-down so the logo
ribs are the first layer. Glue each insert into its shell half up to the end
stop, let it cure, then thread the velcro (see `docs/model.md`, Montage).
~~~

Keep the existing "Pinecil logo" and "Source" sections.

- [ ] **Step 2: CLAUDE.md** — add these bullets:

```markdown
- The case model in plain language is `docs/model.md` — keep it in sync when
  the geometry changes. Decisions + acceptance criteria: the design spec in
  `docs/superpowers/specs/`.
- Check geometry changes visually with `make sections` / `make viewer`, not
  only with tests.
```

- [ ] **Step 3: TODO.md** — replace the Case section with:

```markdown
## Case
- [x] Design the Pinecil V2 travel case — spec: docs/superpowers/specs/2026-10-04-travel-case-design.md, plain-language: docs/model.md
- [x] Model shell A/B + insert A/B, sections, viewer
- [ ] Owner review in the viewer
- [ ] Confirm velcro width/thickness with the real strip
- [ ] Exact iron and tip channel shapes
- [ ] Test print (shell B end cap + logo first?)
```

- [ ] **Step 4: Verify** — `make test` all green; `make build sections viewer` succeed.

- [ ] **Step 5: Commit**

```bash
git add README.md CLAUDE.md TODO.md
git commit -m "Docs: README layout/build for the case, CLAUDE notes, TODO

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
