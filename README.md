# pinecil-travel-case

A 3D-printable travel case for a **Pinecil V2** soldering iron with 4 spare tips
and the M2 hex key: a rounded-trapezoid tube, black PLA shell + PETG insert,
closed by one loop of double-sided velcro. The Pinecil logo (the PINE64
pinecone) is cut through the cap's end face.

**Tracking:** `TODO.md` in this repo.

Geometry is authored in [build123d](https://github.com/gumyr/build123d). The
model in plain language (Dutch): [`docs/model.md`](docs/model.md). Decisions
and acceptance criteria: the
[design spec](docs/superpowers/specs/2026-10-04-travel-case-design.md).

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

- `cad/params.py` — every dimension; derived lengths are computed
- `cad/contents.py` — iron, tips and key: layout B and envelopes
- `cad/profile.py` — channel sections, fitted insert trapezoid, shell profile
- `cad/band.py` — the velcro band ring (grooves + channel behind the end caps)
- `cad/insert.py`, `cad/shell.py` — the printable parts, split in A and B
- `cad/solids.py` — 2D section → 3D extrusion helpers
- `cad/pinecil_logo.py`, `cad/pinecil_logo.svg` — the logo (see above)
- `cad/build.py` — exports; `logo_cutter()`; logo test plate
- `cad/coupons.py` — test-print slices where the fit matters
- `cad/sections.py`, `cad/viewer.py`, `docs/viewer/` — section renders, 3D viewer
- `cad/render.py` — logo centreline validation render
- `tests/` — geometry assertions, one file per module

## Build

```sh
make test       # pytest (~20 s)
make build      # build/{shell-a,shell-b,insert-a,insert-b,logo-plate}.{step,stl}
make coupons    # build/coupons/*.{stl,step} — thin test-print slices of the real parts
make sections   # build/sections.svg (+ .png) — cross-sections from the 3D model
make viewer     # build/travel-case-viewer.html — standalone 3D viewer
make render     # build/logo-centerlines.svg — logo rib centrelines
```

Print every part standing (axis vertical); shell B end-cap-down so the logo
ribs are the first layer. Glue each insert into its shell half up to the end
stop, let it cure, then thread the velcro (see `docs/model.md`, Montage).

## Source

`cad/pinecil_logo.svg` is the PINE64 pinecone mark (the logo on the Pinecil),
taken as a clean 10-path SVG from
[`nabuph/pinecil-web-flash`](https://github.com/nabuph/pinecil-web-flash/blob/main/public/pine64-pinecone.svg).
It matches the pinecone in PINE64's own
[`logo.svg`](https://github.com/pine64/website/blob/main/themes/pinetheme/static/img/logo.svg).
The logo is PINE64's trademark — personal use only.
