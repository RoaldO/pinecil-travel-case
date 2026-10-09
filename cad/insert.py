"""The PETG insert: solid trapezoid with a channel per item, split in A and B.

Tips and iron each get a bore that follows their pieces (+ ITEM_CLEARANCE;
the tips' base steps + TIP_BASE_CLEARANCE).
An item slides into each insert from its split face, so at every depth the
bore also takes whatever passes it on the way in: in each insert a piece's
bore is the union of its own section and every deeper one. Tips: stepped in
A, the collar resting on the last shoulder; one sleeve-wide bore in B.

Outside the band width it runs up to the end caps (the glue end stop); in the
band width the band ring is cut away. Insert A stops INSERT_SPLIT_GAP short of
insert B so the shells always meet first, whatever the glue tolerance. Insert
B's face has an open pocket that takes the key's short leg.
"""

from __future__ import annotations

import math
from functools import cache

from build123d import Part
from shapely.affinity import rotate
from shapely.geometry import Point, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from cad import params as p
from cad.band import BAND_HALF_WIDTH, ring_section, ring_solid
from cad.contents import key_axis, key_short_leg_line, key_short_leg_section, pieces
from cad.profile import channel_sections, insert_profile, magnet_section
from cad.solids import below_x, chamfer_cutter, extrude_x, extrude_y

TIP_NAMES = ("tip_bl", "tip_br", "tip_tl", "tip_tr")


FUNNEL_ANGLE_STEP = 1.0  # degrees between swept copies of the pocket
SWEEP_TOLERANCE = 0.02  # mm, simplify the swept outline (thousands of points otherwise)
SLIVER_TOUCH = 1e-6  # mm: a sliver "touches" the pocket
SLIVER_OVERLAP = 0.05  # mm, shaved bits reach this far into neighbouring cuts


def pocket_section(turn: float = 0.0) -> BaseGeometry:
    """YZ footprint of the pocket in insert B: key and short leg, hulled,
    grown by POCKET_CLEARANCE, kept INSERT_WALL inside the insert surface.
    With ``turn`` (the funnel) it is swept that many degrees either way round
    the key's axis and may come up to MIN_PRINT_WALL from the insert's
    surface (no strength needed there: it is glued to shell B)."""
    ch = channel_sections()
    parts = [ch["key"], key_short_leg_section(p.ITEM_CLEARANCE)]
    hull = unary_union(parts).convex_hull.buffer(p.POCKET_CLEARANCE, p.ARC_QUAD_SEGMENTS)
    if turn > 0:
        n = max(1, math.ceil(2 * turn / FUNNEL_ANGLE_STEP))
        turned = [rotate(hull, -turn + 2 * turn * i / n, origin=key_axis())
                  for i in range(n + 1)]
        hull = unary_union([unary_union(pair).convex_hull
                            for pair in zip(turned, turned[1:])]).simplify(SWEEP_TOLERANCE)
        return hull.intersection(insert_profile().buffer(-p.MIN_PRINT_WALL,
                                                         p.ARC_QUAD_SEGMENTS))
    return hull.intersection(insert_profile().buffer(-p.INSERT_WALL, p.ARC_QUAD_SEGMENTS))


def bore_pieces(name: str) -> list[tuple[float, float, BaseGeometry]]:
    """(x0, x1, YZ section) of the bore for a tip or the iron, split at
    INSERT_SPLIT_X; the end pieces run on to the cavity ends.

    An item slides into each insert from its split face, so at every depth
    the bore holds whatever passes it on the way in: every piece deeper in
    that insert, and — ITEM_CLEARANCE along the axis too — every piece up to
    ITEM_CLEARANCE shallower. So every step in a bore lies ITEM_CLEARANCE
    deeper than the item's shoulder above it (a tip settles that much onto
    its collar seat), and nothing is clamped end to end."""
    base_steps = 0 if name == "iron" else len(p.TIP_BASE_STEPS)
    items = [(x0, x1, s.buffer(p.TIP_BASE_CLEARANCE if i < base_steps else p.ITEM_CLEARANCE,
                               p.ARC_QUAD_SEGMENTS))
             for i, (x0, x1, s) in enumerate(pieces(name, keep_out=True))]
    first, last = items[0], items[-1]
    items[0] = (p.CAVITY_START_X, first[1], first[2])
    items[-1] = (last[0], min(last[1] + p.ITEM_END_CLEARANCE, p.CAVITY_END_X), last[2])
    split, c, eps = p.INSERT_SPLIT_X, p.ITEM_CLEARANCE, 1e-9
    out = []
    # insert A, deeper = lower x: at x the bore takes pieces starting before x + c
    cuts = sorted({p.CAVITY_START_X, split}
                  | {x0 - c for x0, _, _ in items if p.CAVITY_START_X < x0 - c < split})
    for a, b in zip(cuts, cuts[1:]):
        out.append((a, b, unary_union([s for x0, x1, s in items
                                       if x0 < split and x0 - c < b - eps])))
    # insert B, deeper = higher x: at x the bore takes pieces ending after x - c
    end = items[-1][1]
    cuts = sorted({split, end} | {x1 + c for _, x1, _ in items if split < x1 + c < end})
    for a, b in zip(cuts, cuts[1:]):
        out.append((a, b, unary_union([s for x0, x1, s in items
                                       if x1 > split and x1 + c > a + eps])))
    return out


def bore(name: str) -> Part:
    return Part() + [extrude_x(s, x0, x1) for x0, x1, s in bore_pieces(name)]


def _other_cuts_at(x: float) -> BaseGeometry:
    """YZ section of every cut at ``x`` except the short-leg pocket."""
    out = [s for n in ("iron", *TIP_NAMES) for x0, x1, s in bore_pieces(n) if x0 <= x < x1]
    if p.KEY_LONG_X0 - p.ITEM_END_CLEARANCE <= x < p.KEY_SHORT_X1:
        out.append(channel_sections()["key"])
    return unary_union(out)


def _shave(pocket: BaseGeometry, others: BaseGeometry) -> BaseGeometry:
    """``pocket`` plus every bit of PETG next to it narrower than two print
    lines (sharp spikes left between pocket, funnel and other channels).
    Those bits are exactly what closing the cuts (grow, then shrink by one
    print line) fills in, so one pass is enough. Outside the insert is never
    cut, so the outer wall stays."""
    cut = pocket.union(others)
    r = p.MIN_PRINT_WALL
    closed = cut.buffer(r, p.ARC_QUAD_SEGMENTS).buffer(-r, p.ARC_QUAD_SEGMENTS)
    thin = closed.difference(cut)
    spikes = [g for g in getattr(thin, "geoms", [thin])
              if not g.is_empty and g.distance(pocket) < SLIVER_TOUCH]
    if not spikes:
        return pocket
    # reach a little into the neighbouring cuts (never into PETG), so no
    # razor-thin remnants are left where outlines nearly coincide
    grown = unary_union(spikes).buffer(SLIVER_OVERLAP).intersection(closed)
    return pocket.union(grown)


def pocket_slices() -> list[tuple[float, float, BaseGeometry]]:
    """(x0, x1, YZ section) of the short-leg pocket in insert B: the funnel at
    its mouth (KEY_FUNNEL_ANGLE at B's face down to 0 at KEY_FUNNEL_DEPTH, in
    TAPER_STEP slices at their wider, mouth-side angle), then the plain
    pocket; each slice shaved of thin PETG next to it."""
    start, end = p.INSERT_SPLIT_X, p.KEY_SHORT_X1 + p.POCKET_CLEARANCE
    n = max(1, math.ceil(p.KEY_FUNNEL_DEPTH / p.TAPER_STEP))
    cuts = {start + i * p.KEY_FUNNEL_DEPTH / n for i in range(n + 1)}
    cuts |= {x for name in ("iron", *TIP_NAMES) for piece in bore_pieces(name)
             for x in piece[:2]}
    cuts |= {p.KEY_SHORT_X1, end}
    cuts = sorted(x for x in cuts if start <= x <= end)
    out = []
    for x0, x1 in zip(cuts, cuts[1:]):
        depth = x0 - start
        turn = p.KEY_FUNNEL_ANGLE * max(0.0, 1 - depth / p.KEY_FUNNEL_DEPTH)
        out.append((x0, x1, _shave(pocket_section(turn), _other_cuts_at((x0 + x1) / 2))))
    return out


@cache
def channel_cuts() -> Part:
    """Everything cut out of the insert for the contents: item channels, key
    hole and the short-leg pocket."""
    ch = channel_sections()
    cuts = bore("iron")
    for name in TIP_NAMES:
        cuts += bore(name)
    cuts += extrude_x(ch["key"], p.KEY_LONG_X0 - p.ITEM_END_CLEARANCE, p.KEY_SHORT_X1)
    cuts += Part() + [extrude_x(s, x0, x1) for x0, x1, s in pocket_slices()]
    # Where the band bends round the insert's ends its channel cuts diagonally
    # past the square channel ends; round those ends off so INSERT_WALL of
    # PETG always stays between band and items.
    near_band = extrude_y(ring_section().buffer(p.INSERT_WALL, p.ARC_QUAD_SEGMENTS),
                          BAND_HALF_WIDTH + p.INSERT_WALL)
    return cuts - near_band


@cache
def insert_solid() -> Part:
    """The whole insert, before splitting."""
    body = extrude_x(insert_profile(), p.INSERT_START_X, p.INSERT_END_X)
    return body - ring_solid() - channel_cuts()


def key_align_groove() -> Part:
    """Shallow groove in insert A's face from the key hole along the short
    leg (as long as the leg), showing how to line the leg up; it may run
    through other channels."""
    face = p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP
    section = key_short_leg_line().buffer(p.KEY_ALIGN_GROOVE_WIDTH / 2, cap_style="flat")
    return extrude_x(section, face - p.KEY_ALIGN_GROOVE_DEPTH, face + 1)


def magnet_holes_a() -> Part:
    face = p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP
    return extrude_x(magnet_section(), face - p.MAGNET_THICKNESS - p.MAGNET_CLEARANCE, face + 1)


def magnet_holes_b() -> Part:
    face = p.INSERT_SPLIT_X
    return extrude_x(magnet_section(), face - 1, face + p.MAGNET_THICKNESS + p.MAGNET_CLEARANCE)


def edge_chamfer(face: float, size: float, inward: int) -> Part:
    """Cutter for a 45° chamfer of ``size`` round the insert's outer edge at
    the end face ``face``; ``inward`` points from the face into the insert."""
    return chamfer_cutter(insert_profile(), face, size, inward, p.TAPER_STEP,
                          resolution=p.ARC_QUAD_SEGMENTS)


@cache
def insert_a() -> Part:
    """Insert A stops INSERT_SPLIT_GAP short of insert B, so the shells
    always close first. Its face carries the key alignment groove and the
    magnet holes; chamfered on the face it prints on and on its split face
    (lead-in for shell B)."""
    face = p.INSERT_SPLIT_X - p.INSERT_SPLIT_GAP
    return ((insert_solid() & below_x(face))
            - key_align_groove() - magnet_holes_a()
            - edge_chamfer(p.INSERT_START_X, p.INSERT_BED_CHAMFER, +1)
            - edge_chamfer(face, p.INSERT_A_LEAD_IN, -1))


@cache
def insert_b() -> Part:
    """Its face carries the magnet holes opposite insert A's; chamfered on
    the face it prints on (its outer end)."""
    return (insert_solid() - below_x(p.INSERT_SPLIT_X) - magnet_holes_b()
            - edge_chamfer(p.INSERT_END_X, p.INSERT_BED_CHAMFER, -1))
