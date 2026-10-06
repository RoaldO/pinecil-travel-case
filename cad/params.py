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

# The handle's cross-section is a "tombstone": a half cylinder round the tip
# axis, with a block as wide as its diameter on its flat side and that
# block's far corners rounded. It lies round side down, so the flat face with
# the display and the buttons faces up. The handle's base lies deep in insert
# A, the tip points into insert B. Sections are (diameter, total height,
# corner radius).
IRON_HANDLE_LENGTH = 103.3  # base to where the tip comes out
# The iron carries a tip like the spares, pointing the same way: its base
# (white rings) inside the handle, the collar right against the handle's
# front. IRON_LENGTH (derived below) is with the longest tip; measured 159
# with an 89.3 tip.
IRON_BODY_SECTION = (13.9, 16.85, 2.0)  # hard plastic, the whole handle long
# The rubber grip sits over the body (which runs on underneath it, so there
# the iron is body and grip together): from / length along the handle, measured
# from the base.
IRON_GRIP_FROM = 63.8
IRON_GRIP_LENGTH = 30.0
IRON_GRIP_SECTION = (14.6, 17.5, 4.0)
# Screw on the flat face, centred across it; its head sticks out.
IRON_SCREW_AT = 14.7  # head centre, from the handle's base
IRON_SCREW_HEAD_DIAMETER = 3.4
IRON_SCREW_HEAD_HEIGHT = 1.1
# Mounting screw on the flat face (holds the tip), centred; its head sticks out.
IRON_MOUNT_SCREW_AT = 98.5  # head centre, from the handle's base
IRON_MOUNT_SCREW_HEAD_DIAMETER = 6.0
IRON_MOUNT_SCREW_HEAD_HEIGHT = 2.8
# Foot under the round side, opposite the mounting screw, so the iron lies
# steady on a table: there the lower half is a half square (as wide as the
# body's half cylinder, as deep as its radius) instead of a half circle.
IRON_FOOT_FROM = 98.4  # from the handle's base
IRON_FOOT_TO = 102.0
IRON_FOOT_CORNER_RADIUS = 1.0
# Two buttons on the flat face, centred across it, centres from the base.
IRON_BUTTONS_AT = (23.15, 60.6)
IRON_BUTTON_DIAMETER = 4.9
IRON_BUTTON_HEIGHT = 0.7  # sticks out of the flat face
# Display on the flat face, centred across it, flush (sticks out 0).
IRON_DISPLAY_FROM = 19.0  # from the base
IRON_DISPLAY_TO = 55.0
IRON_DISPLAY_WIDTH = 9.55
# Extra room round the buttons and the display, on top of ITEM_CLEARANCE, so
# an iron rattling in its channel never taps them against the wall.
IRON_CONTROL_CLEARANCE = 1.0
# Past the handle the iron carries a tip; its widest part there is the
# heating-element sleeve (TIP_SLEEVE_DIAMETER).

TIP_LENGTH = 92.0  # longest measured 89.3 (they vary), with margin
TIP_DIAMETER = 11.0  # widest, measured: the collar
# The tip's base (the end with the white rings), measured from that end, as
# (length, diameter) — narrowest first. Then the collar (TIP_DIAMETER). The
# base sits deep in insert A, so you can see which tip is which on opening;
# the channel only widens toward its mouth, so a tip slides in and out.
TIP_BASE_STEPS = ((24.1, 5.4), (9.7, 5.7))
TIP_COLLAR_LENGTH = 4.0  # estimated (chamfered, hard to measure); not critical
# Past the collar the widest part is the sleeve round the heating element;
# everything up to the working end fits inside this diameter, so insert B
# holds the tip in one straight bore of it.
TIP_SLEEVE_DIAMETER = 5.5
TIP_COLLAR_MIN_DEPTH = 6.0  # min length of the collar-wide channel in insert A

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
POCKET_CLEARANCE = 1.0  # pocket in insert B around the short leg

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

TIP_BASE_LENGTH = sum(length for length, _ in TIP_BASE_STEPS)  # base end -> collar
IRON_LENGTH = IRON_HANDLE_LENGTH + TIP_LENGTH - TIP_BASE_LENGTH
CAVITY_LENGTH = IRON_LENGTH + 2 * ITEM_END_CLEARANCE
CAVITY_START_X = END_CAP_THICKNESS + RING_END + INSERT_END_WALL
CAVITY_END_X = CAVITY_START_X + CAVITY_LENGTH
CASE_LENGTH = CAVITY_END_X + INSERT_END_WALL + RING_END + END_CAP_THICKNESS

ITEM_START_X = CAVITY_START_X + ITEM_END_CLEARANCE  # iron and all tips start here
TIP_END_X = ITEM_START_X + TIP_LENGTH
TIP_COLLAR_X = ITEM_START_X + TIP_BASE_LENGTH  # rests here
INSERT_SPLIT_X = TIP_END_X - TIP_GRIP
SHELL_SPLIT_X = INSERT_SPLIT_X - OVERLAP

KEY_SHORT_X0 = TIP_END_X + ITEM_CLEARANCE  # short leg, side facing half A
KEY_SHORT_X1 = KEY_SHORT_X0 + KEY_HEX
KEY_LONG_X0 = KEY_SHORT_X1 - KEY_LONG_LEG  # long leg runs back into insert A

# --- Modelling resolution -------------------------------------------------------

# Line segments per quarter circle for every round 2D shape. 16 -> a 64-gon:
# max deviation r * (1 - cos(pi/64)) ≈ 0.007 mm at r = 5.5. Higher = slower.
ARC_QUAD_SEGMENTS = 16
