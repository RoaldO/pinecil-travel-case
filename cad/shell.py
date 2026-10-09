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
from cad.pinecil_logo import logo_cutter
from cad.profile import insert_cavity, shell_profile
from cad.solids import below_x, chamfer_cutter, extrude_x

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
    # each insert glued into its own half; in the overlap insert A slides in
    # shell B — three stretches, so either clearance can be the smaller one
    glue = insert_cavity(p.GLUE_CLEARANCE)
    body -= extrude_x(glue, p.END_CAP_THICKNESS, p.SHELL_SPLIT_X)
    body -= extrude_x(insert_cavity(p.SLIDE_CLEARANCE), p.SHELL_SPLIT_X, p.INSERT_SPLIT_X)
    body -= extrude_x(glue, p.INSERT_SPLIT_X, p.CASE_LENGTH - p.END_CAP_THICKNESS)
    body -= ring_solid()
    return body


@cache
def shell_a() -> Part:
    return shell_solid() & below_x(p.SHELL_SPLIT_X)


@cache
def shell_b() -> Part:
    """With the logo through its end cap and a chamfer round the inside of
    its mouth, the lead-in for sliding it over insert A."""
    cutter = logo_plane() * logo_cutter(p.END_CAP_THICKNESS + 2 * LOGO_CUT_OVERRUN)
    mouth = chamfer_cutter(insert_cavity(p.SLIDE_CLEARANCE), p.SHELL_SPLIT_X,
                           p.SHELL_B_MOUTH_CHAMFER, +1, p.TAPER_STEP, hole=True,
                           resolution=p.ARC_QUAD_SEGMENTS)
    return shell_solid() - below_x(p.SHELL_SPLIT_X) - cutter - mouth
