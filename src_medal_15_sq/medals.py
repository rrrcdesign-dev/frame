"""73 mm circular medals and 25 mm woven ribbons passing through the mid-board slots."""

import build123d as bd
from cad import model

from lib.dims import (
    MEDAL_RADIUS,
    MEDAL_RECESS_DEPTH,
    MEDAL_RIM_WIDTH,
    MEDAL_THICKNESS,
    RIBBON_TAIL_H,
    RIBBON_THICKNESS,
    RIBBON_VISIBLE_H,
    RIBBON_WIDTH,
    SLOT_HEIGHT,
    Y_MID_BOARD_START,
    all_medal_positions,
)
from lib.materials import apply_medal_gold, apply_ribbon_fabric


@model
def medal():
    """Single 73 mm diameter x 5 mm thick circular medal with raised rim and inner medallion step.

    Local frame: back face at Y = 0, front face at Y = -MEDAL_THICKNESS, centered at (X=0, Z=0).
    """
    with bd.BuildPart() as part:
        with bd.BuildSketch(bd.Plane.XZ):
            bd.Circle(MEDAL_RADIUS)
        bd.extrude(amount=MEDAL_THICKNESS)  # Plane.XZ normal is -Y (forward)

        front_plane = bd.Plane(
            origin=(0.0, -MEDAL_THICKNESS, 0.0),
            x_dir=(1, 0, 0),
            z_dir=(0, -1, 0),
        )
        with bd.BuildSketch(front_plane):
            bd.Circle(MEDAL_RADIUS - MEDAL_RIM_WIDTH)
        bd.extrude(amount=-MEDAL_RECESS_DEPTH, mode=bd.Mode.SUBTRACT)

        # Subtle inner decorative step ring
        recess_plane = bd.Plane(
            origin=(0.0, -MEDAL_THICKNESS + MEDAL_RECESS_DEPTH, 0.0),
            x_dir=(1, 0, 0),
            z_dir=(0, -1, 0),
        )
        with bd.BuildSketch(recess_plane):
            bd.Circle(MEDAL_RADIUS - MEDAL_RIM_WIDTH - 3.5)
            bd.Circle(MEDAL_RADIUS - MEDAL_RIM_WIDTH - 5.0, mode=bd.Mode.SUBTRACT)
        bd.extrude(amount=0.35, mode=bd.Mode.ADD)

    solid = part.part
    solid.label = "medal"
    apply_medal_gold(solid)
    bb = solid.bounding_box()
    assert abs(bb.size.X - 2.0 * MEDAL_RADIUS) < 1e-4, bb.size
    assert abs(bb.size.Y - MEDAL_THICKNESS) < 1e-4, bb.size
    assert abs(bb.size.Z - 2.0 * MEDAL_RADIUS) < 1e-4, bb.size
    return solid


@model
def ribbon():
    """25 mm wide woven ribbon showing 15 mm drop on front and passing through slot to back.

    Local frame: Y = 0 aligns with mid-board front face, Z = 0 aligns with medal center.
    """
    z_medal_top = MEDAL_RADIUS
    z_slot_center = MEDAL_RADIUS + RIBBON_VISIBLE_H + SLOT_HEIGHT / 2.0
    y_front_center = -MEDAL_THICKNESS / 2.0  # -2.5 mm (centered above 5 mm medal)
    y_back_drop = 4.8  # 1.8 mm clear behind 3 mm mid-board (Y = 3.0)
    z_tail_bottom = z_slot_center - RIBBON_TAIL_H
    half_t = RIBBON_THICKNESS / 2.0
    r_mid = 1.8
    r_outer = r_mid + half_t
    r_inner = r_mid - half_t

    y_f_out, y_f_in = y_front_center - half_t, y_front_center + half_t
    y_b_out, y_b_in = y_back_drop + half_t, y_back_drop - half_t
    z_s_out, z_s_in = z_slot_center + half_t, z_slot_center - half_t

    with bd.BuildPart() as part:
        with bd.BuildSketch(bd.Plane.YZ):
            with bd.BuildLine():
                bd.FilletPolyline(
                    (y_f_out, z_medal_top),
                    (y_f_out, z_s_out),
                    (y_b_out, z_s_out),
                    (y_b_out, z_tail_bottom),
                    radius=r_outer,
                )
                bd.Line((y_b_out, z_tail_bottom), (y_b_in, z_tail_bottom))
                bd.FilletPolyline(
                    (y_b_in, z_tail_bottom),
                    (y_b_in, z_s_in),
                    (y_f_in, z_s_in),
                    (y_f_in, z_medal_top),
                    radius=r_inner,
                )
                bd.Line((y_f_in, z_medal_top), (y_f_out, z_medal_top))
            bd.make_face()
        bd.extrude(amount=RIBBON_WIDTH / 2.0, both=True)

    solid = part.part
    solid.label = "ribbon"
    apply_ribbon_fabric(solid)
    return solid


@model
def medal_set():
    """All 15 medals and ribbons arranged in the 3x5 display grid."""
    medal_proto = medal().shape
    ribbon_proto = ribbon().shape

    children = []
    for row, col, x, z in all_medal_positions():
        m = bd.Pos(x, Y_MID_BOARD_START, z) * medal_proto
        m.label = f"medal_r{row + 1}_c{col + 1}"

        r = bd.Pos(x, Y_MID_BOARD_START, z) * ribbon_proto
        r.label = f"ribbon_r{row + 1}_c{col + 1}"

        unit = bd.Compound(children=[m, r], label=f"medal_unit_r{row + 1}_c{col + 1}")
        children.append(unit)

    return bd.Compound(children=children, label="medals")


if __name__ == "__main__":
    medal_set()
