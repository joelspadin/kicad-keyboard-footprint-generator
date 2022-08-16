"""
Command line argument utilities
"""

from argparse import ArgumentError, ArgumentParser, Action, Namespace
from typing import Any, Dict
from kicad_keyboard_footprints.types import Led, Mount


class FootprintOptionsAction(Action):
    """Base class for arguments that set a list of footprint options"""

    def __init__(self, options: Dict[str, Any], default: str, **kwargs):
        self.options = options
        default = self.options[default]
        super().__init__(choices=options.keys(), default=default, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Any,
        option_string=None,
    ):
        try:
            setattr(namespace, self.dest, self.options[values.lower()])
        except KeyError as exc:
            choices = [f"'{val}'" for val in self.choices]
            raise ArgumentError(
                self, f"invalid choice: {values} (choose from {choices})"
            ) from exc


def add_output_args(parser: ArgumentParser, default_name: str):
    """
    Adds the --out and --name arguments.

    args.out_dir: str
    args.lib_name: str
    """
    parser.add_argument(
        "--out",
        default="out",
        dest="out_dir",
        help="Output directory",
    )
    parser.add_argument(
        "--name",
        default=default_name,
        dest="lib_name",
        help='Library name (files are written to "{OUT}/{NAME}.pretty")',
    )


def add_led_arg(parser: ArgumentParser):
    """
    Adds the --led argument.

    args.led: Led | list[Led]
    """
    parser.add_argument(
        "--led",
        action=FootprintOptionsAction,
        options={
            "none": Led.NONE,
            "normal": [Led.NONE, Led.NORMAL],
            "reverse": [Led.NONE, Led.REVERSE],
            "all": [Led.NONE, Led.NORMAL, Led.REVERSE],
        },
        default="none",
        help="Include footprints with pins for LEDs (reverse flips LED polarity)",
    )


def add_mount_arg(parser: ArgumentParser):
    """
    Adds the --mount argument.

    args.mount: Mount| list[Mount]
    """
    parser.add_argument(
        "--mount",
        action=FootprintOptionsAction,
        options={
            "pcb": Mount.PCB,
            "plate": Mount.PLATE,
            "all": [Mount.PCB, Mount.PLATE],
        },
        default="pcb",
        help="Include footprints for mounting styles (pcb = 5-pin, plate = 3-pin)",
    )


def add_silkscreen_args(parser: ArgumentParser):
    """
    Adds the --no-front-silk and --no-rear-silk arguments.

    args.front_silk: bool
    args.show_value: bool
    """
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
