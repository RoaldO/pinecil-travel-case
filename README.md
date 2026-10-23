# Pinecil V2 travel case

A 3D-printable case to take a **Pinecil V2** soldering iron on the road —
together with **four spare tips** and a little **hex key** for swapping
them. Everything has its own snug, shaped channel, nothing rattles, and the
case clicks shut with magnets and is held closed by one loop of velcro. The
Pinecil logo (the PINE64 pinecone) is cut through the cap, with the velcro
showing through it.

It prints in **four parts, all PETG, no supports**, on a 180 × 180 mm bed.
Ready-to-print STLs and photos:
[Printables](https://www.printables.com/model/1887698-pinecil-v2-travel-case-iron-4-spare-tips-hex-key).

**Tracking:** `TODO.md` in this repo. The model in plain language (Dutch):
[`docs/model.md`](docs/model.md). Decisions and acceptance criteria: the
[design spec](docs/superpowers/specs/2026-10-04-travel-case-design.md).

## What goes in

| Item | Notes |
|---|---|
| Pinecil V2, with a tip fitted | handle base deep in half A, display and buttons facing up |
| 4 spare tips | standing base-down in half A, so you can see which is which |
| L-shaped hex key | for an M2 hex screw holding the tip (see below); long leg in a hole, short leg free to grab |

The case is **175 × 57 × 43 mm**.

## Compatibility

Designed for the **Pinecil V2 with its short tips**. The channels are
modelled on the real things, measured with calipers — so the case fits what
was measured; anything else is a matter of changing the parameters.

- **Iron:** Pinecil **V2**. The handle is a "tombstone" (a half cylinder
  with a block on its flat side), 13.78 wide with a 14.6 rubber grip; the
  screw head, the two buttons, the tip's screw and the foot are all
  modelled. Other irons — or a V1 — would need their own measurements.
- **Tips:** the short Pinecil tips, with the white ceramic rings at the base
  (base Ø 5.4 / 5.7, collar Ø 11, sleeve ≤ Ø 5.5), **up to 92 mm long**.
  Tip lengths vary a little; shorter ones simply have more room at the end.
- **Tip screw — swapping tips on the road:** the tip is held by two
  screws, normally Phillips heads. Replace **one** of them (two would get
  bulky) by either
  - an **M2 × 5 thumb screw** with a knurled head you turn by hand — that's
    what the case is modelled around (head Ø 6, 2.8 high), or
  - an **M2 × 5 hex socket screw** — then the hex key below travels along.
- **Hex key:** L-shaped, 1.5 mm across flats, legs 46 and 16 mm — for the
  M2 hex screw.
- **Velcro:** one strip of double-sided velcro, **20 mm wide, 2 mm thick**
  per layer (still to be confirmed with the real strip — both are
  parameters).
- **Magnets:** six neodymium discs, **Ø 3 × 2 mm** (three per half).

Different items? Every dimension lives in [`cad/params.py`](cad/params.py);
change it there and the channels, the layout and the case size follow.

## Design

**Cross-section.** A rounded trapezoid, wide side down so it lies stable on
a table. Bottom row: tip – iron – tip; top row: tip – key – tip. The iron
lies round side down, so nothing presses on its display and buttons.

**Two layers.** A thin outer **shell** and a solid **insert** inside it with
a channel for every item (originally two materials; now both PETG, ideally
in two colours). Each half's insert is glued into its own shell half.

**Channels follow the real objects.** Each channel is the item grown by a
clearance — 0.4 mm all round, 0.3 for the tips' base, and an extra 1 mm
around the iron's buttons and display so they never tap the wall when it
rattles. Because things slide in and out, a channel may only get **narrower
going deeper**, never wider again — so a channel also takes whatever passes
it on the way in, and every step lies 0.4 deeper than the item's shoulder,
so nothing is ever clamped end to end.

**Two halves that overlap.** The inserts are cut 21 mm short of the tip
ends, so the spare tips stick out of half A far enough to grab; the shells
are cut 20 mm earlier, so insert A slides into shell B and lines the halves
up. A 0.5 mm gap between the inserts makes sure the shells always meet
first, whatever the print or glue tolerance.

**Closing.** A loop of velcro runs lengthwise around the case: flush in a
groove on top, bending inward and behind both end caps (that's what you see
through the logo), and overlapping itself underneath, where you pull it open.
Three magnets per half make it **click shut** on its own. A small hidden
vent behind the band stops the snug halves from sucking a vacuum when you
open them.

**The hex key** turns freely on its long leg, so its short leg has to meet
its pocket in the other half when you close the case. A shallow **groove**
in the face of half A shows the right angle, and a **funnel** at the mouth
of the pocket turns a leg that is off by up to 20° back into line as you
close the case.

**Made to print.** Every part prints standing, with no supports:

- every channel widens towards the top, so there are no overhangs inside;
- tapers are built from 0.2 mm steps (one layer), so they print as tapers;
- the inserts end flat — beside the band channel the shell carries the end
  stops — so they print flat on the bed with no bridge over the band;
- at least 1.2 mm of material between channels, and sharp spikes where
  the key's pocket runs past other channels are shaved off;
- chamfers lead each part into the next.

**Tested in slices.** Before printing whole parts, the fits were tuned with
thin test slices of the real parts (`make coupons`); the plan, the results
and which parameter fixes which complaint are in
[`docs/testprint.md`](docs/testprint.md).

## Printing

| Part | File | On the bed | Length |
|---|---|---|---|
| Shell A | `shell-a.stl` | its end cap | 68 mm |
| Shell B (cap, with logo) | `shell-b.stl` | its end cap — the logo is the first layer | 107 mm |
| Insert A | `insert-a.stl` | its flat outer end (the chamfered one) | 83 mm |
| Insert B | `insert-b.stl` | its flat outer end (the chamfered one) | 83 mm |

The STL files come out lying down (the case's axis horizontal) — stand them
up in the slicer as above. Settings that worked:

- **PETG, dried** first (damp PETG strings badly), **240 °C**;
- 0.4 mm nozzle, 0.2 mm layers;
- **seam painted or random** — an aligned seam scored the test prints;
- **no supports**.

The clearances were tuned on one printer; on another, print the test slices
first (`make coupons`, see [`docs/testprint.md`](docs/testprint.md)) and
adjust `cad/params.py` if needed.

## Assembly

1. Glue the **magnets** into the three holes in the face of each insert —
   opposite poles facing, so the halves attract. Tip: hold a loose magnet
   against the one you've just glued in, and glue its partner in the other
   half with the same side facing out.
2. Trace the **alignment groove** in insert A's face with a marker — without
   colour it's hard to see.
3. Glue each insert into its own shell half, pushed in up to the end stops.
4. Let the glue cure.
5. Only then thread the **velcro**: in at the top slot, behind the end cap,
   out at the bottom — at both ends — and overlap the ends underneath. The
   channel has generous bends so the strap can be pushed through.
6. Iron, tips and key into half A, slide the cap on, close the velcro.

## Building from source

Requires [`uv`](https://docs.astral.sh/uv/); everything runs via `make`.
Geometry is authored in [build123d](https://github.com/gumyr/build123d).

```sh
make test       # pytest (~5 min: builds every part several ways)
make build      # build/{shell-a,shell-b,insert-a,insert-b,logo-plate}.{step,stl}
make coupons    # build/coupons/*.{stl,step} — thin test-print slices of the real parts
make sections   # build/sections.svg (+ .png) — cross-sections from the 3D model
make viewer     # build/travel-case-viewer.html — standalone 3D viewer
make render     # build/logo-centerlines.svg — logo rib centrelines
```

The **viewer** is a single HTML file: toggle the parts, pull the halves
apart, make the case see-through and show its edges.

### Layout

- `cad/params.py` — every dimension; derived lengths are computed
- `cad/contents.py` — iron, tips and key: their shapes and layout
- `cad/profile.py` — channel sections, fitted insert trapezoid, shell profile, magnet spots
- `cad/band.py` — the velcro band ring (grooves + channel behind the end caps)
- `cad/insert.py`, `cad/shell.py` — the printable parts, split in A and B
- `cad/solids.py` — 2D section → 3D extrusion and chamfer helpers
- `cad/pinecil_logo.py`, `cad/pinecil_logo.svg` — the logo and its cutter (see below)
- `cad/build.py` — exports; logo test plate
- `cad/coupons.py` — test-print slices where the fit matters
- `cad/sections.py`, `cad/viewer.py`, `docs/viewer/` — section renders, 3D viewer
- `cad/render.py` — logo centreline validation render
- `tests/` — geometry assertions, one file per module

### Pinecil logo

The pinecone is 10 pieces (P1..P10) — triangles, rhombi and the stemmed base —
which become **holes**. The gaps between them are the **ribs**: they lie on 6
straight lattice lines (L1..L6) that cross on the vertical axis. The rib
centrelines are recovered from the artwork itself (facing parallel edges of
neighbouring pieces → midline → merge collinear segments), then each hole is its
piece minus a `RIB_WIDTH` band around the centrelines. Widening the ribs eats
into the holes; the logo's outer outline never moves, so it never exceeds
`LOGO_MAX_SIZE`.

| | default | |
|---|---|---|
| `LOGO_MAX_SIZE` | 19.0 mm | max of logo width/height (the pinecone is 14.03 × 19.00 mm) |
| `RIB_WIDTH` | 0.8 mm | rib width; prints clean and sturdy (tested). The artwork's own gaps are 0.71–0.74 mm; values below that have no effect |
| `PLATE_THICKNESS` | 2.0 mm | test plate |
| `PLATE_MARGIN` | 3.0 mm | test plate edge to logo |

## Source

`cad/pinecil_logo.svg` is the PINE64 pinecone mark (the logo on the Pinecil),
taken as a clean 10-path SVG from
[`nabuph/pinecil-web-flash`](https://github.com/nabuph/pinecil-web-flash/blob/main/public/pine64-pinecone.svg).
It matches the pinecone in PINE64's own
[`logo.svg`](https://github.com/pine64/website/blob/main/themes/pinetheme/static/img/logo.svg).
The logo is PINE64's trademark — personal use only.
