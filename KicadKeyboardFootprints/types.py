from enum import Enum
from typing import Tuple
from KicadModTree import Vector2D


Number = int | float
Vec2 = Vector2D | Tuple[Number, Number] | list[Number]


class Switch(Enum):
    NONE = 0
    "No switch in footprint"
    SOLDER = 1
    "Solder connection"
    HOTSWAP = 2
    "Hot-swap socket"
    HOTSWAP_ANTISHEAR = 3
    "Hot-swap socket with anti-shear vias"


class Mount(Enum):
    PCB = 0
    "PCB mount (all mounting holes)"
    PLATE = 1
    "Plate mount (no PCB mounting holes)"


class Led(Enum):
    NONE = 0
    "No LED"
    STANDARD = 1
    "Single color LED"
    REVERSE = 2
    "Single color LED, reversed polarity"


class Stabilizer(Enum):
    NONE = 0
    "No stabilizer"
    STANDARD = 1
    "Cherry stabilizer, North-facing wire"
    REVERSE = 2
    "Cherry stabilizer, South-facing wire"
