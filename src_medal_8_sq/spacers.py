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


def _square_butt_spacer_frame(thickness: float, y_start: float, label_prefix: str) -> bd.Compound:
    """Build 4 square-cut butt-jointed spacer bars: 2 full-length side bars and 2 shorter top/bottom bars."""
    z_center = FRAME_OUTER_H / 2.0
    horiz_len = SHEET_W - 2.0 * SPACER_WALL_W
    top_bar = bd.Pos(0.0, y_start, z_center + SHEET_H / 2.0 - SPACER_WALL_W / 2.0) * bd.Box(
        horiz_len, thickness, SPACER_WALL_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    bottom_bar = bd.Pos(0.0, y_start, z_center - SHEET_H / 2.0 + SPACER_WALL_W / 2.0) * bd.Box(
        horiz_len, thickness, SPACER_WALL_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    left_bar = bd.Pos(-SHEET_W / 2.0 + SPACER_WALL_W / 2.0, y_start, z_center) * bd.Box(
        SPACER_WALL_W, thickness, SHEET_H, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    right_bar = bd.Pos(SHEET_W / 2.0 - SPACER_WALL_W / 2.0, y_start, z_center) * bd.Box(
        SPACER_WALL_W, thickness, SHEET_H, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    if SHEET_CORNER_R > 0.0:
        plane = bd.Plane(origin=(0.0, y_start, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        with bd.BuildPart() as env_part:
            with bd.BuildSketch(plane):
                with bd.Locations((0.0, z_center)):
                    bd.RectangleRounded(SHEET_W, SHEET_H, SHEET_CORNER_R)
            bd.extrude(amount=-thickness)
        left_bar = left_bar & env_part.part
        right_bar = right_bar & env_part.part

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


def _straight_strip_spacer(thickness: float, y_start: float, label_prefix: str, corner_clear: float = 10.0) -> bd.Compound:
    """Build 4 straight square-cut spacer strips cut short of the corners (no CNC corner rounding)."""
    z_center = FRAME_OUTER_H / 2.0
    horiz_len = SHEET_W - 2.0 * corner_clear
    vert_len = SHEET_H - 2.0 * corner_clear

    top_bar = bd.Pos(0.0, y_start, z_center + SHEET_H / 2.0 - SPACER_WALL_W / 2.0) * bd.Box(
        horiz_len, thickness, SPACER_WALL_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    bottom_bar = bd.Pos(0.0, y_start, z_center - SHEET_H / 2.0 + SPACER_WALL_W / 2.0) * bd.Box(
        horiz_len, thickness, SPACER_WALL_W, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    left_bar = bd.Pos(-SHEET_W / 2.0 + SPACER_WALL_W / 2.0, y_start, z_center) * bd.Box(
        SPACER_WALL_W, thickness, vert_len, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
    )
    right_bar = bd.Pos(SHEET_W / 2.0 - SPACER_WALL_W / 2.0, y_start, z_center) * bd.Box(
        SPACER_WALL_W, thickness, vert_len, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)
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
    """16 mm square-cut butt-jointed front spacer (full-height sides, shorter top/bottom)."""
    return _square_butt_spacer_frame(FRONT_SPACER_T, Y_FRONT_SPACER_START, "front_spacer")


@model
def rear_spacer():
    """2 mm simplified straight-strip rear spacer creating cavity behind mid-board for ribbons."""
    return _straight_strip_spacer(REAR_SPACER_T, Y_REAR_SPACER_START, "rear_spacer")


if __name__ == "__main__":
    front_spacer()
    rear_spacer()
