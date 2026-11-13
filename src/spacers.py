"""Front and rear MDF spacer frames inside the frame cavity."""

import build123d as bd
from cad import model

from lib.dims import (
    FRAME_OUTER_H,
    FRONT_SPACER_T,
    REAR_SPACER_T,
    SHEET_CORNER_R,
    SHEET_H,
    SHEET_W,
    SPACER_WALL_W,
    Y_FRONT_SPACER_START,
    Y_REAR_SPACER_START,
)
from lib.materials import apply_spacer_mdf


def spacer_frame_body(thickness: float, y_start: float, label_prefix: str) -> bd.Compound:
    """Build a 4-bar butt-jointed spacer perimeter with outer corner radii clearing the rabbet."""
    z_center = FRAME_OUTER_H / 2.0
    side_len = SHEET_H - 2.0 * SPACER_WALL_W
    # Keep top/bottom spacer bars slightly shorter than full width at corners if needed, or trim with outer rounded envelope
    plane = bd.Plane(origin=(0.0, y_start, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as env_part:
        with bd.BuildSketch(plane):
            with bd.Locations((0.0, z_center)):
                bd.RectangleRounded(SHEET_W, SHEET_H, SHEET_CORNER_R)
        bd.extrude(amount=-thickness)
    envelope = env_part.part

    top_bar = (
        bd.Pos(0.0, y_start, z_center + SHEET_H / 2.0 - SPACER_WALL_W / 2.0)
        * bd.Box(SHEET_W, thickness, SPACER_WALL_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER))
    ) & envelope
    bottom_bar = (
        bd.Pos(0.0, y_start, z_center - SHEET_H / 2.0 + SPACER_WALL_W / 2.0)
        * bd.Box(SHEET_W, thickness, SPACER_WALL_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER))
    ) & envelope
    left_bar = bd.Pos(-SHEET_W / 2.0 + SPACER_WALL_W / 2.0, y_start, z_center) * bd.Box(
        SPACER_WALL_W, thickness, side_len, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    right_bar = bd.Pos(SHEET_W / 2.0 - SPACER_WALL_W / 2.0, y_start, z_center) * bd.Box(
        SPACER_WALL_W, thickness, side_len, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )

    bars = [
        (top_bar, f"{label_prefix}_top"),
        (bottom_bar, f"{label_prefix}_bottom"),
        (left_bar, f"{label_prefix}_left"),
        (right_bar, f"{label_prefix}_right"),
    ]
    for bar, name in bars:
        bar.label = name
        apply_spacer_mdf(bar)
    return bd.Compound(children=[bar for bar, _ in bars], label=label_prefix)


@model
def front_spacer():
    """10 mm front spacer creating clearance between the acrylic cover and medals."""
    return spacer_frame_body(FRONT_SPACER_T, Y_FRONT_SPACER_START, "front_spacer")


@model
def rear_spacer():
    """12 mm rear spacer creating cavity behind the mid-board for excess medal ribbons."""
    return spacer_frame_body(REAR_SPACER_T, Y_REAR_SPACER_START, "rear_spacer")


if __name__ == "__main__":
    front_spacer()
    rear_spacer()
