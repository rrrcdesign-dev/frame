"""Export 3D production STEP files for the 8-medal display frame assembly and its parts."""

import importlib
from pathlib import Path

from cad import export

from acrylic_cover import acrylic_cover
from backboard import backboard
from frame_moulding import hardwood_frame
from hardware import rear_hardware, turn_button, wall_hanger
from medals import medal, ribbon
from mid_board import mid_board
from spacers import front_spacer, rear_spacer

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "STEP" / "8_medal"
PARTS_DIR = OUT_DIR / "parts"

if __name__ == "__main__":
    medal_8 = importlib.import_module("8_medal").medal_8

    export(medal_8(), OUT_DIR / "medal_8.step")
    export(hardwood_frame(), PARTS_DIR / "hardwood_frame.step")
    export(acrylic_cover(), PARTS_DIR / "acrylic_cover.step")
    export(front_spacer(), PARTS_DIR / "front_spacer.step")
    export(mid_board(), PARTS_DIR / "mid_board.step")
    export(rear_spacer(), PARTS_DIR / "rear_spacer.step")
    export(backboard(), PARTS_DIR / "backboard.step")
    export(rear_hardware(), PARTS_DIR / "rear_hardware.step")
    export(turn_button(), PARTS_DIR / "turn_button.step")
    export(wall_hanger(), PARTS_DIR / "wall_hanger.step")
    export(medal(), PARTS_DIR / "medal.step")
    export(ribbon(), PARTS_DIR / "ribbon.step")
