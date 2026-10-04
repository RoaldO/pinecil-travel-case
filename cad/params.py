"""Single source of truth for every dimension (mm)."""

import math

# --- Pinecil logo (pinecone) -------------------------------------------------

# Hard upper bound for the logo: neither its width nor its height may exceed
# this. The logo is scaled uniformly so its largest side equals this value.
LOGO_MAX_SIZE = 19.0

# Width of the ribs between the pinecone pieces. In the original artwork the
# gaps are 0.71-0.74 mm at a 19 mm logo. Ribs are cut along the rib
# centrelines, so a value below the original gap has no effect (the ribs never
# get thinner than in the artwork); a larger value widens them inward, the
# logo's outer outline stays put.
RIB_WIDTH = 0.8

# --- Logo test plate ---------------------------------------------------------

# Standalone plate with the logo as through-holes, for test prints until the
# travel case itself exists.
PLATE_THICKNESS = 2.0
PLATE_MARGIN = 3.0  # plate edge to logo bounding box, each side

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
