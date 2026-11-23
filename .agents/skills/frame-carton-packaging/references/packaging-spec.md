# Packaging Engineering Spec & Cost Reference (`medal_8_sq`)

Reference specification for parametric carton and EPE protective wrap modeling in `build123d`.

---

## 1. Cost Optimization Comparison

### Carton Structure Comparison (China OEM Production, ~455 × 315 × 85 mm Inner)

| Style | Flute / Spec | Die-Cut Tooling (刀模费) | Relative Board Area | Est. China OEM Unit Price (500+ pcs) | Best Use Case |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **FEFCO 0201 RSC (平口箱)** | **3-ply B-flute (`3.0 mm`, `K=K`)** | **¥0** (slotter-creaser) | **1.00× (baseline)** | **¥3.2 – ¥4.5** | Inner unit box inside a 5-ply master carton (4–6 pcs/outer box) |
| **FEFCO 0201 RSC (平口箱)** *(Recommended Standalone)* | **5-ply BE-flute (`4.5 mm`)** | **¥0** (slotter-creaser) | **1.00×** | **¥4.8 – ¥6.8** | Direct e-commerce / single-unit parcel shipping (high puncture & crush strength, zero mold fee) |
| **FEFCO 0201 RSC (平口箱)** | **5-ply BC-flute (`6.0 mm`)** | **¥0** (slotter-creaser) | **1.00×** | **¥5.5 – ¥7.8** | Heavy-duty export / rough courier handling |
| **FEFCO 0427 Mailer (飞机盒)** | 3-ply E/B-flute (`2.0–3.0 mm`) | ¥300 – ¥600 | ~1.25–1.35× | ¥6.5 – ¥9.5 | Branded retail unboxing; higher board waste and tooling cost |
| **Two-Piece Telescoping Box (天地盖)** | 5-ply / greyboard | ¥500 – ¥1,200 | ~1.45–1.60× | ¥10.0 – ¥16.0+ | Retail gift presentation; overkill for shipping protection |

### Key Cost-Saving Levers

1. **Zero-Tooling Box (`FEFCO 0201`)**: Uses adjustable rotary slotter-creasers — **¥0 die-cut mold cost** even for low MOQs (`100–300` units) and eliminates double-sidewall material waste present in `0427` mailers.
2. **Zero-Tooling EPE Protection**: Replaces custom die-cut full-perimeter foam trays (which waste ~60% of the foam center cutout and incur `¥500–¥1,500` foam die charges) with:
   - **Standard EPE pearl cotton bag** (`2.0 mm` off-the-shelf sleeve/bag)
   - **4× Standard L-profile EPE corner guards** (`15.0 mm` wall, `75.0 mm` leg — stock profile cut to `59.0 mm` length)
   - **2× Straight guillotine-cut EPE pads** (`12.0 mm` sheets, zero scrap)
3. **Volumetric Weight Control**: Keeping the outer height slim (`103.0 mm` in 5-ply BE-flute, or `97.0 mm` in 3-ply B-flute) yields a courier volumetric weight of **`~2.58 kg`** (`46.4 × 32.4 × 10.3 / 6000`) or **`~3.10 kg`** (`/ 5000`).
4. **Master Carton Consolidation**: When shipping wholesale/freight batches (`4–6` frames per outer carton), downgrade individual unit boxes to **3-ply heavy B-flute (`3.0 mm`)** and put the crush strength in a single **5-ply BC-flute** outer master carton.

---

## 2. Parametric Stack Formulas

All packaging dimensions derive directly from the frame's outer bounding dimensions:

| Parameter | Default Value | Description |
| :--- | :---: | :--- |
| `FRAME_OUTER_W` | `414.0 mm` | Frame width along `X` (from `src_medal_8_sq/lib/dims.py`) |
| `FRAME_OUTER_H` | `276.0 mm` | Frame height along `Z` (from `src_medal_8_sq/lib/dims.py`) |
| `FRAME_DEPTH` | `46.0 mm` | Hardwood frame depth along `Y` (`0.0` to `46.0`) |
| `FRAME_OUTER_CORNER_R` | `9.0 mm` | Frame outer corner radius in `XZ` |
| `REAR_HARDWARE_PROTRUSION` | `8.0 mm` | Envelope for rear D-ring hangers (`7.67 mm` actual protrusion past `Y = 46.0`) |
| `FRAME_ENVELOPE_D` | `FRAME_DEPTH + REAR_HARDWARE_PROTRUSION` | `54.0 mm` total frame + hardware depth (`Y: 0.0 → 54.0`) |
| `EPE_BAG_T` | `2.0 mm` | EPE pearl cotton bag wall thickness (range `2.0–3.0 mm`) |
| `WRAP_FIT_CLEARANCE` | `0.5 mm` | Slip clearance per side inside the EPE bag |
| `CORNER_WALL_T` | `15.0 mm` | L-profile corner protector perimeter wall thickness (`X`, `Z`) |
| `CORNER_LEG_LEN` | `75.0 mm` | Outer leg length of each L-corner along `X` and `Z` |
| `FRONT_PAD_T` | `12.0 mm` | Front EPE foam pad thickness (range `10.0–15.0 mm`) |
| `REAR_PAD_T` | `12.0 mm` | Rear EPE foam pad thickness (range `10.0–15.0 mm`) |
| `PACK_CLEARANCE` | `2.0 mm` | Minimum slip clearance per side inside carton (`X`, `Z`) and `1.0 mm` per face (`Y`) |
| `FLAP_SEAM_GAP` | `2.0 mm` | Gap between closed FEFCO 0201 major flaps so seams render cleanly |
| `WALL_T` | `4.5 mm` (5-ply BE) / `3.0 mm` (3-ply B) | Corrugated board wall thickness |

### Derived Dimensions

```python
# 1. EPE Bag
BAG_INNER_W = FRAME_OUTER_W + 2.0 * WRAP_FIT_CLEARANCE
BAG_INNER_H = FRAME_OUTER_H + 2.0 * WRAP_FIT_CLEARANCE
BAG_INNER_D = FRAME_ENVELOPE_D + 2.0 * WRAP_FIT_CLEARANCE

BAG_OUTER_W = BAG_INNER_W + 2.0 * EPE_BAG_T
BAG_OUTER_H = BAG_INNER_H + 2.0 * EPE_BAG_T
BAG_OUTER_D = BAG_INNER_D + 2.0 * EPE_BAG_T

# 2. Corner Protectors (flush depth = BAG_OUTER_D)
PROTECTED_W = BAG_OUTER_W + 2.0 * CORNER_WALL_T
PROTECTED_H = BAG_OUTER_H + 2.0 * CORNER_WALL_T
CORNER_DEPTH = BAG_OUTER_D

# 3. Front & Rear Pads (matching PROTECTED_W x PROTECTED_H)
PACK_W = PROTECTED_W
PACK_H = PROTECTED_H
PACK_D = FRONT_PAD_T + BAG_OUTER_D + REAR_PAD_T

# 4. Carton Inner Dimensions (rounded up cleanly to nearest 5 mm if desired)
# For medal_8_sq baseline: 455.0 x 315.0 x 85.0 mm
CARTON_INNER_L = 455.0  # >= PACK_W + 2.0 * PACK_CLEARANCE (453.0 -> 455.0)
CARTON_INNER_W = 315.0  # == PACK_H + 2.0 * PACK_CLEARANCE (315.0)
CARTON_INNER_H = 85.0   # == PACK_D + 2.0 * 1.0 (85.0)

# 5. FEFCO 0201 Outer Dimensions
# L and W add 2 * WALL_T (side walls); H adds 4 * WALL_T (minor + major flap per open face)
CARTON_OUTER_L = CARTON_INNER_L + 2.0 * WALL_T
CARTON_OUTER_W = CARTON_INNER_W + 2.0 * WALL_T
CARTON_OUTER_H = CARTON_INNER_H + 4.0 * WALL_T
```

> **Optional Height Reduction**: If reducing box height further is a priority, replace the flat `12.0 mm` rear pad behind the D-rings with a `15.0 mm` EPE rear sheet seated directly against the bagged frame rear face (`Y = 48.5 mm`) with two local `10 mm`-deep cutouts/relief pockets around the D-ring straps (`X ≈ ±175.7 mm, Z = 184.0 mm`). That reduces `PACK_D` by `~5 mm`, though cutting pockets adds labor/tooling cost.

---

## 3. Worked Baseline Table (`medal_8_sq`: `414.0 × 276.0 × 46.0 mm`)

| Layer / Component | Size `X × Z × Y` (mm) | `X` Range (mm) | `Z` Range (mm) | `Y` Range (mm) | Notes |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Hardwood Frame** (`medal_8_sq`) | `414.0 × 276.0 × 46.0` | `-207.0 … +207.0` | `0.0 … 276.0` | `0.0 … 46.0` | `R9.0` outer corners; `53.67 mm` w/ D-rings (`54.0 mm` env.) |
| **EPE Pearl Cotton Bag** (`2.0 mm`) | `419.0 × 281.0 × 59.0` | `-209.5 … +209.5` | `-2.5 … 278.5` | `-2.5 … 56.5` | `0.5 mm` fit clearance/side; inner cavity `415 × 277 × 55 mm` |
| **4× EPE L-Corner Guards** | `449.0 × 311.0 × 59.0` span | `-224.5 … +224.5` | `-17.5 … 293.5` | `-2.5 … 56.5` | `15.0 mm` wall, `75.0 mm` outer leg, `59.0 mm` depth |
| **Front EPE Foam Pad** (`12.0 mm`) | `449.0 × 311.0 × 12.0` | `-224.5 … +224.5` | `-17.5 … 293.5` | `-14.5 … -2.5` | Protects front PMMA acrylic & walnut face |
| **Rear EPE Foam Pad** (`12.0 mm`) | `449.0 × 311.0 × 12.0` | `-224.5 … +224.5` | `-17.5 … 293.5` | `56.5 … 68.5` | Clears rear D-ring tip (`Y = 53.67 mm`) inside bag |
| **Carton Inner Cavity** | **`455.0 × 315.0 × 85.0`** | `-227.5 … +227.5` | `-19.5 … 295.5` | `-15.5 … 69.5` | `3.0 mm`/side `X`, `2.0 mm`/side `Z`, `1.0 mm`/face `Y` |
| **Carton Outer (5-ply BE `4.5 mm`)** | **`464.0 × 324.0 × 103.0`** | `-232.0 … +232.0` | `-24.0 … 300.0` | `-24.5 … 78.5` | Vol. wt `~2.58 kg` (`÷6000`) / `~3.10 kg` (`÷5000`) |
| **Carton Outer (3-ply B `3.0 mm`)** | **`461.0 × 321.0 × 97.0`** | `-230.5 … +230.5` | `-22.5 … 298.5` | `-21.5 … 75.5` | Master-carton inner box; vol. wt `~2.39 kg` (`÷6000`) |

### Adaptation for `medal_15_sq` (`501.0 × 381.0 × 46.0 mm`)

Using the identical thickness stack (`2.0 mm` EPE bag, `15.0 mm` corner wall, `12.0 mm` front/rear pads, `53.67 mm` rear D-ring envelope):
- EPE Bag outer: `506.0 × 386.0 × 59.0 mm`
- Protected envelope w/ corners & pads: `536.0 × 416.0 × 83.0 mm`
- Carton Inner: **`540.0 × 420.0 × 85.0 mm`**
- Carton Outer (5-ply BE `4.5 mm`): **`549.0 × 429.0 × 103.0 mm`**

---

## 4. `build123d` Modeling & Material Patterns

### Hollow EPE Bag

Model on `bd.Plane.XZ` centered at `(0.0, FRAME_OUTER_H / 2.0)`:
- Extrude outer rounded rectangle `(BAG_OUTER_W, BAG_OUTER_H, corner_r=FRAME_OUTER_CORNER_R + WRAP_FIT_CLEARANCE + EPE_BAG_T)` along `-Y` (`amount=-BAG_OUTER_D` from `Y = -WRAP_FIT_CLEARANCE - EPE_BAG_T`, i.e. `origin=(0, -2.5, 0)`).
- Subtract inner rounded rectangle `(BAG_INNER_W, BAG_INNER_H, corner_r=FRAME_OUTER_CORNER_R + WRAP_FIT_CLEARANCE)` shifted inward by `EPE_BAG_T` (`origin=(0, -0.5, 0)`, `amount=-BAG_INNER_D`).

### L-Profile EPE Corner Protectors

Build one bottom-left L-profile on `bd.Plane.XZ` at `(-PROTECTED_W / 2.0, Z_PROTECTED_MIN)` spanning `[0, CORNER_LEG_LEN] × [0, CORNER_LEG_LEN]` minus the inner cutout `[CORNER_WALL_T, CORNER_LEG_LEN + 1] × [CORNER_WALL_T, CORNER_LEG_LEN + 1]` (or subtracting a rounded rectangle matching `BAG_OUTER_W × BAG_OUTER_H` with `corner_r = FRAME_OUTER_CORNER_R + WRAP_FIT_CLEARANCE + EPE_BAG_T` so the inside of the corner protector conforms cleanly to the bagged rounded corner without interference). Mirror/rotate cleanly to `BR`, `TR`, and `TL`.

### FEFCO 0201 Corrugated Carton

With the frame vertical in `X-Z` and thickness along `Y`, the box's packing openings face `-Y` (front/top lid) and `+Y` (rear/bottom):
- **4 Side Walls**: Span `Y` from `Y_INNER_MIN` to `Y_INNER_MAX` (`CARTON_INNER_H = 85.0 mm`), forming a hollow `CARTON_OUTER_L × CARTON_OUTER_W` perimeter shell around `CARTON_INNER_L × CARTON_INNER_W`.
- **Minor Flaps (Left & Right, `-X` / `+X` walls)**: Hinged at `X = ±CARTON_INNER_L / 2.0` (wall inner/center line) in the inner flap plane (`Y_INNER_MIN - WALL_T` to `Y_INNER_MIN` at front; `Y_INNER_MAX` to `Y_INNER_MAX + WALL_T` at rear). Flap length inward along `X` = `CARTON_INNER_W / 2.0 - 2.0` (standard RSC square minor flap); width along `Z` = `CARTON_INNER_W - 1.0` (`0.5 mm` relief per side).
- **Major Flaps (Top & Bottom, `+Z` / `-Z` walls)**: Seated outside the minor flaps (`Y_INNER_MIN - 2 * WALL_T` to `Y_INNER_MIN - WALL_T` at front; `Y_INNER_MAX + WALL_T` to `Y_INNER_MAX + 2 * WALL_T` at rear). Length along `Z` = `CARTON_OUTER_W / 2.0 - FLAP_SEAM_GAP / 2.0` so the two major flaps leave a `2.0 mm` visible seam gap at `Z = FRAME_OUTER_H / 2.0`; width along `X` = `CARTON_OUTER_L - 1.0`. Rotate front (`-Y`) flaps around their hinge lines when `lid_open_angle > 0.0`.

### Native `bd_materials` Helpers

```python
from bd_materials import paper, plastics


def apply_corrugated_kraft(shape) -> None:
    """Apply natural kraft corrugated cardboard finish."""
    mat = paper.cardboard()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.85)
    shape.material = mat
    shape.color = "#B89163"


def apply_epe_foam(shape) -> None:
    """Apply closed-cell white EPE pearl cotton foam finish."""
    mat = plastics.pe()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.88)
    shape.material = mat
    shape.color = "#F4F5F7"
```
