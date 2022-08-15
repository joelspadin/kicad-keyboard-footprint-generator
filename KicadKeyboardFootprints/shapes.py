from itertools import pairwise
from typing import Any, Iterable, Literal, Optional, Tuple, TypeGuard
from KicadModTree import (
    Vector2D,
    Footprint,
    Pad,
    RectLine,
    FilledRect,
    Line,
    Arc,
    Circle,
)

from .layer import F_SILK
from .types import Number, Vec2

ORIGIN = Vector2D(0, 0)


class Transform:
    translate: Vector2D
    rotate: int

    def __init__(self, translate: Vec2 = ORIGIN, rotate=0):
        self.translate = Vector2D(translate)
        self.rotate = rotate

    def apply(self, p: Vec2) -> Vector2D:
        return self.translate + rotate(p, self.rotate)

    def __call__(self, p: Vec2) -> Vector2D:
        return self.apply(p)


IDENTITY = Transform()


def normalize_angle(angle: int) -> int:
    """Normalize an angle in degrees to [0,360)"""
    return ((angle % 360) + 360) % 360


def rotate(p: Vec2, angle: int) -> Vector2D:
    """Rotate a point around (0,0) by a multiple of 90 degrees clockwise"""
    p = Vector2D(p)
    angle = normalize_angle(angle)

    match angle:
        case 0:
            return p
        case 90:
            return Vector2D(-p.y, p.x)
        case 180:
            return Vector2D(-p.x, -p.y)
        case 270:
            return Vector2D(p.y, -p.x)

    raise ValueError("angle must be a multiple of 90")


def rotate_rect(dims: Vec2, angle: int):
    """Rotate the dimensions of a rectangle by a multiple of 90 degrees"""
    dims = Vector2D(dims)
    angle = normalize_angle(angle)

    match angle:
        case 0 | 180:
            return dims
        case 90 | 270:
            return Vector2D(dims.y, dims.x)

    raise ValueError("angle must be a multiple of 90")


def add_npth(mod: Footprint, at: Vec2, size: Number, transform=IDENTITY):
    """
    Add a non-plated through hole to the footprint.

    :param mod: Footprint to modify
    :param at: Location of the hole
    :param size: Diameter in millimeters
    :param transform: 2D transform to apply
    """
    mod.append(
        Pad(
            type=Pad.TYPE_NPTH,
            shape=Pad.SHAPE_CIRCLE,
            layers=Pad.LAYERS_NPTH,
            at=transform(at),
            size=size,
            drill=size,
        )
    )


def add_through_hole(
    mod: Footprint,
    number: int,
    at: Vec2,
    size: Number,
    drill: Number,
    shape=Pad.SHAPE_CIRCLE,
    transform=IDENTITY,
    **kwargs
):
    mod.append(
        Pad(
            number=number,
            type=Pad.TYPE_THT,
            shape=shape,
            layers=Pad.LAYERS_THT,
            at=transform(at),
            size=size,
            drill=drill,
            **kwargs,
        )
    )


def add_smt_pad(
    mod: Footprint,
    number: int,
    at: Vec2,
    size: Vec2,
    shape=Pad.SHAPE_RECT,
    layers=Pad.LAYERS_SMT,
    transform=IDENTITY,
    **kwargs
):
    mod.append(
        Pad(
            number=number,
            type=Pad.TYPE_SMT,
            shape=shape,
            layers=layers,
            at=transform(at),
            size=rotate_rect(size, transform.rotate),
            **kwargs,
        )
    )


def add_rect(
    mod: Footprint,
    center: Vec2,
    size: Vec2,
    layer=F_SILK,
    stroke: Optional[Number] = None,
    fill=False,
    transform=IDENTITY,
):
    center = Vector2D(center)
    size = Vector2D(size)

    start = transform(center - size / 2)
    end = transform(center + size / 2)

    shape = FilledRect if fill else RectLine

    mod.append(shape(start=start, end=end, width=stroke, layer=layer))


def add_square(
    mod: Footprint,
    center: Vec2,
    size: Number,
    layer=F_SILK,
    stroke: Optional[Number] = None,
    fill=False,
    transform=IDENTITY,
):
    add_rect(mod, center, (size, size), stroke, layer, fill, transform)


def add_circle(
    mod: Footprint,
    center: Vec2,
    radius: Number,
    layer=F_SILK,
    stroke: Optional[Number] = None,
    transform=IDENTITY,
):
    center = transform(center)
    mod.append(Circle(center=center, radius=radius, layer=layer, width=stroke))


def add_line(
    mod: Footprint,
    start: Vec2,
    end: Vec2,
    layer=F_SILK,
    stroke: Optional[Number] = None,
    transform=IDENTITY,
):
    start = transform(start)
    end = transform(end)

    mod.append(Line(start=start, end=end, layer=layer, width=stroke))


def add_arc(
    mod: Footprint,
    start: Vec2,
    center: Vec2,
    end: Vec2,
    layer=F_SILK,
    stroke: Optional[Number] = None,
    transform=IDENTITY,
):
    start = transform(start)
    center = transform(center)
    end = transform(end)

    mod.append(Arc(start=start, center=center, end=end, layer=layer, width=stroke))


class ArcCenter:
    center: Vector2D

    def __init__(self, x: Number | Vec2, y: Optional[Number]):
        if y is not None:
            self.center = Vector2D(x, y)
        else:
            self.center = Vector2D(x)


def add_curve(
    mod: Footprint,
    points: list[Vec2 | ArcCenter],
    layer=F_SILK,
    stroke: Optional[Number] = None,
    transform=IDENTITY,
):
    arc_start: Vec2 = None
    for start, end in pairwise(points):
        match start, end:
            case ArcCenter(), ArcCenter():
                raise TypeError("Cannot have two adjacent arc centers")

            case s, ArcCenter(center=c):
                arc_start = s

            case ArcCenter(center=c), e:
                add_arc(mod, arc_start, c, e, layer, stroke, transform)

            case s, e:
                add_line(mod, s, e, layer, stroke, transform)
