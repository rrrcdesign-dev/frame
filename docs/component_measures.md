# Medal Frame Component Measurements (`8-Medal` & `15-Medal`)

Updated production measurements for **`medal_8_sq`** (`4 cols × 2 rows`) and **`medal_15_sq`** (`5 cols × 3 rows`) with `46.0 mm` total frame depth, `9.0 mm` outer walnut wall, `15.0 mm` front face width, `4.0 mm` mid-board, `15.0 mm` backboard flush with the rear face (`0.0 mm` back inset), `2.0 mm` acrylic cover, and no rear hardware, turning locks, or locking kerf.

---

## 1. Depth Stack (`46.0 mm` Total Frame Depth)

| Layer | Thickness (mm) | `Y` Range (mm) | Notes |
| :--- | :---: | :---: | :--- |
| **Front Lip** (`LIP_DEPTH`) | **`6.0`** | `0.00 – 6.00` | `15.0 mm` face width (`9.0` wall + `3.0` spacer + `3.0` visible overhang) |
| **Acrylic Cover** (`ACRYLIC_T`) | **`2.0`** | `6.00 – 8.00` | Clear PMMA |
| **Front Spacer** (`FRONT_SPACER_T`) | **`15.0`** | `8.00 – 23.00` | `3.0 × 15.0 mm` square-cut butt-jointed (`10.0 mm` air gap before `5.0 mm` medals) |
| **Mid-Board** (`MID_BOARD_T`) | **`4.0`** | `23.00 – 27.00` | Light birch/ash plywood with `45.0 × 2.5 mm` (`R1.0`) slots |
| **Rear Space** (`REAR_SPACER_T`) | **`4.0`** | `27.00 – 31.00` | Open cavity behind `mid_board` (`2.60 mm` clear behind ribbon fold) |
| **Backboard** (`BACKBOARD_T`) | **`15.0`** | `31.00 – 46.00` | Flush with rear face of frame (**`0.0 mm` back inset**; no rear hardware) |

---

## 2. Component Measures (`W × H × D`)

| Component | **8 Medals (`4 × 2`)** | **15 Medals (`5 × 3`)** | Notes |
| :--- | :--- | :--- | :--- |
| **Outer Frame** (`hardwood_frame`) | **`414.0 × 275.0 × 46.0 mm`** | **`501.0 × 379.5 × 46.0 mm`** | `15.0 mm` face width, `9.0 mm` outer wall, `R9.0` outer corners, `R6.0` front edge fillet |
| **Visible Opening** | **`384.0 × 245.0 mm`** | **`471.0 × 349.5 mm`** | `90°` inner corners, `25.0 mm` padding, `14.0 mm` medal gaps (`Ø73 mm` medals) |
| **Rabbet Cavity** | **`396.0 × 257.0 × 40.0 mm`** | **`483.0 × 361.5 × 40.0 mm`** | `90°` square inner corners |
| **Acrylic Cover** (`acrylic_cover`) | **`395.6 × 256.6 × 2.0 mm`** | **`482.6 × 361.1 × 2.0 mm`** | `0.2 mm` clearance per side |
| **Front Spacer — Side Bars (×2)** | **`3.0 × 256.6 × 15.0 mm`** | **`3.0 × 361.1 × 15.0 mm`** | Full height, square-cut |
| **Front Spacer — Top/Bottom (×2)** | **`389.6 × 3.0 × 15.0 mm`** | **`476.6 × 3.0 × 15.0 mm`** | Cut short to fit between side bars |
| **Mid-Board** (`mid_board`) | **`395.6 × 256.6 × 4.0 mm`** (`8` slots) | **`482.6 × 361.1 × 4.0 mm`** (`15` slots) | `45.0 × 2.5 mm` (`R1.0`) horizontal slots |
| **Backboard** (`backboard`) | **`395.4 × 256.4 × 15.0 mm`** | **`482.4 × 360.9 × 15.0 mm`** | `0.3 mm` clearance per side, flush at `Y = 46.0 mm` |
| **Corner Splines (×8)** | `3.2 mm` thick × `9.5 mm` depth | `3.2 mm` thick × `9.5 mm` depth | `Y = 15.0 mm` and `32.0 mm` (`~3.2 mm` clear of cavity) |

---

## 3. Source Models & Exports

- **8-Medal (`medal_8_sq`)**:
  - CAD Source: `src_medal_8_sq/medal_8_sq.py`
  - STEP (No Medals): `exports/medal_8_sq_no_medals.step` & `exports/medal_8_sq_parts/`
  - Laser-Cut Mid-Board SVG: `exports/medal_8_sq_mid_board_lasercut.svg`
- **15-Medal (`medal_15_sq`)**:
  - CAD Source: `src_medal_15_sq/medal_15_sq.py`
  - STEP (No Medals): `exports/medal_15_sq_no_medals.step` & `exports/medal_15_sq_parts/`
  - Laser-Cut Mid-Board SVG: `exports/medal_15_sq_mid_board_lasercut.svg`
