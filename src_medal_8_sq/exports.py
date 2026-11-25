"""Export 3D production STEP files for the medal_8_sq display frame assembly and its parts."""

from pathlib import Path

import build123d as bd
from cad import export, model

from acrylic_cover import acrylic_cover
from backboard import backboard
from frame_moulding import hardwood_frame
from hardware import rear_hardware, turn_button, wall_hanger
from medal_8_sq import medal_8_sq
from mid_board import mid_board
from spacers import front_spacer

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "STEP" / "medal_8_sq"
PARTS_DIR = OUT_DIR / "parts"


@model
def medal_8_sq_no_medals():
    """Production assembly without display medals (frame, acrylic, front spacer, mid-board, backboard, hardware)."""
    return bd.Compound(
        children=[
            hardwood_frame().shape,
            acrylic_cover().shape,
            front_spacer().shape,
            mid_board().shape,
            backboard().shape,
            rear_hardware().shape,
        ],
        label="medal_8_sq_no_medals",
    )


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PARTS_DIR.mkdir(parents=True, exist_ok=True)

    export(medal_8_sq_no_medals(), OUT_DIR / "medal_8_sq_no_medals.step")
    export(medal_8_sq(), OUT_DIR / "medal_8_sq.step")
    export(hardwood_frame(), PARTS_DIR / "hardwood_frame.step")
    export(acrylic_cover(), PARTS_DIR / "acrylic_cover.step")
    export(front_spacer(), PARTS_DIR / "front_spacer.step")
    export(mid_board(), PARTS_DIR / "mid_board.step")
    export(backboard(), PARTS_DIR / "backboard.step")
    export(rear_hardware(), PARTS_DIR / "rear_hardware.step")
    export(turn_button(), PARTS_DIR / "turn_button.step")
    export(wall_hanger(), PARTS_DIR / "wall_hanger.step")
