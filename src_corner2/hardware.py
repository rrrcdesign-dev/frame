"""Rear mounting hardware: heavy-duty metal turn buttons and left/right wall-hanging D-ring brackets."""

import build123d as bd
from cad import model

from lib.dims import (
    BACKBOARD_H,
    BACKBOARD_W,
    FRAME_OUTER_H,
    HANGER_BACKBOARD_INSET,
    HANGER_Z,
    TURN_BUTTON_LEN,
    TURN_BUTTON_SIDE_ZS,
    TURN_BUTTON_T,
    TURN_BUTTON_TOP_BOTTOM_XS,
    TURN_BUTTON_W,
    TURN_LOCK_EDGE_INSET,
    Y_BACKBOARD_END,
)
from lib.materials import apply_hardware_steel


def wood_screw_cap_body(
    shaft_d: float = 3.4,
    shaft_len: float = 2.0,
    head_d: float = 5.4,
    head_h: float = 1.6,
    label: str = "screw",
) -> bd.Shape:
    """Build a pan-head wood screw cap that seats cleanly inside a hardware clearance bore."""
    with bd.BuildPart() as part:
        with bd.BuildSketch(bd.Plane.XZ):
            bd.Circle(shaft_d / 2.0)
        bd.extrude(amount=-shaft_len)  # -z_dir of Plane.XZ is +Y

        head_plane = bd.Plane(origin=(0.0, shaft_len, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        with bd.BuildSketch(head_plane):
            bd.Circle(head_d / 2.0)
        bd.extrude(amount=-head_h)

        # Dome top bevel
        top_edges = part.part.edges().sort_by(bd.Axis.Y)[-1:]
        bd.chamfer(top_edges, length=0.45)

    solid = part.part
    solid.label = label
    apply_hardware_steel(solid)
    return solid


@model
def turn_button():
    """Heavy-duty metal turn button with mounting screw.

    Local frame: screw axis at (X=0, Z=0), Y=0 rests on frame/backboard back face (+Y outward).
    Clamping tongue points along +X.
    """
    tail_r = TURN_BUTTON_W / 2.0
    tip_offset = TURN_BUTTON_LEN - tail_r  # +16.5 mm

    plate_plane = bd.Plane(origin=(0.0, 0.0, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as plate_part:
        with bd.BuildSketch(plate_plane):
            bd.Rectangle(tip_offset, TURN_BUTTON_W, align=(bd.Align.MIN, bd.Align.CENTER))
            with bd.Locations((0.0, 0.0), (tip_offset, 0.0)):
                bd.Circle(tail_r)
        bd.extrude(amount=-TURN_BUTTON_T)

        # Mounting clearance hole at (0, 0)
        with bd.BuildSketch(plate_plane):
            bd.Circle(3.6 / 2.0)
        bd.extrude(amount=-(TURN_BUTTON_T + 1.0), mode=bd.Mode.SUBTRACT)

        top_outer_edges = plate_part.part.faces().sort_by(bd.Axis.Y)[-1].outer_wire().edges()
        bd.chamfer(top_outer_edges, length=0.35)

    plate = plate_part.part
    plate.label = "turn_button_plate"
    apply_hardware_steel(plate)

    screw = wood_screw_cap_body(
        shaft_d=3.4,
        shaft_len=TURN_BUTTON_T,
        head_d=5.4,
        head_h=1.5,
        label="turn_button_screw",
    )

    return bd.Compound(children=[plate, screw], label="turn_button")


@model
def wall_hanger():
    """Heavy-duty 2-hole metal D-ring strap hanger with open loop to tie a hanging cord.

    Local frame: strap centered at (X=0, Z=0), Y=0 touches frame back face (+Y outward).
    D-ring swings inward (+X) and angled slightly away from frame (+Y).
    """
    strap_w = 10.0
    strap_h = 30.0
    strap_t = 1.6
    screw_zs = (-9.5, 9.5)
    barrel_x = 3.4
    barrel_y = 2.8
    barrel_len = 10.0
    barrel_od = 5.0
    barrel_id = 2.6

    plate_plane = bd.Plane(origin=(0.0, 0.0, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with bd.BuildPart() as bracket_part:
        with bd.BuildSketch(plate_plane):
            bd.RectangleRounded(strap_w, strap_h, 2.0)
        bd.extrude(amount=-strap_t)

        # Curled hinge barrel along Z at (barrel_x, barrel_y)
        with bd.Locations((barrel_x, barrel_y, 0.0)):
            bd.Cylinder(barrel_od / 2.0, barrel_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))

        # Subtract bore through barrel
        with bd.Locations((barrel_x, barrel_y, 0.0)):
            bd.Cylinder(
                barrel_id / 2.0,
                barrel_len + 2.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
                mode=bd.Mode.SUBTRACT,
            )

        # Two screw clearance holes in the strap plate
        with bd.BuildSketch(plate_plane):
            for sz in screw_zs:
                with bd.Locations((0.0, sz)):
                    bd.Circle(3.6 / 2.0)
        bd.extrude(amount=-(strap_t + 1.0), mode=bd.Mode.SUBTRACT)

    strap = bracket_part.part
    strap.label = "hanger_strap"
    apply_hardware_steel(strap)

    # Steel D-ring loop passing cleanly through barrel bore (0.2 mm radial clearance)
    # Tilted 18 deg away from the frame (+Y) so it's easy to tie a string through the open loop
    wire_r = 1.1
    with bd.BuildPart() as ring_part:
        with bd.BuildLine(bd.Plane.XY) as ring_line:
            bd.FilletPolyline(
                (0.0, -7.8),
                (0.0, 7.8),
                (14.5, 4.2),
                (14.5, -4.2),
                radius=2.8,
                close=True,
            )
        path_wire = ring_line.wire()
        with bd.BuildSketch(path_wire ^ 0):
            bd.Circle(wire_r)
        bd.sweep(path=path_wire)

    ring = bd.Pos(barrel_x, barrel_y, 0.0) * bd.Rot(0, 0, 18) * bd.Rot(90, 0, 0) * ring_part.part
    ring.label = "hanger_d_ring"
    apply_hardware_steel(ring)

    screw_proto = wood_screw_cap_body(
        shaft_d=3.4,
        shaft_len=strap_t,
        head_d=5.2,
        head_h=1.4,
        label="hanger_screw",
    )
    screws = []
    for idx, sz in enumerate(screw_zs, start=1):
        sc = bd.Pos(0.0, 0.0, sz) * screw_proto
        sc.label = f"hanger_screw_{idx}"
        screws.append(sc)

    return bd.Compound(children=[strap, ring, *screws], label="wall_hanger")


@model
def rear_hardware():
    """6 backboard-mounted turn locks (engaging the frame kerf) and 2 backboard-mounted D-ring hangers."""
    tb_proto = turn_button().shape
    hanger_proto = wall_hanger().shape

    turn_buttons = []
    z_center = FRAME_OUTER_H / 2.0
    x_bb_left = -BACKBOARD_W / 2.0 + TURN_LOCK_EDGE_INSET
    x_bb_right = BACKBOARD_W / 2.0 - TURN_LOCK_EDGE_INSET
    z_bb_bottom = z_center - BACKBOARD_H / 2.0 + TURN_LOCK_EDGE_INSET
    z_bb_top = z_center + BACKBOARD_H / 2.0 - TURN_LOCK_EDGE_INSET

    # Bottom edge (pointing -Z outward into bottom kerf -> +90 deg around Y)
    for idx, x in enumerate(TURN_BUTTON_TOP_BOTTOM_XS, start=1):
        tb = bd.Pos(x, Y_BACKBOARD_END, z_bb_bottom) * bd.Rot(0, 90, 0) * tb_proto
        tb.label = f"turn_button_bottom_{idx}"
        turn_buttons.append(tb)

    # Top edge (pointing +Z outward into top kerf -> -90 deg around Y)
    for idx, x in enumerate(TURN_BUTTON_TOP_BOTTOM_XS, start=1):
        tb = bd.Pos(x, Y_BACKBOARD_END, z_bb_top) * bd.Rot(0, -90, 0) * tb_proto
        tb.label = f"turn_button_top_{idx}"
        turn_buttons.append(tb)

    # Left edge (pointing -X outward into left kerf -> 180 deg around Y)
    for idx, z in enumerate(TURN_BUTTON_SIDE_ZS, start=1):
        tb = bd.Pos(x_bb_left, Y_BACKBOARD_END, z) * bd.Rot(0, 180, 0) * tb_proto
        tb.label = f"turn_button_left_{idx}"
        turn_buttons.append(tb)

    # Right edge (pointing +X outward into right kerf -> 0 deg)
    for idx, z in enumerate(TURN_BUTTON_SIDE_ZS, start=1):
        tb = bd.Pos(x_bb_right, Y_BACKBOARD_END, z) * tb_proto
        tb.label = f"turn_button_right_{idx}"
        turn_buttons.append(tb)

    tb_group = bd.Compound(children=turn_buttons, label="turn_buttons")

    # Left and right metal D-ring hanging brackets mounted on the recessed backboard
    x_hanger_left = -BACKBOARD_W / 2.0 + HANGER_BACKBOARD_INSET
    x_hanger_right = BACKBOARD_W / 2.0 - HANGER_BACKBOARD_INSET

    hanger_left = bd.Pos(x_hanger_left, Y_BACKBOARD_END, HANGER_Z) * hanger_proto
    hanger_left.label = "wall_hanger_left"

    hanger_right = bd.Pos(x_hanger_right, Y_BACKBOARD_END, HANGER_Z) * bd.Rot(0, 180, 0) * hanger_proto
    hanger_right.label = "wall_hanger_right"

    hangers_group = bd.Compound(children=[hanger_left, hanger_right], label="wall_hangers")
    return bd.Compound(children=[tb_group, hangers_group], label="rear_hardware")


if __name__ == "__main__":
    rear_hardware()
