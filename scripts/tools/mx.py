from typing import TypedDict
from typing_extensions import Unpack
from KicadModTree import Vector2D
from KicadKeyboardFootprints.mx import make_mx_iso_enter, make_mx_switch
from KicadKeyboardFootprints.types import Led, Mount, Stabilizer, Switch
from .common import MaybeList, make_footprints


SMALL_UNITS = [1, 1.25, 1.5, 1.75]
"""Unit sizes for keys without stabilizers"""

LARGE_UNITS = [2, 2.25, 2.75, 3, 6, 6.25, 7]
"""Unit sizes for keys with stabilizers"""

HOTSWAP = [Switch.HOTSWAP, Switch.HOTSWAP_ANTISHEAR]
STABILIZERS = [Stabilizer.NONE, Stabilizer.STANDARD, Stabilizer.REVERSE]
LEDS = [Led.NONE, Led.STANDARD, Led.REVERSE]
ISO_SWITCH_ANGLES = [0, 90, 270]


class MxOptions(TypedDict):
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
    switch: MaybeList[Switch]
    mount: MaybeList[Mount]
    led: MaybeList[Led]
    stabilizer: MaybeList[Stabilizer]
    front_silk: MaybeList[bool]
    show_value: MaybeList[bool]
    switch_angle: MaybeList[int]


def make_mx_footprints(lib_name: str, **kwargs: "Unpack[MxOptions]"):
    make_footprints(lib_name, make_mx_switch, **kwargs)


def make_mx_iso_footprints(lib_name: str, **kwargs: "Unpack[MxIsoOptions]"):
    make_footprints(lib_name, make_mx_iso_enter, **kwargs)
