"""
Common types for footprint generators.
"""

from enum import Enum
from typing import Tuple, TypeAlias
from KicadModTree import Vector2D


Number: TypeAlias = int | float
Vec2: TypeAlias = Vector2D | Tuple[Number, Number] | list[Number]


class Switch(Enum):
    """Type of switch connection"""

    NONE = 0
    "No switch in footprint"
    SOLDER = 1
    "Solder connection"
    HOTSWAP = 2
    "Hot-swap socket"
    HOTSWAP_ANTISHEAR = 3
    "Hot-swap socket with anti-shear vias"


class Mount(Enum):
    """Type of switch mounting"""

    PCB = 0
    "PCB mount (all mounting holes)"
    PLATE = 1
    "Plate mount (no PCB mounting holes)"


class Led(Enum):
    """Type of switch LED"""

    NONE = 0
    "No LED"
    NORMAL = 1
    "Single color LED"
    REVERSE = 2
    "Single color LED, reversed polarity"


class Stabilizer(Enum):
    """Type of switch stabilizer"""

    NONE = 0
    "No stabilizer"
    NORMAL = 1
    "Cherry stabilizer, North-facing wire"
    REVERSE = 2
    "Cherry stabilizer, South-facing wire"
