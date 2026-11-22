"""Clear 2.0 mm PMMA acrylic cover seated behind the front rabbet lip."""

import build123d as bd
from cad import model

from lib.dims import ACRYLIC_T, FRAME_OUTER_H, SHEET_CORNER_R, SHEET_H, SHEET_W, Y_ACRYLIC_START
from lib.materials import apply_acrylic


@model
def acrylic_cover():
    """1.5 mm clear acrylic sheet with corner radius clearing the routed rabbet."""
    plane = bd.Plane(origin=(0.0, Y_ACRYLIC_START, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as part:
        with bd.BuildSketch(plane):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                if SHEET_CORNER_R > 0.0:
                    bd.RectangleRounded(SHEET_W, SHEET_H, SHEET_CORNER_R)
                else:
                    bd.Rectangle(SHEET_W, SHEET_H)
        bd.extrude(amount=-ACRYLIC_T)
    sheet = part.part
    sheet.label = "acrylic_cover"
    apply_acrylic(sheet)
    return sheet


if __name__ == "__main__":
    acrylic_cover()
