"""Hardwood outer frame rails/stiles with rounded corners, curved inset router, and 2-spline corner joinery."""

import build123d as bd
from cad import model

from lib.dims import (
    CAVITY_CORNER_R,
    CAVITY_H,
    CAVITY_W,
    FRAME_DEPTH,
    FRAME_FACE_W,
    FRAME_INNER_CORNER_R,
    FRAME_OUTER_CORNER_R,
    FRAME_OUTER_FRONT_FILLET,
    FRAME_OUTER_H,
    FRAME_OUTER_W,
    KERF_DEPTH,
    KERF_H,
    LIP_DEPTH,
    OPEN_H,
    OPEN_W,
    SPLINE_DEPTH,
    SPLINE_THICKNESS,
    SPLINE_YS,
    Y_KERF_START,
)
from lib.materials import apply_hardwood_walnut, apply_spline_walnut


def _build_unslotted_frame_envelope() -> bd.Shape:
    """Build the continuous walnut outer frame with rounded front edges, square back edge, rabbet, and curved inner router."""
    p_xz = bd.Plane.XZ
    with bd.BuildPart() as fp:
        with bd.BuildSketch(p_xz):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                if FRAME_OUTER_CORNER_R > 0.0:
                    bd.RectangleRounded(FRAME_OUTER_W, FRAME_OUTER_H, FRAME_OUTER_CORNER_R)
                else:
                    bd.Rectangle(FRAME_OUTER_W, FRAME_OUTER_H)
        bd.extrude(amount=-FRAME_DEPTH)

        if FRAME_OUTER_FRONT_FILLET > 0.0:
            front_edges = fp.part.faces().sort_by(bd.Axis.Y)[0].outer_wire().edges()
            bd.fillet(front_edges, radius=FRAME_OUTER_FRONT_FILLET)

        # Rear rabbet cavity
        rab_plane = bd.Plane(origin=(0.0, LIP_DEPTH, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        with bd.BuildSketch(rab_plane):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                if CAVITY_CORNER_R > 0.0:
                    bd.RectangleRounded(CAVITY_W, CAVITY_H, CAVITY_CORNER_R)
                else:
                    bd.Rectangle(CAVITY_W, CAVITY_H)
        bd.extrude(amount=-(FRAME_DEPTH - LIP_DEPTH + 2.0), mode=bd.Mode.SUBTRACT)

        # Internal locking kerf groove behind the 3 mm recessed backboard
        kerf_plane = bd.Plane(origin=(0.0, Y_KERF_START, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        with bd.BuildSketch(kerf_plane):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                if CAVITY_CORNER_R > 0.0:
                    bd.RectangleRounded(
                        CAVITY_W + 2.0 * KERF_DEPTH,
                        CAVITY_H + 2.0 * KERF_DEPTH,
                        CAVITY_CORNER_R + KERF_DEPTH,
                    )
                else:
                    bd.Rectangle(
                        CAVITY_W + 2.0 * KERF_DEPTH,
                        CAVITY_H + 2.0 * KERF_DEPTH,
                    )
        bd.extrude(amount=-KERF_H, mode=bd.Mode.SUBTRACT)

        # Viewing opening through front lip
        with bd.BuildSketch(p_xz):
            with bd.Locations((0.0, FRAME_OUTER_H / 2.0)):
                if FRAME_INNER_CORNER_R > 0.0:
                    bd.RectangleRounded(OPEN_W, OPEN_H, FRAME_INNER_CORNER_R)
                else:
                    bd.Rectangle(OPEN_W, OPEN_H)
        bd.extrude(amount=-(LIP_DEPTH + 2.0), mode=bd.Mode.SUBTRACT)

    return fp.part


def _corner_spline_blanks() -> list[tuple[str, bd.Shape]]:
    """Build the 8 oversized spline blank solids (2 per corner) oriented perpendicular to each mitre."""
    w_half = FRAME_OUTER_W / 2.0
    corners = [
        ("bl", -w_half, 0.0, -45.0),
        ("br", w_half, 0.0, -135.0),
        ("tr", w_half, FRAME_OUTER_H, 135.0),
        ("tl", -w_half, FRAME_OUTER_H, 45.0),
    ]
    # Blank extends from u = -6.0 (outside sharp corner) to u = +SPLINE_DEPTH inward along diagonal
    u_len = 6.0 + SPLINE_DEPTH
    u_center = (SPLINE_DEPTH - 6.0) / 2.0
    blank_proto = bd.Pos(u_center, 0.0, 0.0) * bd.Box(u_len, SPLINE_THICKNESS, 60.0)

    blanks: list[tuple[str, bd.Shape]] = []
    for corner_tag, cx, cz, rot_y in corners:
        for slot_idx, y_c in enumerate(SPLINE_YS, start=1):
            placed = bd.Pos(cx, y_c, cz) * bd.Rot(0.0, rot_y, 0.0) * blank_proto
            blanks.append((f"spline_{corner_tag}_{slot_idx}", placed))
    return blanks


def _split_mitred_pieces(frame_solid: bd.Shape) -> list[bd.Shape]:
    """Slice the continuous routed frame along the 45-deg corner mitre planes into 4 joinery pieces."""
    w_half = FRAME_OUTER_W / 2.0
    m = FRAME_FACE_W + 4.0  # inward reach past the 28 mm face width
    extrude_depth = FRAME_DEPTH + 10.0

    region_polys = [
        (
            "frame_bottom",
            [(-w_half - 5.0, -5.0), (w_half + 5.0, -5.0), (w_half - m, m), (-w_half + m, m)],
        ),
        (
            "frame_top",
            [
                (-w_half + m, FRAME_OUTER_H - m),
                (w_half - m, FRAME_OUTER_H - m),
                (w_half + 5.0, FRAME_OUTER_H + 5.0),
                (-w_half - 5.0, FRAME_OUTER_H + 5.0),
            ],
        ),
        (
            "frame_left",
            [(-w_half - 5.0, -5.0), (-w_half + m, m), (-w_half + m, FRAME_OUTER_H - m), (-w_half - 5.0, FRAME_OUTER_H + 5.0)],
        ),
        (
            "frame_right",
            [(w_half - m, m), (w_half + 5.0, -5.0), (w_half + 5.0, FRAME_OUTER_H + 5.0), (w_half - m, FRAME_OUTER_H - m)],
        ),
    ]

    cut_plane = bd.Plane(origin=(0.0, FRAME_DEPTH / 2.0, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    pieces: list[bd.Shape] = []
    for name, pts in region_polys:
        with bd.BuildPart() as mask_part:
            with bd.BuildSketch(cut_plane):
                bd.Polygon(*pts, align=None)
            bd.extrude(amount=extrude_depth / 2.0, both=True)
        piece = frame_solid & mask_part.part
        piece.label = name
        apply_hardwood_walnut(piece)
        pieces.append(piece)
    return pieces


@model
def hardwood_frame():
    """Four-piece mitred walnut frame with rounded corners, curved inset router, and 8 corner splines."""
    envelope = _build_unslotted_frame_envelope()
    spline_blanks = _corner_spline_blanks()

    splines: list[bd.Shape] = []
    slotted_frame = envelope
    for name, blank in spline_blanks:
        spline_solid = envelope & blank
        spline_solid.label = name
        apply_spline_walnut(spline_solid)
        splines.append(spline_solid)
        slotted_frame = slotted_frame - blank

    pieces = _split_mitred_pieces(slotted_frame)
    spline_group = bd.Compound(children=splines, label="corner_splines")
    asm = bd.Compound(children=[*pieces, spline_group], label="hardwood_frame")
    bb = asm.bounding_box()
    assert abs(bb.size.X - FRAME_OUTER_W) < 1e-4, bb.size
    assert abs(bb.size.Y - FRAME_DEPTH) < 1e-4, bb.size
    assert abs(bb.size.Z - FRAME_OUTER_H) < 1e-4, bb.size
    return asm


if __name__ == "__main__":
    hardwood_frame()
