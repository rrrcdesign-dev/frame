---
name: frame-carton-packaging
description: >-
  Designs and exports 3D build123d CAD assemblies and STEP files for protective
  shipping cartons around medal display frames in this repository (defaulting to
  the 8-medal frame `medal_8_sq`), including an EPE pearl cotton wrap/bag, 4x EPE
  foam corner protectors, front/back EPE foam pads, and a cost-optimized FEFCO 0201
  corrugated carton. Use when the user asks to create, update, or export packaging,
  cartons, or protective wrap CAD models for `medal_8_sq` or `medal_15_sq`.
---

# Medal Frame Carton & Protective Packaging Skill

Generates parametric `build123d` 3D CAD models and `.step` exports for shipping the 8-medal walnut display frame (`medal_8_sq`, or `medal_15_sq` by parameter override) with cost-optimized protective wrapping and corrugated carton geometry.

## Overview & Cost-Optimized Default

1. **Carton Style — FEFCO 0201 Regular Slotted Container (RSC / 平口箱)**:
   - Lowest unit cost and **¥0 die-cut tooling fee** (produced on standard adjustable slotter-creaser machines).
   - Uses ~25–35% less corrugated board area than a FEFCO 0427 roll-end tuck-top mailer (`飞机盒`).
2. **Board Spec**:
   - **Standalone direct parcel shipping (default)**: 5-ply **BE-flute (`4.5 mm`)** kraft corrugated (`464.0 × 324.0 × 103.0 mm` outer for `medal_8_sq`).
   - **Multi-unit master carton shipping**: 3-ply **heavy B-flute (`3.0 mm`, `K=K`)** inner box (`461.0 × 321.0 × 97.0 mm` outer) packed 4–6 units inside a 5-ply outer master carton.
3. **Protective EPE Wrapping Stack (Zero Foam Tooling Cost)**:
   - **EPE Pearl Cotton Bag (`2.0 mm` wall, configurable `2.0–3.0 mm`)**: `0.5 mm` slip clearance per side over the `414.0 × 276.0 × 46.0 mm` frame and `53.67 mm` rear D-ring envelope (`54.0 mm` nominal).
   - **4× Flush L-Profile EPE Corner Protectors**: `15.0 mm` perimeter wall (`X`/`Z`), `75.0 mm` outer leg length, spanning the full bagged depth (`59.0 mm`). Standard extruded/cut corner stock — no custom die.
   - **Front EPE Foam Pad (`12.0 mm`, configurable `10.0–15.0 mm`)**: Straight-cut sheet matching the corner-protected footprint (`449.0 × 311.0 mm`) to shield the PMMA acrylic cover.
   - **Rear EPE Foam Pad (`12.0 mm`, configurable `10.0–15.0 mm`)**: Straight-cut sheet (`449.0 × 311.0 mm`) behind the rear D-ring hardware envelope.

See [packaging-spec.md](./references/packaging-spec.md) for the full cost comparison, parametric stack formulas, worked `medal_8_sq` coordinate table, FEFCO 0201 flap geometry, and `build123d` modeling patterns.

---

## Prerequisites & Conventions

- **Python environment**: Run all scripts with `.venv/bin/python` (`build123d`, `cad`, `bd_materials`).
- **Source of truth**: Read frame dimensions directly from `src_medal_8_sq/lib/dims.py` (or `src_medal_15_sq/lib/dims.py`) rather than hardcoding stale values. Always inspect `docs/component_measures.md` and `hardware.py` bounds for rear D-ring protrusion (`53.67 mm` total depth for `medal_8_sq`).
- **Coordinate system**: Keep the repository's native frame orientation for all packaging components so sub-parts align directly with `medal_8_sq`:
  - `X`: horizontal width, centered at `0.0` (`-L/2` to `+L/2`)
  - `Y`: depth from front acrylic face (`0.0`) toward rear hardware (`+D`)
  - `Z`: vertical height from frame bottom (`0.0`) to top (`+H`)
  - Only apply a `-90°` X-rotation at a top-level flat-pack display wrapper if requested for horizontal box inspection.

---

## Procedure: Generating the Carton CAD & STEP Exports

### Step 1: Create the Packaging Module (`src_carton_medal_8_sq/`)

Organize the CAD package to mirror `src_medal_8_sq/`:

1. `src_carton_medal_8_sq/lib/dims.py`
   - Import `FRAME_OUTER_W`, `FRAME_OUTER_H`, `FRAME_DEPTH`, `FRAME_OUTER_CORNER_R` from `src_medal_8_sq/lib/dims.py` (or verify against them with assertions).
   - Compute all bag, corner protector, pad, inner carton, and FEFCO 0201 outer carton dimensions parametrically per [packaging-spec.md](./references/packaging-spec.md).
2. `src_carton_medal_8_sq/lib/materials.py`
   - Define `apply_corrugated_kraft(shape)` using `paper.cardboard()` (`roughness=0.85`, `#B89163`) and `apply_epe_foam(shape)` using `plastics.pe()` (`roughness=0.88`, `#F4F5F7`) with `.strip_maps().override(...)`.
3. `src_carton_medal_8_sq/epe_protection.py`
   - Implement `@model` builders:
     - `epe_wrap_bag()` — hollow rectangular shell (`R` matching `FRAME_OUTER_CORNER_R + BAG_WALL_CLEARANCE`) subtracting the inner cavity.
     - `epe_corner_protectors()` — 4× L-profile corner guards positioned at `BL`, `BR`, `TL`, `TR` with corner radius relief so they do not intersect the bagged frame.
     - `epe_front_pad()` and `epe_rear_pad()` — straight-cut rectangular foam sheets.
     - `epe_protection_set()` — `bd.Compound` combining all EPE components.
4. `src_carton_medal_8_sq/carton_box.py`
   - Implement `@model` builder `corrugated_carton(lid_open_angle: float = 0.0)`:
     - 4 vertical perimeter walls around `CARTON_INNER_L × CARTON_INNER_W × CARTON_INNER_H`.
     - Bottom (`+Y`) 2 minor flaps + 2 major flaps with `2.0 mm` meeting seam gap.
     - Top (`-Y`) 2 minor flaps + 2 major flaps supporting `lid_open_angle` (`0.0°` closed for shipping/STEP export, `> 0°` for inspection).
5. `src_carton_medal_8_sq/medal_8_sq_carton.py`
   - Root `@model` assembly combining the `medal_8_sq` frame (excluding loose medals by default to match production export `medal_8_sq_no_medals.step`, or full `medal_8_sq()`), `epe_protection_set()`, and `corrugated_carton()`.

### Step 2: Export STEP Files

Add an export runner (or `if __name__ == "__main__":` block) using `bd.export_step(shape, path)` to write:

- `exports/medal_8_sq_carton_assembly.step` — complete packed assembly (frame + EPE protection + closed carton)
- `exports/medal_8_sq_carton_parts/`:
  - `epe_wrap_bag.step`
  - `epe_corner_protectors.step`
  - `epe_front_pad.step`
  - `epe_rear_pad.step`
  - `corrugated_carton.step`

> Note: `.gitignore` ignores `*.step` by default. Remind the user if they want generated STEP files committed via `git add -f`.

---

## Mandatory Verification Checklist

Run verification with `.venv/bin/python` after building or editing the packaging CAD modules:

1. **Bounding-Box Assertions**: Verify every `@model` part matches its parametric dimensions within `1e-3 mm`, including final carton outer bounds (`CARTON_OUTER_L × CARTON_OUTER_W × CARTON_OUTER_H`).
2. **Non-Interference Boolean Checks**: Verify `(part_a & part_b).volume < 1e-3` across all adjacent pairs:
   - `medal_8_sq` (including rear D-rings up to `Y = 53.67 mm`) vs `epe_wrap_bag`
   - `epe_wrap_bag` vs `epe_corner_protectors`, `epe_front_pad`, `epe_rear_pad`
   - `epe_protection_set` vs `corrugated_carton` walls and closed top/bottom flaps
3. **STEP Export Integrity**: Confirm every `.step` file exists, is non-empty, and re-imports cleanly with `bd.import_step(path)`.
