"""Front and rear MDF spacer frames inside the frame cavity."""

import build123d as bd
from cad import model

from lib.dims import (
    FRAME_OUTER_H,
    FRONT_SPACER_T,
    REAR_SPACER_T,
    SHEET_H,
    SHEET_W,
    SPACER_WALL_W,
    Y_FRONT_SPACER_START,
    Y_REAR_SPACER_START,
)
from lib.materials import apply_spacer_mdf


def _mitred_spacer_frame(thickness: float, y_start: float, label_prefix: str) -> bd.Compound:
    """Build 4 straight 45-deg mitred spacer bars with a 6.0 mm outer-corner tip relief."""
    z_center = FRAME_OUTER_H / 2.0
    w_half = SHEET_W / 2.0
    h_half = SHEET_H / 2.0
    plane = bd.Plane(origin=(0.0, y_start, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))

    with bd.BuildPart() as ring_part:
        with bd.BuildSketch(plane):
            with bd.Locations((0.0, z_center)):
                bd.Rectangle(SHEET_W, SHEET_H)
                bd.Rectangle(SHEET_W - 2.0 * SPACER_WALL_W, SHEET_H - 2.0 * SPACER_WALL_W, mode=bd.Mode.SUBTRACT)
        bd.extrude(amount=-thickness)
        outer_vert_edges = ring_part.part.edges().filter_by(bd.Axis.Y).sort_by_distance((0.0, y_start, z_center))[-4:]
        bd.chamfer(outer_vert_edges, length=6.0)

    ring = ring_part.part
    m = SPACER_WALL_W + 2.0
    region_polys = [
        ("top", [(-w_half + m, z_center + h_half - m), (w_half - m, z_center + h_half - m), (w_half + 2.0, z_center + h_half + 2.0), (-w_half - 2.0, z_center + h_half + 2.0)]),
        ("bottom", [(-w_half - 2.0, z_center - h_half - 2.0), (w_half + 2.0, z_center - h_half - 2.0), (w_half - m, z_center - h_half + m), (-w_half + m, z_center - h_half + m)]),
        ("left", [(-w_half - 2.0, z_center - h_half - 2.0), (-w_half + m, z_center - h_half + m), (-w_half + m, z_center + h_half - m), (-w_half - 2.0, z_center + h_half + 2.0)]),
        ("right", [(w_half - m, z_center - h_half + m), (w_half + 2.0, z_center - h_half - 2.0), (w_half + 2.0, z_center + h_half + 2.0), (w_half - m, z_center + h_half - m)]),
    ]

    cut_plane = bd.Plane(origin=(0.0, y_start + thickness / 2.0, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    bars = []
    for side, pts in region_polys:
        with bd.BuildPart() as mask_part:
            with bd.BuildSketch(cut_plane):
                bd.Polygon(*pts, align=None)
            bd.extrude(amount=thickness / 2.0 + 2.0, both=True)
        bar = ring & mask_part.part
        bar.label = f"{label_prefix}_{side}"
        apply_spacer_mdf(bar)
        bars.append(bar)
    return bd.Compound(children=bars, label=label_prefix)


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
    """19 mm front mitred spacer creating clearance between the acrylic cover and medals."""
    return _mitred_spacer_frame(FRONT_SPACER_T, Y_FRONT_SPACER_START, "front_spacer")


@model
def rear_spacer():
    """5 mm simplified straight-strip rear spacer creating cavity behind mid-board for ribbons."""
    return _straight_strip_spacer(REAR_SPACER_T, Y_REAR_SPACER_START, "rear_spacer")


if __name__ == "__main__":
    front_spacer()
    rear_spacer()
