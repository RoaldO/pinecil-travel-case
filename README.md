# pinecil-travel-case

A 3D-printable travel case for a **Pinecil V2** soldering iron. The case itself
comes later; the first part is the Pinecil logo (the PINE64 pinecone) as a
pattern of through-holes, with parametric rib width.

**Tracking:** `TODO.md` in this repo.

Geometry is authored in [build123d](https://github.com/gumyr/build123d).

## Pinecil logo

The pinecone is 10 pieces (P1..P10) — triangles, rhombi and the stemmed base —
which become **holes**. The gaps between them are the **ribs**: they lie on 6
straight lattice lines (L1..L6) that cross on the vertical axis. The rib
centrelines are recovered from the artwork itself (facing parallel edges of
neighbouring pieces → midline → merge collinear segments), then each hole is its
piece minus a `RIB_WIDTH` band around the centrelines. Widening the ribs eats
into the holes; the logo's outer outline never moves, so it never exceeds
`LOGO_MAX_SIZE`.

Parameters (`cad/params.py`):

| | default | |
|---|---|---|
| `LOGO_MAX_SIZE` | 19.0 mm | max of logo width/height (the pinecone is 14.03 × 19.00 mm) |
| `RIB_WIDTH` | 0.8 mm | rib width; the artwork's own gaps are 0.71–0.74 mm, values below that have no effect |
| `PLATE_THICKNESS` | 2.0 mm | test plate |
| `PLATE_MARGIN` | 3.0 mm | test plate edge to logo |

## Layout

- `cad/pinecil_logo.svg` — the pinecone artwork (see *Source* below)
- `cad/params.py` — every dimension
- `cad/pinecil_logo.py` — SVG → pieces, rib centrelines, holes (2D, shapely)
- `cad/build.py` — build123d: `logo_cutter()` (reusable for the case) and the test plate
- `cad/render.py` — validation render: artwork + centreline ids, and the resulting plate
- `tests/` — geometry assertions

## Build

```sh
make test     # pytest
make render   # build/logo-centerlines.svg (+ .png via inkscape)
make build    # build/logo-plate.step + build/logo-plate.stl
```

Requires `uv`.

## Source

`cad/pinecil_logo.svg` is the PINE64 pinecone mark (the logo on the Pinecil),
taken as a clean 10-path SVG from
[`nabuph/pinecil-web-flash`](https://github.com/nabuph/pinecil-web-flash/blob/main/public/pine64-pinecone.svg).
It matches the pinecone in PINE64's own
[`logo.svg`](https://github.com/pine64/website/blob/main/themes/pinetheme/static/img/logo.svg).
The logo is PINE64's trademark — personal use only.
