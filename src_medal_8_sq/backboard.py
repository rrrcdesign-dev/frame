"""15 mm removable MDF backboard flush with the back face of the frame."""

import build123d as bd
from cad import model

from lib.dims import BACKBOARD_H, BACKBOARD_T, BACKBOARD_W, FRAME_OUTER_H, SHEET_CORNER_R, Y_BACKBOARD_START
from lib.materials import apply_backboard_mdf


@model
def backboard():
    """3 mm MDF backboard recessed behind the 1.5 mm locking kerf and 3.0 mm solid back lip."""
    plane = bd.Plane(origin=(0.0, Y_BACKBOARD_START, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as part:
        with bd.BuildSketch(plane):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                if SHEET_CORNER_R > 0.0:
                    bd.RectangleRounded(BACKBOARD_W, BACKBOARD_H, SHEET_CORNER_R)
                else:
                    bd.Rectangle(BACKBOARD_W, BACKBOARD_H)
        bd.extrude(amount=-BACKBOARD_T)
    board = part.part
    board.label = "backboard"
    apply_backboard_mdf(board)
    return board


if __name__ == "__main__":
    backboard()
