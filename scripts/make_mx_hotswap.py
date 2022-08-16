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
    STABILIZERS,
    ISO_SWITCH_ANGLES,
    make_mx_footprints,
    make_mx_iso_footprints,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate MX switch footprints with hotswap sockets"
    )
    parser.add_argument(
        "--out",
        default="out",
        help="Output directory",
    )
    parser.add_argument(
        "--name",
        default="MX_Hotswap",
        help='Library name (files are written to "{OUT}/{NAME}.pretty")',
    )
    parser.add_argument(
        "--led",
        choices=("normal", "reverse", "all", "none"),
        default="none",
        help="Include footprints with pins for LEDs (reverse flips LED polarity)",
    )
    parser.add_argument(
        "--mount",
        choices=("pcb", "plate", "all"),
        default="pcb",
        help="Include footprints for mounting styles (pcb = 5-pin, plate = 3-pin)",
    )
    parser.add_argument(
        "--pads",
        choices=("normal", "antishear", "all"),
        default="normal",
        help="Type of SMT pads for hotswap sockets (antishear adds through holes to resist pads lifting)",
    )
    parser.add_argument(
        "--no-front-silk",
        dest="front_silk",
        action="store_false",
        help="Do not outline switches on the front silkscreen layer",
    )
    parser.add_argument(
        "--no-rear-silk",
        dest="show_value",
        action="store_false",
        help="Do not show switch labels on the back silkscreen layer",
    )

    args = parser.parse_args()

    config = dict(
        out_dir=args.out,
        lib_name=args.name,
        led=get_led(args.led),
        mount=get_mount(args.mount),
        switch=get_switch(args.pads),
        front_silk=args.front_silk,
        show_value=args.show_value,
    )

    # Standard switches
    make_mx_footprints(**config, units=SMALL_UNITS)
    make_mx_footprints(**config, units=LARGE_UNITS, stabilizer=STABILIZERS)

    # Vertical 2u
    make_mx_footprints(
        **config,
        units=2,
        stabilizer=STABILIZERS,
        vertical=True,
    )

    # 6u spacebar with offset stem
    make_mx_footprints(
        **config,
        units=6,
        stabilizer=STABILIZERS,
        switch_offset=(0.5, 0),
    )

    # ISO Enter
    make_mx_iso_footprints(
        **config,
        stabilizer=STABILIZERS,
        switch_angle=ISO_SWITCH_ANGLES,
    )


def get_led(arg):
    match arg:
        case "none":
            return [Led.NONE]
        case "normal":
            return [Led.NONE, Led.NORMAl]
        case "reverse":
            return [Led.NONE, Led.REVERSE]
        case _:
            return [Led.NONE, Led.NORMAl, Led.REVERSE]


def get_mount(arg):
    match arg:
        case "pcb":
            return Mount.PCB
        case "plate":
            return Mount.PLATE
        case _:
            return [Mount.PCB, Mount.PLATE]


def get_switch(arg):
    match arg:
        case "normal":
            return Switch.HOTSWAP
        case "antishear":
            return Switch.HOTSWAP_ANTISHEAR
        case _:
            return [Switch.HOTSWAP, Switch.HOTSWAP_ANTISHEAR]


if __name__ == "__main__":
    main()
