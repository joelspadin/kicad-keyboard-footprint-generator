#!/usr/bin/env python3
"""
Script to generate hotswap MX switch footprints
"""

# pylint: disable=duplicate-code

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.append(str(SCRIPTS_DIR.parent))

# pylint: disable=wrong-import-position
from scripts.tools.cli import (
    add_output_args,
    add_led_arg,
    add_mount_arg,
    add_silkscreen_args,
    FootprintOptionsAction,
)
from scripts.tools.mx import make_standard_mx_footprints
from kicad_keyboard_footprints.types import Switch

# pylint: enable=wrong-import-position


def main():  # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser(
        description="Generate MX switch footprints with hotswap sockets"
    )
    add_output_args(parser, "MX_Hotswap")
    add_led_arg(parser)
    add_mount_arg(parser)
    parser.add_argument(
        "--pads",
        action=FootprintOptionsAction,
        options={
            "normal": Switch.HOTSWAP,
            "antishear": Switch.HOTSWAP_ANTISHEAR,
            "all": [Switch.HOTSWAP, Switch.HOTSWAP_ANTISHEAR],
        },
        default="normal",
        dest="switch",
        help="Type of SMT pads for sockets "
        "(antishear adds through holes to resist pads lifting)",
    )
    add_silkscreen_args(parser)

    args = parser.parse_args()
    make_standard_mx_footprints(**vars(args))


if __name__ == "__main__":
    main()
