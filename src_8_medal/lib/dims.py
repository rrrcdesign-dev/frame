"""Parametric dimensions and coordinate formulas for the 8-medal (2x4) display frame.

Coordinate convention:
  - X: horizontal left (-X) to right (+X), centered at 0
  - Y: depth front (0.0) to back (+FRAME_DEPTH)
  - Z: vertical bottom (0.0) to top (+FRAME_OUTER_H)
"""

# Grid & medal geometry
MEDAL_ROWS = 2
MEDAL_COLS = 4
MEDAL_DIAMETER = 73.0
MEDAL_RADIUS = MEDAL_DIAMETER / 2.0
MEDAL_THICKNESS = 5.0
MEDAL_RIM_WIDTH = 3.2
MEDAL_RECESS_DEPTH = 0.8
MEDAL_BAIL_WIDTH = 10.0
MEDAL_BAIL_HEIGHT = 3.5
MEDAL_BAIL_THICKNESS = 2.4

# Ribbon & mid-board slot geometry
RIBBON_WIDTH = 25.0
RIBBON_THICKNESS = 1.2
RIBBON_VISIBLE_H = 15.0
RIBBON_TAIL_H = 48.0
SLOT_WIDTH = RIBBON_WIDTH + 3.0
SLOT_HEIGHT = 3.0
SLOT_CORNER_R = 1.0

# Spacing & outer padding inside the visible frame opening
MEDAL_GAP_X = 14.0
MEDAL_GAP_Z = 14.0
FRAME_PADDING = 25.0

COL_PITCH = MEDAL_DIAMETER + MEDAL_GAP_X
MEDAL_UNIT_H = MEDAL_DIAMETER + RIBBON_VISIBLE_H + SLOT_HEIGHT
ROW_PITCH = MEDAL_UNIT_H + MEDAL_GAP_Z

OPEN_W = MEDAL_COLS * MEDAL_DIAMETER + (MEDAL_COLS - 1) * MEDAL_GAP_X + 2.0 * FRAME_PADDING
OPEN_H = MEDAL_ROWS * MEDAL_UNIT_H + (MEDAL_ROWS - 1) * MEDAL_GAP_Z + 2.0 * FRAME_PADDING

# Hardwood moulding & rabbet geometry
# 28 mm total front face width = 16 mm outer hardwood wall + 6 mm spacer (22 mm) + 6 mm lip overhang
FRAME_FACE_W = 28.0
FRAME_WALL_W = 16.0
SPACER_WALL_W = 6.0
LIP_DEPTH = 9.0
FRAME_OUTER_CORNER_R = 20.0
FRAME_INNER_CORNER_R = 6.0
FRAME_OUTER_FRONT_FILLET = 13.5
CAVITY_CORNER_R = 6.0
SHEET_CORNER_R = 7.0

# Corner spline joinery (2 slot inserts per mitred corner)
SPLINE_THICKNESS = 3.2
SPLINE_DEPTH = 17.0  # measured inward along 45-deg diagonal from sharp corner
SPLINE_YS = (16.5, 30.0)

# Stack thicknesses (front to back)
ACRYLIC_T = 1.5
FRONT_SPACER_T = 15.0
MID_BOARD_T = 3.0
REAR_SPACER_T = 5.0
BACKBOARD_T = 3.0
BACKBOARD_REAR_INSET = 3.0  # recess backboard 3 mm inward from back face of frame

FRAME_DEPTH = LIP_DEPTH + ACRYLIC_T + FRONT_SPACER_T + MID_BOARD_T + REAR_SPACER_T + BACKBOARD_T + BACKBOARD_REAR_INSET

FRAME_OUTER_W = OPEN_W + 2.0 * FRAME_FACE_W
FRAME_OUTER_H = OPEN_H + 2.0 * FRAME_FACE_W

CAVITY_W = FRAME_OUTER_W - 2.0 * FRAME_WALL_W
CAVITY_H = FRAME_OUTER_H - 2.0 * FRAME_WALL_W

SHEET_CLEARANCE = 0.2
SHEET_W = CAVITY_W - 2.0 * SHEET_CLEARANCE
SHEET_H = CAVITY_H - 2.0 * SHEET_CLEARANCE

BACKBOARD_CLEARANCE = 0.3
BACKBOARD_W = CAVITY_W - 2.0 * BACKBOARD_CLEARANCE
BACKBOARD_H = CAVITY_H - 2.0 * BACKBOARD_CLEARANCE

# Stack Y coordinates (front = 0.0, back = FRAME_DEPTH)
Y_FRONT = 0.0
Y_ACRYLIC_START = LIP_DEPTH
Y_ACRYLIC_END = Y_ACRYLIC_START + ACRYLIC_T
Y_FRONT_SPACER_START = Y_ACRYLIC_END
Y_FRONT_SPACER_END = Y_FRONT_SPACER_START + FRONT_SPACER_T
Y_MID_BOARD_START = Y_FRONT_SPACER_END
Y_MID_BOARD_END = Y_MID_BOARD_START + MID_BOARD_T
Y_REAR_SPACER_START = Y_MID_BOARD_END
Y_REAR_SPACER_END = Y_REAR_SPACER_START + REAR_SPACER_T
Y_BACKBOARD_START = Y_REAR_SPACER_END
Y_BACKBOARD_END = Y_BACKBOARD_START + BACKBOARD_T
Y_KERF_START = Y_BACKBOARD_END
Y_BACK = FRAME_DEPTH

# Internal frame locking kerf (receives backboard-mounted turn locks)
KERF_DEPTH = 4.0
KERF_H = 1.5

# Turn locks & D-ring hangers mounted on the recessed backboard
TURN_BUTTON_LEN = 21.0
TURN_BUTTON_W = 9.0
TURN_BUTTON_T = 1.2
TURN_LOCK_EDGE_INSET = 18.0  # pivot inset inward from backboard edge (3.0 mm tip reach into 4.0 mm kerf)
HANGER_BACKBOARD_INSET = 22.0  # D-ring strap center inset inward from backboard left/right edge

TURN_BUTTON_TOP_BOTTOM_XS = (-110.0, 110.0)
TURN_BUTTON_SIDE_ZS = (FRAME_OUTER_H / 2.0,)
HANGER_Z = FRAME_OUTER_H * (2.0 / 3.0)  # top third


def medal_center(row: int, col: int) -> tuple[float, float]:
    """Return (x, z) center of a medal in 0-indexed (bottom-to-top row, left-to-right col)."""
    x = (col - (MEDAL_COLS - 1) / 2.0) * COL_PITCH
    z_open_bottom = FRAME_FACE_W
    z_first_medal_center = z_open_bottom + FRAME_PADDING + MEDAL_RADIUS
    z = z_first_medal_center + row * ROW_PITCH
    return x, z


def slot_center(row: int, col: int) -> tuple[float, float]:
    """Return (x, z) center of the horizontal ribbon slot above the medal."""
    x, z_medal = medal_center(row, col)
    z_slot = z_medal + MEDAL_RADIUS + RIBBON_VISIBLE_H + SLOT_HEIGHT / 2.0
    return x, z_slot


def all_medal_positions() -> list[tuple[int, int, float, float]]:
    """Return [(row, col, x, z), ...] for all 12 medals."""
    positions: list[tuple[int, int, float, float]] = []
    for row in range(MEDAL_ROWS):
        for col in range(MEDAL_COLS):
            x, z = medal_center(row, col)
            positions.append((row, col, x, z))
    return positions

