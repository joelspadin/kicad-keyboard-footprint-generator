#!/usr/bin/env python3

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

sys.path.append(str(SCRIPTS_DIR))
sys.path.append(str(SCRIPTS_DIR.parent))

from KicadKeyboardFootprints.types import Switch
from tools.mx import (
    SMALL_UNITS,
    LARGE_UNITS,
    LEDS,
    STABILIZERS,
    ISO_SWITCH_ANGLES,
    make_mx_footprints,
    make_mx_iso_footprints,
)


def main():
    LIB = "MX_Solder"

    # Standard switches
    make_mx_footprints(LIB, switch=Switch.SOLDER, units=SMALL_UNITS, led=LEDS)
    make_mx_footprints(
        LIB, switch=Switch.SOLDER, units=LARGE_UNITS, led=LEDS, stabilizer=STABILIZERS
    )

    # Vertical 2u
    make_mx_footprints(
        LIB,
        switch=Switch.SOLDER,
        units=2,
        leds=LEDS,
        stabilizer=STABILIZERS,
        vertical=True,
    )

    # 6u spacebar with offset stem
    make_mx_footprints(
        LIB,
        switch=Switch.SOLDER,
        units=6,
        leds=LEDS,
        stabilizer=STABILIZERS,
        switch_offset=(0.5, 0),
    )

    # ISO Enter
    make_mx_iso_footprints(
        LIB,
        switch=Switch.SOLDER,
        leds=LEDS,
        stabilizer=STABILIZERS,
        switch_angle=ISO_SWITCH_ANGLES,
    )


if __name__ == "__main__":
    main()
