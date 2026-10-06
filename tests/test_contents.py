"""Item layout in the cross-section (spec criterion 3, 2D part)."""

import itertools

import pytest

from cad import params as p
from cad.contents import ITEM_GAP, key_short_leg_section, layout, pieces


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
    """...the iron pieces it lies beside (key and iron don't move relative to
    each other: both stay in half A's frame)."""
    leg = key_short_leg_section(0)
    beside = [s for x0, x1, s in pieces("iron") if x0 < p.KEY_SHORT_X1 and x1 > p.KEY_SHORT_X0]
    assert beside
    for section in beside:
        assert leg.distance(section) >= 2 * p.ITEM_CLEARANCE
