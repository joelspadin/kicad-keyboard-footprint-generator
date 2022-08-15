#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

sys.path.append(str(SCRIPTS_DIR))
sys.path.append(str(SCRIPTS_DIR.parent))

from KicadKeyboardFootprints.types import Switch, Mount, Led
from tools.mx import (
    SMALL_UNITS,
    LARGE_UNITS,
    HOTSWAP,
    STABILIZERS,
    ISO_SWITCH_ANGLES,
    make_mx_footprints,
    make_mx_iso_footprints,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--led", action="store_true")
    parser.add_argument("-m", "--mount", choices=("pcb", "plate", "all"), default="pcb")
    parser.add_argument(
        "-p", "--pads", choices=("normal", "antishear", "all"), default="normal"
    )

    LIB = "MX_Hotswap"

    # Standard switches
    make_mx_footprints(LIB, switch=HOTSWAP, units=SMALL_UNITS)
    make_mx_footprints(LIB, switch=HOTSWAP, units=LARGE_UNITS, stabilizer=STABILIZERS)

    # Vertical 2u
    make_mx_footprints(
        LIB,
        switch=Switch.HOTSWAP,
        units=2,
        stabilizer=STABILIZERS,
        vertical=True,
    )

    # 6u spacebar with offset stem
    make_mx_footprints(
        LIB,
        switch=HOTSWAP,
        units=6,
        stabilizer=STABILIZERS,
        switch_offset=(0.5, 0),
    )

    # ISO Enter
    make_mx_iso_footprints(
        LIB,
        switch=HOTSWAP,
        stabilizer=STABILIZERS,
        switch_angle=ISO_SWITCH_ANGLES,
    )


if __name__ == "__main__":
    main()
