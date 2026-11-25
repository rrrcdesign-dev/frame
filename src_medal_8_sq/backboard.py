"""Two-layer 15 mm removable backboard: 4 mm inner plywood + 11 x 15 mm outer pinewood perimeter frame."""

import build123d as bd
from cad import model

from lib.dims import (
    BACKBOARD_FRAME_T,
    BACKBOARD_FRAME_W,
    BACKBOARD_H,
    BACKBOARD_PLY_T,
    BACKBOARD_T,
    BACKBOARD_W,
    FRAME_OUTER_H,
    SHEET_CORNER_R,
    Y_BACKBOARD_FRAME_START,
    Y_BACKBOARD_START,
)
from lib.materials import apply_backboard_pine, apply_backboard_plywood


@model
def backboard():
    """15 mm two-layer bonded backboard (4 mm plywood inner sheet + 11 mm x 15 mm pinewood rear frame)."""
    z_center = FRAME_OUTER_H / 2.0

    # Inner 4 mm plywood sheet (Y = 31.0 .. 35.0 mm)
    ply_plane = bd.Plane(origin=(0.0, Y_BACKBOARD_START, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as ply_part:
        with bd.BuildSketch(ply_plane):
            with bd.Locations((0.0, z_center)):
                if SHEET_CORNER_R > 0.0:
                    bd.RectangleRounded(BACKBOARD_W, BACKBOARD_H, SHEET_CORNER_R)
                else:
                    bd.Rectangle(BACKBOARD_W, BACKBOARD_H)
        bd.extrude(amount=-BACKBOARD_PLY_T)
    plywood = ply_part.part
    plywood.label = "backboard_plywood"
    apply_backboard_plywood(plywood)

    # Outer 11 mm deep x 15 mm wide pinewood perimeter frame (Y = 35.0 .. 46.0 mm)
    vert_len = BACKBOARD_H - 2.0 * BACKBOARD_FRAME_W
    top_stick = bd.Pos(0.0, Y_BACKBOARD_FRAME_START, z_center + BACKBOARD_H / 2.0 - BACKBOARD_FRAME_W / 2.0) * bd.Box(
        BACKBOARD_W, BACKBOARD_FRAME_T, BACKBOARD_FRAME_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    bottom_stick = bd.Pos(0.0, Y_BACKBOARD_FRAME_START, z_center - BACKBOARD_H / 2.0 + BACKBOARD_FRAME_W / 2.0) * bd.Box(
        BACKBOARD_W, BACKBOARD_FRAME_T, BACKBOARD_FRAME_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    left_stick = bd.Pos(-BACKBOARD_W / 2.0 + BACKBOARD_FRAME_W / 2.0, Y_BACKBOARD_FRAME_START, z_center) * bd.Box(
        BACKBOARD_FRAME_W, BACKBOARD_FRAME_T, vert_len, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    right_stick = bd.Pos(BACKBOARD_W / 2.0 - BACKBOARD_FRAME_W / 2.0, Y_BACKBOARD_FRAME_START, z_center) * bd.Box(
        BACKBOARD_FRAME_W, BACKBOARD_FRAME_T, vert_len, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )

    if SHEET_CORNER_R > 0.0:
        frame_plane = bd.Plane(origin=(0.0, Y_BACKBOARD_FRAME_START, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        with bd.BuildPart() as env_part:
            with bd.BuildSketch(frame_plane):
                with bd.Locations((0.0, z_center)):
                    bd.RectangleRounded(BACKBOARD_W, BACKBOARD_H, SHEET_CORNER_R)
            bd.extrude(amount=-BACKBOARD_FRAME_T)
        top_stick = top_stick & env_part.part
        bottom_stick = bottom_stick & env_part.part

    sticks = [
        (top_stick, "backboard_pine_top"),
        (bottom_stick, "backboard_pine_bottom"),
        (left_stick, "backboard_pine_left"),
        (right_stick, "backboard_pine_right"),
    ]
    for stick, name in sticks:
        stick.label = name
        apply_backboard_pine(stick)

    pine_frame = bd.Compound(children=[stick for stick, _ in sticks], label="backboard_pine_frame")
    asm = bd.Compound(children=[plywood, pine_frame], label="backboard")
    bb = asm.bounding_box()
    assert abs(bb.size.X - BACKBOARD_W) < 1e-4, bb.size
    assert abs(bb.size.Y - BACKBOARD_T) < 1e-4, bb.size
    assert abs(bb.size.Z - BACKBOARD_H) < 1e-4, bb.size
    return asm


if __name__ == "__main__":
    backboard()
