# Pinecil V2 travel case — design spec

Date: 2026-10-04. Status: approved in brainstorm, pending written-spec review.

The plain-language description of the model is [`docs/model.md`](../../model.md)
(Dutch, kept current). This spec records the decisions, the geometry
definitions, every parameter, and the acceptance criteria.

## Goal

A 3D-printable tube case for a Pinecil V2 with its tip, 4 spare tips and the
M2 hex key. Printer: 180 × 180 bed, 180 max print height. Inner part PETG
(colour), outer part black PLA. Closed by one loop of double-sided velcro.
The existing Pinecil logo (`cad/pinecil_logo.py`) goes through the end cap of
the cap half.

## Decisions (from the brainstorm)

| # | Decision |
|---|---|
| D1 | Cross-section: rounded trapezoid, wide side down (the side it rests on). |
| D2 | Layout B: bottom row tip – iron – tip; top row tip – key channel – tip. |
| D3 | Inner part is a **solid insert with per-item channels** (not a thin tube). |
| D4 | Outer shell split at mid-length; insert split elsewhere → overlap. |
| D5 | Half A: short insert, items protrude when opened. Half B ("cap"): long insert slides into outer A; **logo on B's end cap**. |
| D6 | Key K1: short leg crosswise at the deep end of A, against the insert end wall; top tips shifted toward B to make room; long leg protrudes `KEY_GRIP` past insert A. The **insert split position is derived** from this. |
| D7 | Velcro: one closed lengthwise loop. Top: flush groove, continuous across the splits. Ends: bends inward, runs between insert and shell behind the end caps. Bottom: the two strip ends overlap → double layer → deeper groove. |
| D8 | Velcro path = **band ring**: in side view, an outer rounded block minus an inner rounded block, *almost* concentric (inner block is one band thickness smaller at top and ends, two at the bottom); extruded across the band width; subtracted (with clearance) from shell **and** insert. Bends, no corners; band must slide freely so the case can be opened. |
| D9 | Shell top wall = 1 band layer + clearance + floor; bottom wall = 2 layers + clearance + floor; side walls plain. |
| D10 | Logo upright when the case rests on its wide side (logo top → narrow side); must lie within the straight vertical run of the band behind the end cap, with margin. |
| D11 | Inserts are glued into their own shell half (velcro placed first). |
| D12 | All parts print standing (axis vertical); cap half prints end-cap-down so the logo ribs are the first layer. |
| D13 | No magic numbers: every dimension is a named parameter; derived values are computed. |

## Coordinate system

- X: case axis, from the outer face of half A's end cap (x = 0) to half B's
  (x = `CASE_LENGTH`).
- Z: up; z = 0 is the bottom (wide) face.
- Y: across; y = 0 is the symmetry plane.

## Parameters (`cad/params.py`, starting values, mm)

### Contents (simplified envelopes)

| Name | Value | Note |
|---|---|---|
| `IRON_LENGTH` | 159.0 | measured, with tip |
| `IRON_HANDLE_LENGTH` | 103.0 | spec sheet |
| `IRON_WIDTH` | 17.4 | measured, lies wide (Y) |
| `IRON_HEIGHT` | 14.4 | measured (Z) |
| `IRON_METAL_DIAMETER` | 5.0 | assumed; thin part past the handle |
| `TIP_LENGTH` | 90.0 | measured |
| `TIP_DIAMETER` | 11.0 | widest, measured |
| `KEY_LONG_LEG` | 46.0 | measured |
| `KEY_SHORT_LEG` | 16.0 | measured |
| `KEY_HEX` | 1.46 | measured (across flats) |

### Insert

| Name | Value | Note |
|---|---|---|
| `ITEM_CLEARANCE` | 0.4 | item → channel wall, radial |
| `ITEM_END_CLEARANCE` | 1.0 | item end → cavity end |
| `INSERT_WEB` | 1.2 | min PETG between channels |
| `INSERT_WALL` | 1.2 | min PETG channel → insert surface |
| `INSERT_END_WALL` | 1.6 | insert end walls |
| `INSERT_CORNER_RADIUS` | 3.0 | trapezoid corner radius |
| `TOP_EXTRA_WIDTH` | 0.0 | widen the top flat (for the groove margin) |
| `KEY_GRIP` | 8.0 | key protrusion past insert A |

### Shell and fits

| Name | Value | Note |
|---|---|---|
| `SHELL_SIDE_WALL` | 1.6 | |
| `SHELL_FLOOR` | 1.2 | PLA left under a groove |
| `END_CAP_THICKNESS` | 2.0 | logo depth |
| `GLUE_CLEARANCE` | 0.2 | insert → own shell half |
| `SLIDE_CLEARANCE` | 0.2 | insert B → shell A (overlap) |
| `SPLIT_GAP` | 0.0 | material removed at a cut (0 = plain cut) |

### Velcro

| Name | Value | Note |
|---|---|---|
| `VELCRO_WIDTH` | 20.0 | to be confirmed with the real strip |
| `VELCRO_THICKNESS` | 2.0 | one layer, to be confirmed |
| `VELCRO_CLEARANCE` | 0.3 | added to the ring thickness and width |
| `VELCRO_BOTTOM_LAYERS` | 2 | |
| `BAND_BEND_RADIUS` | 5.0 | inner block corner radius |

### Logo / print

| Name | Value | Note |
|---|---|---|
| `LOGO_MAX_SIZE` | 19.0 | existing |
| `RIB_WIDTH` | 0.8 | existing |
| `LOGO_BAND_MARGIN` | 1.0 | logo → start of the band bends, each side |
| `MAX_PRINT_HEIGHT` | 180.0 | |
| `PRINT_BED` | 180.0 | |

### Derived (computed, never typed)

- `TOP_TIP_SHIFT` = `KEY_HEX` + 2 × `ITEM_CLEARANCE` + `INSERT_WEB` (≈ 3.5;
  the brainstorm sketch used 4).
- `RING_END` = `VELCRO_THICKNESS` + `VELCRO_CLEARANCE`;
  `RING_TOP` = same; `RING_BOTTOM` = `VELCRO_BOTTOM_LAYERS` ×
  `VELCRO_THICKNESS` + `VELCRO_CLEARANCE`.
- `SHELL_TOP_WALL` = `RING_TOP` + `SHELL_FLOOR`;
  `SHELL_BOTTOM_WALL` = `RING_BOTTOM` + `SHELL_FLOOR`.
- `CAVITY_LENGTH` = `IRON_LENGTH` + 2 × `ITEM_END_CLEARANCE`.
- `CASE_LENGTH` = 2 × (`END_CAP_THICKNESS` + `RING_END` + `INSERT_END_WALL`)
  + `CAVITY_LENGTH` (≈ 172.8).
- `SHELL_SPLIT_X` = `CASE_LENGTH` / 2.
- `INSERT_SPLIT_X` = key end x − `KEY_GRIP`, where the key's short leg sits
  against insert A's end wall + `ITEM_END_CLEARANCE`.
- `OVERLAP` = `SHELL_SPLIT_X` − `INSERT_SPLIT_X` (≈ 42).

## Geometry definitions

1. **Contents** (`contents.py`): each item as a 3D envelope placed in case
   coordinates. Bottom tips and iron start at the cavity start
   (+ `ITEM_END_CLEARANCE`); top tips additionally `TOP_TIP_SHIFT`. Layout B
   positions are computed: bottom row on the cavity floor, top tips dropped
   onto the bottom row with `INSERT_WEB` + 2 × `ITEM_CLEARANCE` spacing, key
   channel centred between the top tips.
2. **Channels**: each item's cross-section offset by `ITEM_CLEARANCE`,
   extruded over its length (+ clearance). The key gets an L-shaped pocket:
   the long-leg channel plus a crosswise slot for the short leg.
3. **Insert profile** (`profile.py`): the smallest symmetric rounded trapezoid
   (`INSERT_CORNER_RADIUS`) containing all channels offset by `INSERT_WALL`,
   with the top half-width increased by `TOP_EXTRA_WIDTH` / 2.
4. **Shell profile**: the insert profile offset by `GLUE_CLEARANCE` +
   `SHELL_SIDE_WALL` at the sides, with the top/bottom faces moved out to
   `SHELL_TOP_WALL` / `SHELL_BOTTOM_WALL`; still a rounded trapezoid.
5. **Band ring** (`band.py`), in the XZ plane:
   - outer block: x ∈ [`END_CAP_THICKNESS`, `CASE_LENGTH` − `END_CAP_THICKNESS`],
     z ∈ [0, case height], corner radius `BAND_BEND_RADIUS` + `RING_END`;
   - inner block: shrunk by `RING_END` at the ends, `RING_TOP` at the top,
     `RING_BOTTOM` at the bottom, corner radius `BAND_BEND_RADIUS`;
   - ring = outer − inner, extruded over y ∈ ±(`VELCRO_WIDTH` /2 +
     `VELCRO_CLEARANCE`).
6. **Insert** (`insert.py`): profile extruded over its length (between the
   band ring's inner block ends), minus channels, minus ring; split at
   `INSERT_SPLIT_X` → insert A, insert B.
7. **Shell** (`shell.py`): shell profile extruded over `CASE_LENGTH`, minus
   the insert envelope (+ `GLUE_CLEARANCE`; `SLIDE_CLEARANCE` in the overlap
   zone of shell A), minus ring; split at `SHELL_SPLIT_X` → shell A, shell B;
   minus `logo_cutter(END_CAP_THICKNESS)` on B's end cap, rotated so the logo
   is upright (top → +Z) as seen from outside, centred on the straight
   vertical run of the band.

## Outputs

- `make build` → `build/` STEP + STL per part: `shell-a`, `shell-b`,
  `insert-a`, `insert-b` (+ the existing `logo-plate`).
- `make sections` → SVG/PNG cross-section and longitudinal section from the
  real model, with labels.
- `make viewer` → self-contained HTML 3D viewer (three.js, embedded STL):
  toggle shell A/B, insert A/B, band, contents; standard views; explode
  slider. Same approach as `gridfinity-airbrush-bin`.

## Acceptance criteria (tests)

1. All four parts are valid single solids.
2. Each part's length ≤ `MAX_PRINT_HEIGHT`; its cross-section fits
   `PRINT_BED`.
3. Contents don't intersect the insert; channels keep `ITEM_CLEARANCE`.
4. Ring doesn't leave less than `SHELL_FLOOR` of shell under any groove.
5. Insert and shell don't intersect (assembled); shell A ↔ insert B keeps
   `SLIDE_CLEARANCE` in the overlap.
6. Logo bounding box lies within the band's straight vertical run minus
   `LOGO_BAND_MARGIN`, and within `VELCRO_WIDTH` minus margin.
7. Logo upright: its top (P1) is toward +Z.
8. Key protrudes exactly `KEY_GRIP` past insert A's split face.
9. `CASE_LENGTH`, `OVERLAP`, `INSERT_SPLIT_X` match the derived formulas.

## Out of scope (later)

- Exact iron and tip channel shapes.
- Real velcro dimensions (parameters only).
- Press-fit / detent alternative to gluing.
- Finger notches, chamfers, text.
