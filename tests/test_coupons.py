"""Test-print coupons: real slices, on the bed, printable."""

import pytest

from cad import params as p
from cad.coupons import coupons, slice_part

COUPONS = {c.stem: c for c in coupons()}


@pytest.mark.parametrize("stem", COUPONS)
def test_coupon_is_a_valid_slice_on_the_bed(stem):
    c = COUPONS[stem]
    part = slice_part(c)
    assert part.is_valid
    assert part.volume > 0
    bb = part.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    assert bb.size.Z == pytest.approx(c.x1 - c.x0, abs=1e-6)
    assert max(bb.size.X, bb.size.Y) <= p.PRINT_BED
