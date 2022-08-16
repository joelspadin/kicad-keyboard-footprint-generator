"""
Common utilities for generating MX switch footprints.
"""

from pathlib import Path
from typing import TypedDict
from typing_extensions import Unpack  # pylint: disable=unused-import
from KicadModTree import Vector2D
from kicad_keyboard_footprints.mx import make_mx_iso_enter, make_mx_switch
from kicad_keyboard_footprints.types import Led, Mount, Stabilizer, Switch
from .common import MaybeList, make_footprints


SMALL_UNITS = [1, 1.25, 1.5, 1.75]
"""Unit sizes for keys without stabilizers"""

LARGE_UNITS = [2, 2.25, 2.75, 3, 6, 6.25, 7]
"""Unit sizes for keys with stabilizers"""

STABILIZERS = [Stabilizer.NONE, Stabilizer.NORMAL, Stabilizer.REVERSE]
"""List of all stabilizer types"""

SWITCH_ANGLES = [0, 90, 180, 270]
"""List of all possible switch rotations"""


class MxOptions(TypedDict):
    """
    Options for generating regular MX switch footprints

    Each value may be a single value to use that for all footprints, a list of
    values to generate one footprint per value, or omitted to use the default
    for all footprints.
    """

    units: MaybeList[float]
    switch: MaybeList[Switch]
    mount: MaybeList[Mount]
    led: MaybeList[Led]
    stabilizer: MaybeList[Stabilizer]
    vertical: MaybeList[bool]
    front_silk: MaybeList[bool]
    show_value: MaybeList[bool]
    switch_offset: MaybeList[Vector2D]
    switch_angle: MaybeList[int]


class MxIsoOptions(TypedDict):
    """
    Options for generating MX ISO Enter footprints

    Each value may be a single value to use that for all footprints, a list of
    values to generate one footprint per value, or omitted to use the default
    for all footprints.
    """

    switch: MaybeList[Switch]
    mount: MaybeList[Mount]
    led: MaybeList[Led]
    stabilizer: MaybeList[Stabilizer]
    front_silk: MaybeList[bool]
    show_value: MaybeList[bool]
    switch_angle: MaybeList[int]


class MxStandardOptions(TypedDict):
    """
    Options for generating all standard MX footprints.
    """

    switch: MaybeList[Switch]
    mount: MaybeList[Mount]
    led: MaybeList[Led]
    front_silk: MaybeList[bool]
    show_value: MaybeList[bool]


def make_mx_footprints(
    out_dir: Path | str, lib_name: str, **kwargs: "Unpack[MxOptions]"
):
    """
    Generates MX switch footprints for every permutation of the given options.

    :param out_dir: Output directory path
    :param lib_name: Library name (not including ".pretty")
    :param kwargs: MxOptions values
    """
    make_footprints(out_dir, lib_name, make_mx_switch, **kwargs)


def make_mx_iso_footprints(
    out_dir: Path | str, lib_name: str, **kwargs: "Unpack[MxIsoOptions]"
):
    """
    Generates MX ISO Enter footprints for every permutation of the given options.

    :param out_dir: Output directory path
    :param lib_name: Library name (not including ".pretty")
    :param kwargs: MxIsoOptions values
    """
    make_footprints(out_dir, lib_name, make_mx_iso_enter, **kwargs)


def make_standard_mx_footprints(
    out_dir: Path | str, lib_name: str, **kwargs: MxStandardOptions
):
    """
    Generates MX switch footprints for every permutation of the given options
    for standard key sizes.
    """
    # Regular keys
    make_mx_footprints(**kwargs, units=SMALL_UNITS)
    make_mx_footprints(**kwargs, units=LARGE_UNITS, stabilizer=STABILIZERS)

    # Vertical 2u
    make_mx_footprints(
        out_dir,
        lib_name,
        units=2,
        stabilizer=STABILIZERS,
        vertical=True,
        **kwargs,
    )

    # 6u spacebar with offset stem
    make_mx_footprints(
        out_dir,
        lib_name,
        units=6,
        stabilizer=STABILIZERS,
        switch_offset=(0.5, 0),
        **kwargs,
    )

    # ISO Enter
    make_mx_iso_footprints(
        out_dir,
        lib_name,
        stabilizer=STABILIZERS,
        switch_angle=SWITCH_ANGLES,
        **kwargs,
    )
