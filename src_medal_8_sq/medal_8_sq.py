"""Root assembly for the 8-medal (2 rows x 4 columns) square-outer-corner walnut display frame."""

import build123d as bd
from cad import model

from acrylic_cover import acrylic_cover
from backboard import backboard
from frame_moulding import hardwood_frame
from hardware import rear_hardware
from lib.dims import FRAME_OUTER_H, FRAME_OUTER_W
from medals import medal_set
from mid_board import mid_board
from spacers import front_spacer


@model
def medal_8_sq():
    """Complete 8-medal (2x4) display frame assembly with 90-degree outer corners."""
    frame = hardwood_frame().shape
    acrylic = acrylic_cover().shape
    f_spacer = front_spacer().shape
    medals = medal_set().shape
    mid = mid_board().shape
    back = backboard().shape
    hw = rear_hardware().shape

    asm = bd.Compound(
        children=[
            frame,
            acrylic,
            f_spacer,
            medals,
            mid,
            back,
            hw,
        ],
        label="medal_8_sq",
    )
    bb = asm.bounding_box()
    assert abs(bb.size.X - FRAME_OUTER_W) < 1e-4, bb.size
    assert abs(bb.size.Z - FRAME_OUTER_H) < 1e-4, bb.size
    return asm


if __name__ == "__main__":
    medal_8_sq()

