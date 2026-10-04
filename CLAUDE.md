# pinecil-travel-case — notes for Claude

See [`README.md`](README.md).

**Tracking:** `TODO.md` in this repo — open work and new items go there.

- Python via `uv` only. `make` targets, not `just`.
- build123d for 3D; the logo is 2D-processed in shapely (`cad/pinecil_logo.py`).
- `cad/params.py` is the single source of truth for every dimension.
- Rib centreline ids (L1..L6) and piece ids (P1..P10) are what the owner uses
  to give feedback — check them against `make render` before changing the
  detection; keep ids stable.
- The case model in plain language is `docs/model.md` — keep it in sync when
  the geometry changes. Decisions + acceptance criteria: the design spec in
  `docs/superpowers/specs/`.
- Check geometry changes visually with `make sections` / `make viewer`, not
  only with tests.
