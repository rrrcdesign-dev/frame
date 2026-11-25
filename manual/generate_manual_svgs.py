"""Generate 5 true-vector color-filled IKEA-style SVG manual graphics and raster previews."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

OUT_DIR = Path("/Volumes/X10 Pro/Antigravity/Frame/manual")
SCRATCH_DIR = Path("/Users/ryan/.gemini/antigravity/brain/71e762b4-7d6b-4d2f-b894-c011e5d05ce0/scratch")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Exact medal_8_sq dimensions (mm) from src_medal_8_sq/lib/dims.py
FRAME_W_MM = 414.0
FRAME_H_MM = 275.0
FRAME_D_MM = 46.0
FRAME_WALL_MM = 9.0
FRAME_FACE_MM = 15.0
LIP_DEPTH_MM = 6.0
ACRYLIC_T_MM = 2.0
FRONT_SPACER_T_MM = 15.0
SPACER_WALL_MM = 3.0
MID_BOARD_T_MM = 4.0
BACKBOARD_PLY_T_MM = 4.0
BACKBOARD_FRAME_T_MM = 11.0
BACKBOARD_FRAME_W_MM = 15.0

SHEET_W_MM = 395.6
SHEET_H_MM = 256.6
COL_PITCH_MM = 87.0
MEDAL_DIAMETER_MM = 73.0
MEDAL_RADIUS_MM = MEDAL_DIAMETER_MM / 2.0
MEDAL_RIM_WIDTH_MM = 3.2
RIBBON_WIDTH_MM = 25.0
RIBBON_TAIL_H_MM = 48.0
SLOT_WIDTH_MM = 45.0
SLOT_HEIGHT_MM = 2.5
TOP_SLOT_OFFSET_MM = 35.05
BOTTOM_SLOT_OFFSET_MM = 139.55
TOP_MEDAL_OFFSET_MM = 87.8

INK = "#111111"

PALETTE = {
    "walnut_top": "#A67550",
    "walnut_left": "#8C5E3C",
    "walnut_right": "#734B2E",
    "walnut_in_left": "#7C5335",
    "walnut_in_right": "#664228",
    "walnut_ledge": "#B88A66",
    "acrylic_face": "#E4F4FA",
    "acrylic_trans": "#DFF1F7",
    "acrylic_edge": "#B5DCE8",
    "acrylic_sheen": "#5A9DB5",
    "film_top": "#BDD2DD",
    "film_flap": "#D5E4EC",
    "film_under": "#A8C0CD",
    "spacer_top": "#9B8878",
    "spacer_left": "#7D6B5D",
    "spacer_right": "#68574A",
    "birch_face": "#EBDAC2",
    "birch_edge": "#CEB795",
    "birch_slot": "#C4AB88",
    "ply_face": "#D4B483",
    "pine_top": "#ECD4AE",
    "pine_left": "#DEC092",
    "pine_right": "#CCA976",
    "pine_in": "#C4A06E",
    "medal_rim": "#E8C868",
    "medal_disc": "#D4AF37",
    "medal_step": "#E2BE52",
    "medal_bail": "#C9A233",
    "ribbon": "#3A5B8C",
    "ribbon_fold": "#243D63",
    "tape": "#F5E9C8",
    "wall_front": "#F3F2EE",
    "wall_edge": "#DEDCD5",
    "wall_section": "#E3E1DA",
    "nail_shaft": "#9AA3AD",
    "nail_head": "#C2C9D1",
}


def pts_str(pts: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def poly(
    pts: list[tuple[float, float]],
    fill: str,
    stroke: str = INK,
    sw: float = 2.4,
    extra: str = "",
) -> str:
    return (
        f'<polygon points="{pts_str(pts)}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw:.2f}" stroke-linejoin="round" {extra}/>'
    )


def svg_curved_arrow(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    w0: float = 2.4,
    w1: float = 7.2,
    head_len: float = 22.0,
    head_hw: float = 15.5,
    halo: float = 5.0,
) -> str:
    """Build a crisp tapered IKEA-style curved arrow from a cubic Bezier."""
    pts: list[tuple[float, float, float, float, float, float, float]] = []
    n_steps = 48
    for i in range(n_steps + 1):
        t = i / n_steps
        mt = 1.0 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        dx = 3 * mt**2 * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t**2 * (p3[0] - p2[0])
        dy = 3 * mt**2 * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t**2 * (p3[1] - p2[1])
        norm = math.hypot(dx, dy) or 1.0
        ux, uy = dx / norm, dy / norm
        nx, ny = -uy, ux
        hw = w0 + (w1 - w0) * (t**0.85)
        pts.append((x, y, nx, ny, hw, ux, uy))

    left = [(x + nx * hw, y + ny * hw) for x, y, nx, ny, hw, _, _ in pts]
    right = [(x - nx * hw, y - ny * hw) for x, y, nx, ny, hw, _, _ in reversed(pts)]
    tx, ty, nx, ny, _, ux, uy = pts[-1]
    tip = (tx + ux * head_len, ty + uy * head_len)
    w_a = (tx + nx * head_hw, ty + ny * head_hw)
    w_b = (tx - nx * head_hw, ty - ny * head_hw)
    all_pts = left + [w_a, tip, w_b] + right
    halo_attr = f'stroke="#FFFFFF" stroke-width="{halo:.2f}" stroke-linejoin="round" paint-order="stroke"' if halo > 0 else ""
    return f'<polygon points="{pts_str(all_pts)}" fill="{INK}" {halo_attr}/>'


def svg_block_arrow(cx: float, y_top: float, y_bot: float, shaft_hw: float = 12.0, head_h: float = 34.0, head_hw: float = 28.0) -> str:
    """Straight downward IKEA block arrow."""
    neck_y = y_bot - head_h
    pts = [
        (cx - shaft_hw, y_top),
        (cx + shaft_hw, y_top),
        (cx + shaft_hw, neck_y),
        (cx + head_hw, neck_y),
        (cx, y_bot),
        (cx - head_hw, neck_y),
        (cx - shaft_hw, neck_y),
    ]
    return f'<polygon points="{pts_str(pts)}" fill="{INK}" stroke="#FFFFFF" stroke-width="5.0" stroke-linejoin="round" paint-order="stroke"/>'


def wrap_svg(width: int, height: int, body: str) -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
        f'  <rect width="{width}" height="{height}" fill="#FFFFFF"/>\n'
        f'{body}\n'
        f'</svg>\n'
    )


def rasterize_svg(svg_path: Path, png_path: Path, width: int, height: int) -> None:
    """Rasterize SVG at 2x via headless Chrome and LANCZOS-downsample to clean RGB PNG."""
    html_path = SCRATCH_DIR / f"{svg_path.stem}_render.html"
    raw_2x = SCRATCH_DIR / f"{svg_path.stem}_2x.png"
    svg_text = svg_path.read_text(encoding="utf-8")
    html_path.write_text(
        f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
html, body {{ margin: 0; padding: 0; width: {width}px; height: {height}px; background: #fff; overflow: hidden; }}
svg {{ display: block; width: {width}px; height: {height}px; }}
</style></head>
<body>{svg_text}</body>
</html>""",
        encoding="utf-8",
    )
    subprocess.run(
        [
            CHROME_BIN,
            "--headless=new",
            "--disable-gpu",
            "--force-device-scale-factor=2",
            f"--window-size={width},{height}",
            "--hide-scrollbars",
            f"--screenshot={raw_2x}",
            html_path.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    im = Image.open(raw_2x).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    arr = np.array(im)
    arr[np.all(arr >= 252, axis=2)] = [255, 255, 255]
    Image.fromarray(arr, mode="RGB").save(png_path, format="PNG")
    print(f"Saved {svg_path.name} + {png_path.name} ({width}x{height})")


# ────────────────────────────────────────────────────────────────────
# STEP 01: Front orthographic 4x2 mid-board with 3 medals (Cols 1-3)
# ────────────────────────────────────────────────────────────────────
def build_step01() -> str:
    W, H = 1200, 896
    scale = 2.40
    bw = SHEET_W_MM * scale
    bh = SHEET_H_MM * scale
    bx0 = (W - bw) / 2.0
    by0 = (H - bh) / 2.0 + 16.0

    slot_w = SLOT_WIDTH_MM * scale
    slot_h = 11.0
    slot_rx = slot_h / 2.0
    col_xs_mm = [-130.5, -43.5, 43.5, 130.5]
    row_ys_mm = [TOP_SLOT_OFFSET_MM, BOTTOM_SLOT_OFFSET_MM]

    parts: list[str] = [
        f'<rect x="{bx0:.2f}" y="{by0:.2f}" width="{bw:.2f}" height="{bh:.2f}" '
        f'fill="{PALETTE["birch_face"]}" stroke="{INK}" stroke-width="3.0" stroke-linejoin="miter"/>'
    ]

    # 8 slots (4x2)
    for r_idx, y_mm in enumerate(row_ys_mm):
        for c_idx, x_mm in enumerate(col_xs_mm):
            cx = bx0 + bw / 2.0 + x_mm * scale
            cy = by0 + y_mm * scale
            sx = cx - slot_w / 2.0
            sy = cy - slot_h / 2.0
            parts.append(
                f'<rect x="{sx:.2f}" y="{sy:.2f}" width="{slot_w:.2f}" height="{slot_h:.2f}" '
                f'rx="{slot_rx:.2f}" ry="{slot_rx:.2f}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/>'
            )
            # Subtle inner plywood edge shadow on top inside of slot
            parts.append(
                f'<path d="M {sx + slot_rx:.2f} {sy + 3.0:.2f} L {sx + slot_w - slot_rx:.2f} {sy + 3.0:.2f}" '
                f'stroke="{PALETTE["birch_slot"]}" stroke-width="2.0" stroke-linecap="round"/>'
            )

    # 3 medals hanging on Row 1 Columns 1, 2, 3
    medal_cy = by0 + TOP_MEDAL_OFFSET_MM * scale
    top_slot_cy = by0 + TOP_SLOT_OFFSET_MM * scale
    medal_r = MEDAL_RADIUS_MM * scale
    rim_r = (MEDAL_RADIUS_MM - MEDAL_RIM_WIDTH_MM) * scale
    inner_r = (MEDAL_RADIUS_MM - MEDAL_RIM_WIDTH_MM - 5.0) * scale
    ribbon_w = RIBBON_WIDTH_MM * scale
    bail_w = 13.0 * scale
    bail_h = 4.6 * scale
    bail_y = medal_cy - medal_r - bail_h * 0.52
    rib_top = top_slot_cy - slot_h * 0.32
    rib_bot = bail_y + bail_h * 0.45

    for c_idx in range(3):
        cx = bx0 + bw / 2.0 + col_xs_mm[c_idx] * scale
        rx0 = cx - ribbon_w / 2.0
        bail_x = cx - bail_w / 2.0
        parts.append(
            f'<g id="medal-{c_idx + 1}">'
            # Ribbon
            f'<rect x="{rx0:.2f}" y="{rib_top:.2f}" width="{ribbon_w:.2f}" height="{rib_bot - rib_top:.2f}" '
            f'fill="{PALETTE["ribbon"]}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<line x1="{rx0 + 4:.2f}" y1="{rib_bot - 5:.2f}" x2="{rx0 + ribbon_w - 4:.2f}" y2="{rib_bot - 5:.2f}" '
            f'stroke="{PALETTE["ribbon_fold"]}" stroke-width="1.8" stroke-linecap="round"/>'
            # Bail
            f'<rect x="{bail_x:.2f}" y="{bail_y:.2f}" width="{bail_w:.2f}" height="{bail_h:.2f}" '
            f'rx="4.2" ry="4.2" fill="{PALETTE["medal_bail"]}" stroke="{INK}" stroke-width="2.3"/>'
            f'<rect x="{bail_x + 4.5:.2f}" y="{bail_y + 3.0:.2f}" width="{bail_w - 9.0:.2f}" height="{bail_h - 6.0:.2f}" '
            f'rx="1.8" ry="1.8" fill="{PALETTE["birch_face"]}" stroke="{INK}" stroke-width="1.4"/>'
            # Gold Medal
            f'<circle cx="{cx:.2f}" cy="{medal_cy:.2f}" r="{medal_r:.2f}" fill="{PALETTE["medal_rim"]}" stroke="{INK}" stroke-width="2.8"/>'
            f'<circle cx="{cx:.2f}" cy="{medal_cy:.2f}" r="{rim_r:.2f}" fill="{PALETTE["medal_disc"]}" stroke="{INK}" stroke-width="1.8"/>'
            f'<circle cx="{cx:.2f}" cy="{medal_cy:.2f}" r="{inner_r:.2f}" fill="none" stroke="{PALETTE["medal_step"]}" stroke-width="2.4"/>'
            f'<circle cx="{cx:.2f}" cy="{medal_cy:.2f}" r="{inner_r - 2.0:.2f}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.75"/>'
            f'</g>'
        )

    # Bold curved threading arrow on the 3rd medal (Row 1, Col 3)
    c3_x = bx0 + bw / 2.0 + col_xs_mm[2] * scale
    parts.append(
        svg_curved_arrow(
            p0=(c3_x + ribbon_w * 1.18, top_slot_cy + 40.0),
            p1=(c3_x + ribbon_w * 1.32, top_slot_cy - 54.0),
            p2=(c3_x + 12.0, top_slot_cy - 62.0),
            p3=(c3_x - 2.0, top_slot_cy - 19.0),
        )
    )

    return wrap_svg(W, H, "\n  ".join(parts))


# ────────────────────────────────────────────────────────────────────
# STEP 02: Flipped 4x2 mid-board back view — Col 1 empty, Cols 2-4 taped, arrow on Col 2
# ────────────────────────────────────────────────────────────────────
def build_step02() -> str:
    W, H = 1200, 896

    # True 1-point tabletop perspective projection of board (u in [-SHEET_W/2, +SHEET_W/2], v in [0, SHEET_H])
    # Top edge (v=0) is narrower and higher; bottom edge (v=SHEET_H) is wider and lower.
    def proj(u_mm: float, v_mm: float) -> tuple[float, float]:
        t = v_mm / SHEET_H_MM  # 0 at top edge, 1 at bottom edge
        # Projective perspective interpolation
        p = 0.28
        w_t = 1.0 / (1.0 - p * (1.0 - t))
        w_0 = 1.0 / (1.0 - p)
        alpha = (w_t - w_0) / (1.0 - w_0)  # 0 at v=0, 1 at v=SHEET_H
        y = 228.0 + alpha * (706.0 - 228.0)
        half_w = 376.0 + alpha * (506.0 - 376.0)
        x = W / 2.0 + (u_mm / (SHEET_W_MM / 2.0)) * half_w
        return x, y

    tl = proj(-SHEET_W_MM / 2.0, 0.0)
    tr = proj(SHEET_W_MM / 2.0, 0.0)
    br = proj(SHEET_W_MM / 2.0, SHEET_H_MM)
    bl = proj(-SHEET_W_MM / 2.0, SHEET_H_MM)
    edge_drop = 14.0
    bl_bot = (bl[0], bl[1] + edge_drop)
    br_bot = (br[0], br[1] + edge_drop)

    parts: list[str] = [
        # 4mm front thickness edge
        poly([bl, br, br_bot, bl_bot], PALETTE["birch_edge"], INK, 2.8),
        # Flipped back face
        poly([tl, tr, br, bl], PALETTE["birch_face"], INK, 3.0),
    ]

    # 8 horizontal rounded-end slots (4 cols x 2 rows)
    col_xs_mm = [-130.5, -43.5, 43.5, 130.5]
    row_ys_mm = [TOP_SLOT_OFFSET_MM + 12.0, BOTTOM_SLOT_OFFSET_MM + 12.0]  # visual breathing room on back

    def slot_polygon(cx_mm: float, cy_mm: float, w_mm: float = SLOT_WIDTH_MM, h_mm: float = 9.5) -> list[tuple[float, float]]:
        rx = h_mm / 2.0
        pts: list[tuple[float, float]] = []
        # Top straight + right semicircle + bottom straight + left semicircle
        n_arc = 10
        x_l = cx_mm - w_mm / 2.0 + rx
        x_r = cx_mm + w_mm / 2.0 - rx
        for i in range(n_arc + 1):
            ang = -math.pi / 2 + math.pi * (i / n_arc)
            pts.append(proj(x_r + rx * math.cos(ang), cy_mm + rx * math.sin(ang)))
        for i in range(n_arc + 1):
            ang = math.pi / 2 + math.pi * (i / n_arc)
            pts.append(proj(x_l + rx * math.cos(ang), cy_mm + rx * math.sin(ang)))
        return pts

    for y_mm in row_ys_mm:
        for x_mm in col_xs_mm:
            s_pts = slot_polygon(x_mm, y_mm)
            # Inner 4mm cut thickness wall visible at top interior of slot
            inner_pts = slot_polygon(x_mm, y_mm + 2.6, SLOT_WIDTH_MM - 1.5, 7.0)
            parts.append(poly(s_pts, PALETTE["birch_slot"], INK, 2.4))
            parts.append(poly(inner_pts, "#FFFFFF", INK, 1.5))

    # Row 1 Col 1 (left top slot) is EMPTY.
    # Row 1 Cols 2, 3, 4 (next 3 slots) have folded navy ribbons + cream serrated masking tape!
    r1_y = row_ys_mm[0]
    rib_half_w = RIBBON_WIDTH_MM / 2.0  # 12.5 mm
    rib_top_v = r1_y + 1.0
    rib_bot_v = r1_y + 62.0  # ends cleanly well above Row 2 (151.5 mm)

    tape_half_w = 27.0
    tape_top_v = r1_y + 16.0
    tape_bot_v = r1_y + 34.0

    for idx, x_mm in enumerate(col_xs_mm[1:], start=2):
        # Navy folded excess ribbon tail
        r_pts = [
            proj(x_mm - rib_half_w, rib_top_v),
            proj(x_mm + rib_half_w, rib_top_v),
            proj(x_mm + rib_half_w, rib_bot_v),
            proj(x_mm - rib_half_w, rib_bot_v),
        ]
        # Subtle crease line where ribbon folds out of the slot
        f_l = proj(x_mm - rib_half_w + 1.5, rib_top_v + 4.5)
        f_r = proj(x_mm + rib_half_w - 1.5, rib_top_v + 4.5)
        parts.append(poly(r_pts, PALETTE["ribbon"], INK, 2.4))
        parts.append(
            f'<line x1="{f_l[0]:.2f}" y1="{f_l[1]:.2f}" x2="{f_r[0]:.2f}" y2="{f_r[1]:.2f}" '
            f'stroke="{PALETTE["ribbon_fold"]}" stroke-width="1.8" stroke-linecap="round"/>'
        )

        # Cream masking tape strip with crisp serrated left/right ends
        t_pts: list[tuple[float, float]] = [proj(x_mm - tape_half_w, tape_top_v), proj(x_mm + tape_half_w, tape_top_v)]
        n_teeth = 5
        for k in range(1, n_teeth * 2):
            tv = tape_top_v + (tape_bot_v - tape_top_v) * (k / (n_teeth * 2))
            tu = x_mm + tape_half_w + (2.4 if k % 2 == 1 else -1.4)
            t_pts.append(proj(tu, tv))
        t_pts.append(proj(x_mm + tape_half_w, tape_bot_v))
        t_pts.append(proj(x_mm - tape_half_w, tape_bot_v))
        for k in range(n_teeth * 2 - 1, 0, -1):
            tv = tape_top_v + (tape_bot_v - tape_top_v) * (k / (n_teeth * 2))
            tu = x_mm - tape_half_w - (2.4 if k % 2 == 1 else -1.4)
            t_pts.append(proj(tu, tv))
        parts.append(poly(t_pts, PALETTE["tape"], INK, 2.1))

    # Bold curved pressing arrow on the 2nd slot (Row 1, Col 2) — NO HAND
    c2_top = proj(col_xs_mm[1] + 24.0, r1_y - 26.0)
    c2_mid1 = proj(col_xs_mm[1] + 44.0, r1_y - 12.0)
    c2_mid2 = proj(col_xs_mm[1] + 34.0, r1_y + 10.0)
    c2_end = proj(col_xs_mm[1] + 10.0, r1_y + 20.0)
    parts.append(svg_curved_arrow(c2_top, c2_mid1, c2_mid2, c2_end, w0=2.8, w1=7.8, head_len=24.0, head_hw=16.5))

    return wrap_svg(W, H, "\n  ".join(parts))


# ────────────────────────────────────────────────────────────────────
# STEP 03: Peel protective film off both sides of 2 mm acrylic — NO HAND
# ────────────────────────────────────────────────────────────────────
def build_step03() -> str:
    W, H = 1200, 896

    # Match 03.png's tilted 30-deg isometric acrylic sheet coordinates cleanly in 1200x896
    # Corners of top face: Left (80, 520), Bottom (435, 760), Right (1065, 396), Top (710, 198)
    L = (80.0, 520.0)
    B = (435.0, 760.0)
    R = (1065.0, 396.0)
    T = (710.0, 198.0)
    th = 13.0
    L_b = (L[0], L[1] + th)
    B_b = (B[0], B[1] + th)
    R_b = (R[0], R[1] + th)

    # Diagonal peel seam line from bottom corner B up to top-right-ish edge P_top on T-R?
    # In 03.png, peel seam runs from B (bottom corner) to P_top near T (along T-R edge, ~22% from T).
    P_top = (T[0] + 0.04 * (R[0] - T[0]), T[1] + 0.04 * (R[1] - T[1]))
    # Left edge peel crease starts around B and curls upward-left to lifted corner C_lift
    C_lift = (446.0, 232.0)

    parts: list[str] = []

    # 1. Underside peeling protective film (hanging below B-R edge)
    u_path = (
        f"M {B_b[0] + 18:.2f},{B_b[1] - 4:.2f} "
        f"Q {620:.2f},{660:.2f} {822:.2f},{548:.2f} "
        f"Q {792:.2f},{660:.2f} {802:.2f},{728:.2f} "
        f"Q {630:.2f},{704:.2f} {B_b[0] + 18:.2f},{B_b[1] - 4:.2f} Z"
    )
    parts.append(f'<path d="{u_path}" fill="{PALETTE["film_under"]}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    # Glossy white crease highlights on underside film
    parts.append(
        f'<path d="M 628,690 Q 685,686 732,698 Q 682,700 628,690 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/>'
        f'<path d="M 745,595 Q 778,630 792,664 Q 765,638 745,595 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/>'
    )

    # 2. Acrylic 2mm thickness edges (left-front L->B and right-front B->R)
    parts.append(poly([L, B, B_b, L_b], PALETTE["acrylic_edge"], INK, 2.4))
    parts.append(poly([B, R, R_b, B_b], PALETTE["acrylic_edge"], INK, 2.4))

    # 3. Exposed right half of clear acrylic top face
    parts.append(poly([B, P_top, R], "#FFFFFF", "none", 0.0))  # base white
    parts.append(poly([B, P_top, R], PALETTE["acrylic_face"], INK, 2.6))

    # Diagonal glass sheen lines on exposed clear acrylic (matching 03.png)
    sheen_lines = [
        ((625, 474), (826, 408)),
        ((668, 486), (812, 439)),
        ((855, 398), (898, 384)),
        ((838, 326), (846, 392)),
        ((848, 422), (854, 478)),
    ]
    for s0, s1 in sheen_lines:
        parts.append(
            f'<line x1="{s0[0]}" y1="{s0[1]}" x2="{s1[0]}" y2="{s1[1]}" '
            f'stroke="{PALETTE["acrylic_sheen"]}" stroke-width="2.2" stroke-linecap="round"/>'
        )

    # 4. Left adhered top protective film triangle (L -> B -> P_top -> T)
    parts.append(poly([L, B, P_top, T], PALETTE["film_top"], INK, 2.6))

    # 5. Lifted curling top protective film flap (from B curving up to C_lift, across to P_top, sweeping down to B)
    flap_path = (
        f"M {B[0]:.2f},{B[1]:.2f} "
        f"C {462:.2f},{540:.2f} {454:.2f},{360:.2f} {C_lift[0]:.2f},{C_lift[1]:.2f} "
        f"Q {580:.2f},{254:.2f} {P_top[0]:.2f},{P_top[1]:.2f} "
        f"C {635:.2f},{385:.2f} {535:.2f},{585:.2f} {B[0]:.2f},{B[1]:.2f} Z"
    )
    parts.append(f'<path d="{flap_path}" fill="{PALETTE["film_flap"]}" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')

    # Crisp white glossy film wrinkle/highlight ribbons on the curled flap
    wrinkles = [
        "M 498,290 Q 595,286 676,320 Q 606,308 498,290 Z",
        "M 562,368 Q 572,425 604,462 Q 576,442 562,368 Z",
        "M 505,468 Q 535,515 548,554 Q 524,522 505,468 Z",
        "M 454,328 Q 466,356 462,374 Q 452,350 454,328 Z",
    ]
    for wp in wrinkles:
        parts.append(f'<path d="{wp}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>')

    # 6. Three bold solid-black curved IKEA arrows (matching 03.png positions, NO HAND)
    # Arrow 1: curving upward at top lifted film edge
    parts.append(svg_curved_arrow((575, 252), (618, 212), (612, 156), (578, 120), w0=3.4, w1=8.6, head_len=25.0, head_hw=18.0))
    # Arrow 2: curving leftward across curled top film
    parts.append(svg_curved_arrow((502, 412), (464, 464), (392, 474), (326, 456), w0=3.4, w1=8.6, head_len=25.0, head_hw=18.0))
    # Arrow 3: curving down-right from underside peeling film
    parts.append(svg_curved_arrow((702, 650), (748, 682), (748, 728), (712, 766), w0=3.2, w1=8.2, head_len=24.0, head_hw=17.0))

    return wrap_svg(W, H, "\n  ".join(parts))


# ────────────────────────────────────────────────────────────────────
# STEP 04: 5-layer 30-deg isometric exploded stack (frame face down at bottom)
# ────────────────────────────────────────────────────────────────────
def build_step04() -> str:
    W, H = 896, 1200
    COS30 = math.cos(math.radians(30))
    SIN30 = math.sin(math.radians(30))
    S = 1.04  # px per mm

    # Isometric orientation matching 04.png:
    # +u (board width) goes UP-RIGHT (+COS30, -SIN30)
    # +v (board height) goes UP-LEFT (-COS30, -SIN30)
    # +z (exploded height) goes STRAIGHT UP (0, -1)
    OX, OY = W / 2.0, 968.0

    def iso(u: float, v: float, z: float) -> tuple[float, float]:
        x = OX + (u * COS30 - v * COS30) * S
        y = OY - (u * SIN30 + v * SIN30) * S - z * S
        return x, y

    def draw_box(
        u0: float, u1: float, v0: float, v1: float, z0: float, z1: float,
        c_top: str, c_left: str, c_right: str, sw: float = 2.0, alpha: float = 1.0
    ) -> list[str]:
        """Draw visible faces of an axis-aligned box in painter's order (front-left u=u0?, wait: check visibility!)."""
        # With +u up-right and +v up-left:
        # Lowest screen-Y is backmost (+u,+v). Highest screen-Y is frontmost (-u,-v).
        # Visible vertical faces from viewer (-u, -v):
        #   1. v = v0 face (front-right facing down-right)
        #   2. u = u0 face (front-left facing down-left)
        #   3. z = z1 face (top face)
        op = f'fill-opacity="{alpha:.2f}"' if alpha < 1.0 else ""
        f_left = [iso(u0, v0, z0), iso(u0, v1, z0), iso(u0, v1, z1), iso(u0, v0, z1)]
        f_right = [iso(u0, v0, z0), iso(u1, v0, z0), iso(u1, v0, z1), iso(u0, v0, z1)]
        f_top = [iso(u0, v0, z1), iso(u1, v0, z1), iso(u1, v1, z1), iso(u0, v1, z1)]
        return [
            poly(f_left, c_left, INK, sw, op),
            poly(f_right, c_right, INK, sw, op),
            poly(f_top, c_top, INK, sw, op),
        ]

    def draw_hollow_collar(
        u_in0: float, u_in1: float, v_in0: float, v_in1: float,
        u_out0: float, u_out1: float, v_out0: float, v_out1: float,
        z0: float, z1: float,
        c_top: str, c_left: str, c_right: str, c_in_left: str, c_in_right: str,
        sw: float = 2.2,
    ) -> list[str]:
        """Draw a hollow rectangular collar cleanly back-to-front."""
        out: list[str] = []
        # 1. Inner back walls (visible looking into the open top!)
        # Inner wall at v = v_in1 (back-left inner wall facing front-right)
        in_v1 = [iso(u_in0, v_in1, z0), iso(u_in1, v_in1, z0), iso(u_in1, v_in1, z1), iso(u_in0, v_in1, z1)]
        # Inner wall at u = u_in1 (back-right inner wall facing front-left)
        in_u1 = [iso(u_in1, v_in0, z0), iso(u_in1, v_in1, z0), iso(u_in1, v_in1, z1), iso(u_in1, v_in0, z1)]
        out.append(poly(in_v1, c_in_left, INK, sw))
        out.append(poly(in_u1, c_in_right, INK, sw))

        # 2. Outer front faces: u = u_out0 (front-left) and v = v_out0 (front-right)
        out_u0 = [iso(u_out0, v_out0, z0), iso(u_out0, v_out1, z0), iso(u_out0, v_out1, z1), iso(u_out0, v_out0, z1)]
        out_v0 = [iso(u_out0, v_out0, z0), iso(u_out1, v_out0, z0), iso(u_out1, v_out0, z1), iso(u_out0, v_out0, z1)]
        out.append(poly(out_u0, c_left, INK, sw))
        out.append(poly(out_v0, c_right, INK, sw))

        # 3. Top perimeter rim as 4 pieces or compound evenodd path
        outer_top = [iso(u_out0, v_out0, z1), iso(u_out1, v_out0, z1), iso(u_out1, v_out1, z1), iso(u_out0, v_out1, z1)]
        inner_top = [iso(u_in0, v_in0, z1), iso(u_in0, v_in1, z1), iso(u_in1, v_in1, z1), iso(u_in1, v_in0, z1)]
        d = (
            f"M {outer_top[0][0]:.2f},{outer_top[0][1]:.2f} L {outer_top[1][0]:.2f},{outer_top[1][1]:.2f} "
            f"L {outer_top[2][0]:.2f},{outer_top[2][1]:.2f} L {outer_top[3][0]:.2f},{outer_top[3][1]:.2f} Z "
            f"M {inner_top[0][0]:.2f},{inner_top[0][1]:.2f} L {inner_top[1][0]:.2f},{inner_top[1][1]:.2f} "
            f"L {inner_top[2][0]:.2f},{inner_top[2][1]:.2f} L {inner_top[3][0]:.2f},{inner_top[3][1]:.2f} Z"
        )
        out.append(f'<path d="{d}" fill="{c_top}" fill-rule="evenodd" stroke="{INK}" stroke-width="{sw:.2f}" stroke-linejoin="round"/>')
        return out

    parts: list[str] = []
    hw = FRAME_W_MM / 2.0
    hh = FRAME_H_MM / 2.0
    sw_box = SHEET_W_MM / 2.0
    sh_box = SHEET_H_MM / 2.0
    cw = (FRAME_W_MM - 2 * FRAME_WALL_MM) / 2.0
    ch = (FRAME_H_MM - 2 * FRAME_WALL_MM) / 2.0
    ow = (FRAME_W_MM - 2 * FRAME_FACE_MM) / 2.0
    oh = (FRAME_H_MM - 2 * FRAME_FACE_MM) / 2.0

    # ── LAYER 1 (Bottom): Deep Walnut Outer Frame lying FACE DOWN ──
    z_f0, z_f1 = 0.0, FRAME_D_MM
    z_lip = LIP_DEPTH_MM
    # Bottom inner front lip shelf (visible inside open cavity at z = z_lip)
    lip_outer = [iso(-cw, -ch, z_lip), iso(cw, -ch, z_lip), iso(cw, ch, z_lip), iso(-cw, ch, z_lip)]
    lip_inner = [iso(-ow, -oh, z_lip), iso(-ow, oh, z_lip), iso(ow, oh, z_lip), iso(ow, -oh, z_lip)]
    lip_d = (
        f"M {lip_outer[0][0]:.2f},{lip_outer[0][1]:.2f} L {lip_outer[1][0]:.2f},{lip_outer[1][1]:.2f} "
        f"L {lip_outer[2][0]:.2f},{lip_outer[2][1]:.2f} L {lip_outer[3][0]:.2f},{lip_outer[3][1]:.2f} Z "
        f"M {lip_inner[0][0]:.2f},{lip_inner[0][1]:.2f} L {lip_inner[1][0]:.2f},{lip_inner[1][1]:.2f} "
        f"L {lip_inner[2][0]:.2f},{lip_inner[2][1]:.2f} L {lip_inner[3][0]:.2f},{lip_inner[3][1]:.2f} Z"
    )
    parts.append(f'<path d="{lip_d}" fill="{PALETTE["walnut_ledge"]}" fill-rule="evenodd" stroke="{INK}" stroke-width="2.0" stroke-linejoin="round"/>')
    # Inner bottom-lip vertical drop edges at viewing opening
    parts.append(poly([iso(-ow, oh, 0.0), iso(ow, oh, 0.0), iso(ow, oh, z_lip), iso(-ow, oh, z_lip)], PALETTE["walnut_in_left"], INK, 1.8))
    parts.append(poly([iso(ow, -oh, 0.0), iso(ow, oh, 0.0), iso(ow, oh, z_lip), iso(ow, -oh, z_lip)], PALETTE["walnut_in_right"], INK, 1.8))
    # Main hollow frame collar walls + top rim
    parts.extend(
        draw_hollow_collar(
            -cw, cw, -ch, ch,
            -hw, hw, -hh, hh,
            z_f0, z_f1,
            PALETTE["walnut_top"], PALETTE["walnut_left"], PALETTE["walnut_right"],
            PALETTE["walnut_in_left"], PALETTE["walnut_in_right"],
            sw=2.4,
        )
    )
    # 45-degree miter lines on top walnut rim
    for (u_o, v_o), (u_i, v_i) in [
        ((-hw, -hh), (-cw, -ch)),
        ((hw, -hh), (cw, -ch)),
        ((hw, hh), (cw, ch)),
        ((-hw, hh), (-cw, ch)),
    ]:
        p_a, p_b = iso(u_o, v_o, z_f1), iso(u_i, v_i, z_f1)
        parts.append(f'<line x1="{p_a[0]:.2f}" y1="{p_a[1]:.2f}" x2="{p_b[0]:.2f}" y2="{p_b[1]:.2f}" stroke="{INK}" stroke-width="1.8"/>')

    # ── LAYER 2: 2 mm Clear Acrylic Cover ──
    z_ac = 160.0
    parts.extend(
        draw_box(
            -sw_box, sw_box, -sh_box, sh_box, z_ac, z_ac + 4.0,
            PALETTE["acrylic_trans"], PALETTE["acrylic_edge"], PALETTE["acrylic_edge"],
            sw=2.2, alpha=0.84,
        )
    )
    # Glass sheen lines on top face of acrylic
    for (u0, v0), (u1, v1) in [
        ((-110, -50), (-30, 55)),
        ((-95, -55), (-15, 50)),
        ((35, -35), (125, 45)),
        ((60, 15), (140, -25)),
    ]:
        pa, pb = iso(u0, v0, z_ac + 4.0), iso(u1, v1, z_ac + 4.0)
        parts.append(f'<line x1="{pa[0]:.2f}" y1="{pa[1]:.2f}" x2="{pb[0]:.2f}" y2="{pb[1]:.2f}" stroke="{PALETTE["acrylic_sheen"]}" stroke-width="1.8" stroke-linecap="round"/>')

    # ── LAYER 3: Hollow Front Spacer Bars (15 mm tall, 3 mm wall) ──
    z_sp = 295.0
    sp_w = 5.5  # slightly emphasized from 3mm so walls read clearly at manual scale
    parts.extend(
        draw_hollow_collar(
            -sw_box + sp_w, sw_box - sp_w, -sh_box + sp_w, sh_box - sp_w,
            -sw_box, sw_box, -sh_box, sh_box,
            z_sp, z_sp + FRONT_SPACER_T_MM * 1.35,
            PALETTE["spacer_top"], PALETTE["spacer_left"], PALETTE["spacer_right"],
            PALETTE["spacer_left"], PALETTE["spacer_right"],
            sw=2.2,
        )
    )

    # ── LAYER 4: Loaded 4x2 Mid-Board FACE DOWN (back face UP, matching Step 02!) ──
    z_mb = 455.0
    mb_t = 5.5
    parts.extend(
        draw_box(
            -sw_box, sw_box, -sh_box, sh_box, z_mb, z_mb + mb_t,
            PALETTE["birch_face"], PALETTE["birch_edge"], PALETTE["birch_edge"],
            sw=2.3,
        )
    )
    # 8 horizontal slots on mid-board in isometric coords:
    # Row 1 at high +v (top of board in Step 02), Row 2 at lower v.
    z_mb_top = z_mb + mb_t
    iso_cols = [-130.5, -43.5, 43.5, 130.5]
    iso_rows = [58.0, -48.0]  # Row 1 (back-upper), Row 2 (front-lower)
    for r_v in iso_rows:
        for c_u in iso_cols:
            s_pts = [
                iso(c_u - 21.0, r_v - 3.0, z_mb_top),
                iso(c_u + 21.0, r_v - 3.0, z_mb_top),
                iso(c_u + 21.0, r_v + 3.0, z_mb_top),
                iso(c_u - 21.0, r_v + 3.0, z_mb_top),
            ]
            parts.append(poly(s_pts, PALETTE["birch_slot"], INK, 1.6))

    # Row 1 Cols 2, 3, 4 (next 3 slots) taped ribbons matching Step 02! (Col 1 empty)
    for c_u in iso_cols[1:]:
        rib_pts = [
            iso(c_u - 12.0, iso_rows[0] - 1.0, z_mb_top),
            iso(c_u + 12.0, iso_rows[0] - 1.0, z_mb_top),
            iso(c_u + 12.0, iso_rows[0] - 58.0, z_mb_top),
            iso(c_u - 12.0, iso_rows[0] - 58.0, z_mb_top),
        ]
        tape_pts = [
            iso(c_u - 24.0, iso_rows[0] - 16.0, z_mb_top),
            iso(c_u + 24.0, iso_rows[0] - 16.0, z_mb_top),
            iso(c_u + 24.0, iso_rows[0] - 32.0, z_mb_top),
            iso(c_u - 24.0, iso_rows[0] - 32.0, z_mb_top),
        ]
        parts.append(poly(rib_pts, PALETTE["ribbon"], INK, 1.8))
        parts.append(poly(tape_pts, PALETTE["tape"], INK, 1.7))

    # ── LAYER 5 (Top): Two-layer Backboard (4 mm Plywood base + 11x15 mm Pine frame, NO turn-buttons) ──
    z_bb = 670.0
    ply_t = 6.0
    pine_t = 14.0
    # Lower 4 mm plywood sheet
    parts.extend(
        draw_box(
            -sw_box, sw_box, -sh_box, sh_box, z_bb, z_bb + ply_t,
            PALETTE["ply_face"], PALETTE["ply_face"], PALETTE["birch_edge"],
            sw=2.2,
        )
    )
    # Upper 11 x 15 mm hollow pinewood perimeter frame sitting on top of the plywood
    bw_in_u = sw_box - BACKBOARD_FRAME_W_MM
    bw_in_v = sh_box - BACKBOARD_FRAME_W_MM
    parts.extend(
        draw_hollow_collar(
            -bw_in_u, bw_in_u, -bw_in_v, bw_in_v,
            -sw_box, sw_box, -sh_box, sh_box,
            z_bb + ply_t, z_bb + ply_t + pine_t,
            PALETTE["pine_top"], PALETTE["pine_left"], PALETTE["pine_right"],
            PALETTE["pine_in"], PALETTE["pine_in"],
            sw=2.3,
        )
    )
    # Butt-joint lines on top pine frame (top/bottom full width, sides fit between)
    for u_j in (-bw_in_u, bw_in_u):
        for v_a, v_b in ((-sh_box, -bw_in_v), (bw_in_v, sh_box)):
            # Actually top/bottom are full width -> horizontal lines along u at v = +/- bw_in_v from u=-sw_box to -bw_in_u? No, from -sw_box to +sw_box!
            pass
    for v_j in (-bw_in_v, bw_in_v):
        for u_a, u_b in ((-sw_box, -bw_in_u), (bw_in_u, sw_box)):
            pa, pb = iso(u_a, v_j, z_bb + ply_t + pine_t), iso(u_b, v_j, z_bb + ply_t + pine_t)
            parts.append(f'<line x1="{pa[0]:.2f}" y1="{pa[1]:.2f}" x2="{pb[0]:.2f}" y2="{pb[1]:.2f}" stroke="{INK}" stroke-width="1.7"/>')

    # Bold solid-black vertical DOWNWARD block arrow above backboard
    top_center = iso(0.0, 0.0, z_bb + ply_t + pine_t)
    parts.append(svg_block_arrow(cx=W / 2.0, y_top=46.0, y_bot=top_center[1] + 8.0, shaft_hw=13.0, head_h=38.0, head_hw=30.0))

    return wrap_svg(W, H, "\n  ".join(parts))


# ────────────────────────────────────────────────────────────────────
# STEP 05: Hang straight on the wall — ONE centered nail + TRIPLE-THICKNESS zoom lip
# ────────────────────────────────────────────────────────────────────
def build_step05() -> str:
    W, H = 1200, 896
    COS30 = math.cos(math.radians(30))
    SIN30 = math.sin(math.radians(30))

    # Isometric axes for wall view:
    # +u goes UP-RIGHT along the wall (+COS30, -SIN30)
    # +v goes DOWN-RIGHT OUTWARD from wall toward viewer (+COS30, +SIN30)
    # +z goes STRAIGHT UP (0, -1)
    def wall_iso(u: float, v: float, z: float) -> tuple[float, float]:
        x = 120.0 + u * COS30 + v * COS30
        y = 755.0 - u * SIN30 + v * SIN30 - z
        return x, y

    parts: list[str] = []

    # ── 1. Vertical Wall Slab (single nail centered horizontally in the middle) ──
    wall_u0, wall_u1 = 0.0, 490.0
    wall_z0, wall_z1 = 0.0, 505.0
    wall_t = 26.0  # wall thickness extending back (-v)
    # Left thickness edge (u = wall_u0, v in [-wall_t, 0])
    parts.append(
        poly(
            [wall_iso(wall_u0, -wall_t, wall_z0), wall_iso(wall_u0, 0, wall_z0),
             wall_iso(wall_u0, 0, wall_z1), wall_iso(wall_u0, -wall_t, wall_z1)],
            PALETTE["wall_edge"], INK, 2.4,
        )
    )
    # Top thickness edge (z = wall_z1, v in [-wall_t, 0])
    parts.append(
        poly(
            [wall_iso(wall_u0, -wall_t, wall_z1), wall_iso(wall_u1, -wall_t, wall_z1),
             wall_iso(wall_u1, 0, wall_z1), wall_iso(wall_u0, 0, wall_z1)],
            PALETTE["wall_edge"], INK, 2.4,
        )
    )
    # Front wall face (v = 0)
    parts.append(
        poly(
            [wall_iso(wall_u0, 0, wall_z0), wall_iso(wall_u1, 0, wall_z0),
             wall_iso(wall_u1, 0, wall_z1), wall_iso(wall_u0, 0, wall_z1)],
            PALETTE["wall_front"], INK, 2.6,
        )
    )

    # ONLY ONE nail centered in the exact middle of the wall (u = 245, z = 295)
    nail_u, nail_z = 245.0, 295.0
    n_base = wall_iso(nail_u, 0.0, nail_z)
    n_tip = wall_iso(nail_u, 40.0, nail_z + 10.0)
    # Angled shaft + round steel head
    dx, dy = n_tip[0] - n_base[0], n_tip[1] - n_base[1]
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln * 3.0, dx / ln * 3.0
    parts.append(
        poly(
            [(n_base[0] + nx, n_base[1] + ny), (n_tip[0] + nx, n_tip[1] + ny),
             (n_tip[0] - nx, n_tip[1] - ny), (n_base[0] - nx, n_base[1] - ny)],
            PALETTE["nail_shaft"], INK, 2.0,
        )
    )
    parts.append(f'<circle cx="{n_tip[0]:.2f}" cy="{n_tip[1]:.2f}" r="6.2" fill="{PALETTE["nail_head"]}" stroke="{INK}" stroke-width="2.0"/>')

    # ── 2. Assembled Walnut Display Frame in front of the wall (facing outward) ──
    fu0, fu1 = 68.0, 422.0   # 354 units wide, centered around u = 245
    fz0, fz1 = 148.0, 384.0  # 236 units tall
    fv_back = 185.0
    fv_front = 228.0         # 43 units shadow-box depth
    lip = 16.0

    # Left outer walnut wall (u = fu0, v in [fv_back, fv_front])
    parts.append(
        poly(
            [wall_iso(fu0, fv_back, fz0), wall_iso(fu0, fv_front, fz0),
             wall_iso(fu0, fv_front, fz1), wall_iso(fu0, fv_back, fz1)],
            PALETTE["walnut_left"], INK, 2.5,
        )
    )
    # Top outer walnut wall (z = fz1, v in [fv_back, fv_front])
    parts.append(
        poly(
            [wall_iso(fu0, fv_back, fz1), wall_iso(fu1, fv_back, fz1),
             wall_iso(fu1, fv_front, fz1), wall_iso(fu0, fv_front, fz1)],
            PALETTE["walnut_top"], INK, 2.5,
        )
    )
    # Front viewing opening interior: recessed birch board with 3 subtle gold medals & navy ribbons
    ov_depth = fv_front - 16.0
    parts.append(
        poly(
            [wall_iso(fu0 + lip, ov_depth, fz0 + lip), wall_iso(fu1 - lip, ov_depth, fz0 + lip),
             wall_iso(fu1 - lip, ov_depth, fz1 - lip), wall_iso(fu0 + lip, ov_depth, fz1 - lip)],
            PALETTE["birch_face"], INK, 2.0,
        )
    )
    # Subtle 3 medals + ribbons inside the display frame (matching Step 01)
    for col_u in (142.0, 206.0, 270.0):
        # Ribbon
        r_pts = [
            wall_iso(col_u - 8.0, ov_depth, fz1 - lip - 20.0),
            wall_iso(col_u + 8.0, ov_depth, fz1 - lip - 20.0),
            wall_iso(col_u + 8.0, ov_depth, fz1 - lip - 40.0),
            wall_iso(col_u - 8.0, ov_depth, fz1 - lip - 40.0),
        ]
        parts.append(poly(r_pts, PALETTE["ribbon"], INK, 1.4))
        mc = wall_iso(col_u, ov_depth, fz1 - lip - 64.0)
        parts.append(
            f'<ellipse cx="{mc[0]:.2f}" cy="{mc[1]:.2f}" rx="20.0" ry="24.0" '
            f'transform="rotate(-14 {mc[0]:.2f} {mc[1]:.2f})" '
            f'fill="{PALETTE["medal_disc"]}" stroke="{INK}" stroke-width="1.6"/>'
        )

    # Clear acrylic glass tint over opening + diagonal sheen
    parts.append(
        poly(
            [wall_iso(fu0 + lip, fv_front - 5.0, fz0 + lip), wall_iso(fu1 - lip, fv_front - 5.0, fz0 + lip),
             wall_iso(fu1 - lip, fv_front - 5.0, fz1 - lip), wall_iso(fu0 + lip, fv_front - 5.0, fz1 - lip)],
            PALETTE["acrylic_trans"], "none", 0.0, 'fill-opacity="0.32"',
        )
    )
    # Inner bottom & right shadow-box rabbet walls visible inside front opening
    parts.append(
        poly(
            [wall_iso(fu0 + lip, ov_depth, fz0 + lip), wall_iso(fu1 - lip, ov_depth, fz0 + lip),
             wall_iso(fu1 - lip, fv_front, fz0 + lip), wall_iso(fu0 + lip, fv_front, fz0 + lip)],
            PALETTE["walnut_ledge"], INK, 1.8,
        )
    )
    parts.append(
        poly(
            [wall_iso(fu1 - lip, ov_depth, fz0 + lip), wall_iso(fu1 - lip, fv_front, fz0 + lip),
             wall_iso(fu1 - lip, fv_front, fz1 - lip), wall_iso(fu1 - lip, ov_depth, fz1 - lip)],
            PALETTE["walnut_in_right"], INK, 1.8,
        )
    )

    # Front walnut bezel (even-odd) + 45-degree miter lines
    f_out = [wall_iso(fu0, fv_front, fz0), wall_iso(fu1, fv_front, fz0), wall_iso(fu1, fv_front, fz1), wall_iso(fu0, fv_front, fz1)]
    f_in = [wall_iso(fu0 + lip, fv_front, fz0 + lip), wall_iso(fu0 + lip, fv_front, fz1 - lip), wall_iso(fu1 - lip, fv_front, fz1 - lip), wall_iso(fu1 - lip, fv_front, fz0 + lip)]
    bezel_d = (
        f"M {f_out[0][0]:.2f},{f_out[0][1]:.2f} L {f_out[1][0]:.2f},{f_out[1][1]:.2f} "
        f"L {f_out[2][0]:.2f},{f_out[2][1]:.2f} L {f_out[3][0]:.2f},{f_out[3][1]:.2f} Z "
        f"M {f_in[0][0]:.2f},{f_in[0][1]:.2f} L {f_in[1][0]:.2f},{f_in[1][1]:.2f} "
        f"L {f_in[2][0]:.2f},{f_in[2][1]:.2f} L {f_in[3][0]:.2f},{f_in[3][1]:.2f} Z"
    )
    parts.append(f'<path d="{bezel_d}" fill="{PALETTE["walnut_top"]}" fill-rule="evenodd" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    for idx_a, idx_b in [(0, 0), (1, 3), (2, 2), (3, 1)]:
        parts.append(f'<line x1="{f_out[idx_a][0]:.2f}" y1="{f_out[idx_a][1]:.2f}" x2="{f_in[idx_b][0]:.2f}" y2="{f_in[idx_b][1]:.2f}" stroke="{INK}" stroke-width="1.8"/>')

    # ONE bold centered hooking arrow arching cleanly ABOVE the frame back toward the single center nail
    arr_start = wall_iso(245.0, fv_front - 6.0, fz1 + 52.0)
    arr_p1 = wall_iso(245.0, fv_back - 30.0, fz1 + 128.0)
    arr_p2 = wall_iso(245.0, 82.0, nail_z + 158.0)
    arr_end = wall_iso(245.0, 44.0, nail_z + 48.0)
    parts.append(svg_curved_arrow(arr_start, arr_p1, arr_p2, arr_end, w0=3.4, w1=9.2, head_len=26.0, head_hw=19.0))

    # ── 3. Top-Right Circular Zoom-In Callout: TRIPLE-THICKNESS Back Hanging Lip ──
    ZC_X, ZC_Y, ZC_R = 965.0, 252.0, 162.0
    # Triangular pointer leader pointing directly toward the single center nail head
    leader_pts = [
        (n_tip[0] + 20.0, n_tip[1] - 4.0),
        (ZC_X - ZC_R * 0.88, ZC_Y + 12.0),
        (ZC_X - ZC_R * 0.72, ZC_Y + 62.0),
    ]
    parts.append(poly(leader_pts, "#FFFFFF", INK, 2.4))

    # Clipped zoom circle contents
    parts.append(
        f'<defs><clipPath id="zoom-clip"><circle cx="{ZC_X:.2f}" cy="{ZC_Y:.2f}" r="{ZC_R - 1.5:.2f}"/></clipPath></defs>'
    )
    zoom_inner: list[str] = [f'<circle cx="{ZC_X:.2f}" cy="{ZC_Y:.2f}" r="{ZC_R:.2f}" fill="#FFFFFF"/>']

    # Vertical wall section on left side of zoom circle
    wall_x0, wall_x1 = ZC_X - 122.0, ZC_X - 48.0
    zoom_inner.append(
        f'<rect x="{wall_x0:.2f}" y="{ZC_Y - ZC_R - 10:.2f}" width="{wall_x1 - wall_x0:.2f}" '
        f'height="{ZC_R * 2 + 20:.2f}" fill="{PALETTE["wall_section"]}" stroke="{INK}" stroke-width="2.4"/>'
    )

    # Single angled steel nail protruding rightward from the wall into the open pocket under the lip
    zn_x0, zn_y0 = wall_x0 - 28.0, ZC_Y + 66.0
    zn_x1, zn_y1 = wall_x1 + 40.0, ZC_Y + 48.0
    zoom_inner.append(
        f'<polygon points="{zn_x0:.2f},{zn_y0:.2f} {zn_x1:.2f},{zn_y1 - 4.5:.2f} '
        f'{zn_x1:.2f},{zn_y1 + 4.5:.2f} {zn_x0:.2f},{zn_y0 + 3.0:.2f}" '
        f'fill="{PALETTE["nail_shaft"]}" stroke="{INK}" stroke-width="2.0" stroke-linejoin="round"/>'
    )
    zoom_inner.append(
        f'<rect x="{zn_x1 - 2.0:.2f}" y="{zn_y1 - 10.0:.2f}" width="6.5" height="20.0" rx="2.0" '
        f'transform="rotate(-14 {zn_x1:.2f} {zn_y1:.2f})" '
        f'fill="{PALETTE["nail_head"]}" stroke="{INK}" stroke-width="2.0"/>'
    )

    # TRIPLE-THICKNESS back hanging lip of the frame hooking straight down onto the nail!
    # The nail sits cleanly in the pocket (wall_x1 .. lip_x_in) directly BELOW the 38px-thick solid wood lip,
    # clearing the inner plywood backing sheet at x = lip_x_in!
    lip_x_back = wall_x1 + 12.0   # rear face of frame just clearing the wall
    lip_x_in = lip_x_back + 38.0  # TRIPLE-THICKNESS chunky solid wood lip (38px wide!)
    lip_y_top = ZC_Y - 60.0
    lip_y_hook_bot = ZC_Y + 22.0  # hovers cleanly above nail shaft ready to drop straight down onto it!
    ply_x_in = lip_x_in + 14.0

    # Outer walnut shell top + front-right wall
    walnut_sec = [
        (lip_x_back, lip_y_top),
        (ZC_X + 132.0, lip_y_top),
        (ZC_X + 132.0, ZC_Y + ZC_R + 10.0),
        (ZC_X + 106.0, ZC_Y + ZC_R + 10.0),
        (ZC_X + 106.0, lip_y_top + 26.0),
        (lip_x_back, lip_y_top + 26.0),
    ]
    zoom_inner.append(poly(walnut_sec, PALETTE["walnut_top"], INK, 2.4))

    # Inner plywood backing sheet (recessed cleanly behind the triple-thickness lip, clearing the nail head!)
    ply_sec = [
        (lip_x_in, lip_y_top + 26.0),
        (ply_x_in, lip_y_top + 26.0),
        (ply_x_in, ZC_Y + ZC_R + 10.0),
        (lip_x_in, ZC_Y + ZC_R + 10.0),
    ]
    zoom_inner.append(poly(ply_sec, PALETTE["ply_face"], INK, 2.2))

    # Chunky TRIPLE-THICKNESS pinewood rear hanging lip rail (hooks straight down onto the nail)
    pine_lip = [
        (lip_x_back, lip_y_top + 26.0),
        (lip_x_in, lip_y_top + 26.0),
        (lip_x_in, lip_y_hook_bot),
        (lip_x_back, lip_y_hook_bot),
    ]
    zoom_inner.append(poly(pine_lip, PALETTE["pine_top"], INK, 2.5))
    # Subtle triple-lamination bond lines showing 3x thickness clearly
    for lam_x in (lip_x_back + 12.6, lip_x_back + 25.3):
        zoom_inner.append(
            f'<line x1="{lam_x:.2f}" y1="{lip_y_top + 28.0:.2f}" x2="{lam_x:.2f}" y2="{lip_y_hook_bot - 2.0:.2f}" '
            f'stroke="{INK}" stroke-width="1.3" stroke-dasharray="4 3" opacity="0.55"/>'
        )

    # Bold solid-black downward arrow showing the triple-thickness lip dropping onto the nail
    zoom_inner.append(
        svg_block_arrow(
            cx=lip_x_back + 19.0,
            y_top=ZC_Y - 122.0,
            y_bot=lip_y_top - 4.0,
            shaft_hw=7.0,
            head_h=20.0,
            head_hw=16.0,
        )
    )

    parts.append(f'<g clip-path="url(#zoom-clip)">\n    ' + "\n    ".join(zoom_inner) + '\n  </g>')
    parts.append(f'<circle cx="{ZC_X:.2f}" cy="{ZC_Y:.2f}" r="{ZC_R:.2f}" fill="none" stroke="{INK}" stroke-width="3.0"/>')

    return wrap_svg(W, H, "\n  ".join(parts))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

    specs = [
        ("01_position_medals_thread_slots", 1200, 896, build_step01),
        ("02_tape_ribbons_back", 1200, 896, build_step02),
        ("03_peel_cover", 1200, 896, build_step03),
        ("04_stack_and_lock", 896, 1200, build_step04),
        ("05_hang_on_wall", 1200, 896, build_step05),
    ]
    for stem, w, h, builder in specs:
        svg_path = OUT_DIR / f"{stem}.svg"
        png_path = OUT_DIR / f"{stem}.png"
        svg_path.write_text(builder(), encoding="utf-8")
        rasterize_svg(svg_path, png_path, w, h)


if __name__ == "__main__":
    main()
