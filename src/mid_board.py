"""3 mm walnut-veneered plywood mid-board with 12 horizontal slots for medal ribbons."""

import build123d as bd
from cad import model

from lib.dims import (
    FRAME_OUTER_H,
    MEDAL_COLS,
    MEDAL_ROWS,
    MID_BOARD_T,
    SHEET_CORNER_R,
    SHEET_H,
    SHEET_W,
    SLOT_CORNER_R,
    SLOT_HEIGHT,
    SLOT_WIDTH,
    Y_MID_BOARD_START,
    slot_center,
)
from lib.materials import apply_veneer_plywood


@model
def mid_board():
    """3 mm walnut-veneered plywood backing plate with 12 horizontal ribbon pass-through slots."""
    board_plane = bd.Plane(origin=(0.0, Y_MID_BOARD_START, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as part:
        with bd.BuildSketch(board_plane):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                bd.RectangleRounded(SHEET_W, SHEET_H, SHEET_CORNER_R)
            for row in range(MEDAL_ROWS):
                for col in range(MEDAL_COLS):
                    x, z = slot_center(row, col)
                    with bd.Locations((x, z)):
                        bd.RectangleRounded(SLOT_WIDTH, SLOT_HEIGHT, SLOT_CORNER_R, mode=bd.Mode.SUBTRACT)
        bd.extrude(amount=-MID_BOARD_T)

    board = part.part
    board.label = "mid_board"
    apply_veneer_plywood(board)
    return board


if __name__ == "__main__":
    mid_board()
