from typing import List, overload
from KicadModTree import Pad, RectLine, Vector2D


def make_npth(at: Vector2D, size: float):
    if at is None:
        at = Vector2D(0, 0)

    return Pad(
        type=Pad.TYPE_NPTH,
        shape=Pad.SHAPE_CIRCLE,
        layers=Pad.LAYERS_NPTH,
        at=at,
        size=size,
        drill=size,
    )


def make_rect(at: Vector2D, size: float | Vector2D, width=float, layer=str):
    if not isinstance(size, Vector2D):
        size = Vector2D(size, size)

    half_size = size / 2
    return RectLine(start=at - half_size, end=at + half_size, width=width, layer=layer)
