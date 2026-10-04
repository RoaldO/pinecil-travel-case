"""Single source of truth for every dimension (mm)."""

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
