"""
Functions for adding shapes and other footprint elements.
"""

from dataclasses import dataclass
from itertools import pairwise
from typing import Any, Optional
from KicadModTree import (
    Vector2D,
    Vector3D,
    Footprint,
    Pad,
    RectLine,
    FilledRect,
    Line,
    Polygon,
    Arc,
    Circle,
    Text,
)

from .layer import F_SILK
from .types import Number, Vec2

ORIGIN = Vector2D(0, 0)
DEFAULT_STROKE = 0.15


def normalize_angle(angle: int) -> int:
    """Normalize an angle in degrees to [0,360)"""
    return ((angle % 360) + 360) % 360


def rotate_point(point: Vec2, angle: int) -> Vector2D:
    """Rotate a point around (0,0) by a multiple of 90 degrees clockwise"""
    point = Vector2D(point)
    angle = normalize_angle(angle)

    match angle:
        case 0:
            return point
        case 90:
            return Vector2D(-point.y, point.x)
        case 180:
            return Vector2D(-point.x, -point.y)
        case 270:
            return Vector2D(point.y, -point.x)

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


def to_vec2(vec: Number | Vec2):
    """
    Make a Vector2D. If given a single number, it sets both dimensions.
    """
    if isinstance(vec, (int, float)):
        return Vector2D(vec, vec)
    return Vector2D(vec)


def to_vec3(vec: Any):
    """
    Make a Vector3D. If given a single number, it sets all three dimensions.
    """
    if isinstance(vec, (int, float)):
        return Vector3D(vec, vec, vec)
    return Vector3D(vec)


class Transform:
    """
    2D transformation.

    Transformations are applied in the order scale, rotate, translate.
    """

    rotate: int
    translate: Vector2D
    scale: Vector2D

    def __init__(self, translate: Vec2 = ORIGIN, rotate=0, scale: Number | Vec2 = 1):
        self.translate = Vector2D(translate)
        self.rotate = rotate
        self.scale = to_vec2(scale)

    def apply(self, point: Vec2) -> Vector2D:
        """Apply the transform to a point"""
        return rotate_point(Vector2D(point) * self.scale, self.rotate) + self.translate

    def with_rotation(self, rotate: Number):
        """Make a new transform with the rotation changed"""
        return Transform(self.translate, rotate, self.scale)

    def with_scale(self, scale: Number | Vec2):
        """Make a new transform with the scale changed"""
        return Transform(self.translate, self.rotate, scale)

    def __call__(self, point: Vec2) -> Vector2D:
        return self.apply(point)


IDENTITY = Transform()


def add_npth(mod: Footprint, center: Vec2, size: Number, transform=IDENTITY):
    """
    Add a non-plated through hole to the footprint.

    :param mod: Footprint to modify
    :param center: Location of the hole
    :param size: Diameter in millimeters
    :param transform: 2D transform to apply
    """
    mod.append(
        Pad(
            type=Pad.TYPE_NPTH,
            shape=Pad.SHAPE_CIRCLE,
            layers=Pad.LAYERS_NPTH,
            at=transform(center),
            size=size,
            drill=size,
        )
    )


def add_tht_pad(
    mod: Footprint,
    number: int | str,
    center: Vec2,
    size: Number | Vec2,
    drill: Number | Vec2,
    shape=Pad.SHAPE_CIRCLE,
    transform=IDENTITY,
    **kwargs
):
    """
    Add a through-hole pad to the footprint.

    :param mod: Footprint to modify
    :param number: Number/name of the pad
    :param center: Location of the pad
    :param size: Size of the pad
    :param drill: Drill size of the pad
    :param shape: Shape of the pad (default: Pad.SHAPE_CIRCLE)
    :param transform: 2D transform to apply
    :param kwargs: Any arguments to KicadModTree.Pad()
    """
    mod.append(
        Pad(
            number=number,
            type=Pad.TYPE_THT,
            shape=shape,
            layers=Pad.LAYERS_THT,
            at=transform(center),
            size=size,
            drill=drill,
            **kwargs,
        )
    )


def add_smt_pad(
    mod: Footprint,
    number: int | str,
    center: Vec2,
    size: Vec2,
    shape=Pad.SHAPE_RECT,
    layers: Optional[list[str]] = None,
    transform=IDENTITY,
    **kwargs
):
    """
    Add a surface mount pad to the footprint.

    :param mod: Footprint to modify
    :param number: Number/name of the pad
    :param center: Location of the pad
    :param size: Size of the pad
    :param shape: Shape of the pad (default: Pad.SHAPE_RECT)
    :param layers: Layers used for the pad (default: Pad.LAYERS_SMT)
    :param transform: 2D transform to apply
    :param kwargs: Any arguments to KicadModTree.Pad()
    """
    mod.append(
        Pad(
            number=number,
            type=Pad.TYPE_SMT,
            shape=shape,
            layers=layers or Pad.LAYERS_SMT,
            at=transform(center),
            size=rotate_rect(size, transform.rotate),
            **kwargs,
        )
    )


def add_rect(
    mod: Footprint,
    center: Vec2,
    size: Vec2,
    layer=F_SILK,
    stroke=DEFAULT_STROKE,
    fill=False,
    transform=IDENTITY,
):
    """
    Add a rectangle to the footprint.

    :param mod: Footprint to modify
    :param center: Center of the rectangle
    :param size: Size of the pad
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param fill: True to draw a filled shape
    :param transform: 2D transform to apply
    """
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
    stroke=DEFAULT_STROKE,
    fill=False,
    transform=IDENTITY,
):
    """
    Add a square to the footprint.

    :param mod: Footprint to modify
    :param center: Center of the square
    :param size: Size of the square
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param fill: True to draw a filled shape
    :param transform: 2D transform to apply
    """
    add_rect(
        mod,
        center=center,
        size=(size, size),
        layer=layer,
        stroke=stroke,
        fill=fill,
        transform=transform,
    )


def add_circle(
    mod: Footprint,
    center: Vec2,
    radius: Number,
    layer=F_SILK,
    stroke=DEFAULT_STROKE,
    transform=IDENTITY,
):
    """
    Add a circle to the footprint.

    :param mod: Footprint to modify
    :param center: Center of the circle
    :param radius: Radius of the circle
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param transform: 2D transform to apply
    """
    center = transform(center)
    mod.append(Circle(center=center, radius=radius, layer=layer, width=stroke))


def add_line(
    mod: Footprint,
    start: Vec2,
    end: Vec2,
    layer=F_SILK,
    stroke=DEFAULT_STROKE,
    transform=IDENTITY,
):
    """
    Add a line to the footprint.

    :param mod: Footprint to modify
    :param start: Start point
    :param end: End point
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param transform: 2D transform to apply
    """
    start = transform(start)
    end = transform(end)

    mod.append(Line(start=start, end=end, layer=layer, width=stroke))


def add_arc(
    mod: Footprint,
    start: Vec2,
    center: Vec2,
    end: Vec2,
    layer=F_SILK,
    stroke=DEFAULT_STROKE,
    transform=IDENTITY,
):
    """
    Add an arc to the footprint.

    :param mod: Footprint to modify
    :param start: Start point
    :param center: Center point of the arc's circle
    :param end: End point
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param transform: 2D transform to apply
    """
    start = transform(start)
    center = transform(center)
    end = transform(end)

    mod.append(Arc(start=start, center=center, end=end, layer=layer, width=stroke))


def add_polygon(
    mod: Footprint,
    nodes: list[Vec2],
    layer=F_SILK,
    stroke=DEFAULT_STROKE,
    fill=False,
    transform=IDENTITY,
):
    """
    Add a polygon to the footprint.

    :param mod: Footprint to modify
    :param nodes: List of corner points
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param fill: True to draw a filled shape
    :param transform: 2D transform to apply
    """
    if fill:
        nodes = [transform(p) for p in nodes]
        mod.append(Polygon(nodes=nodes, layer=layer, width=stroke))
    else:
        # KicadModTree doesn't provide a way to make a non-filled polygon
        nodes.append(nodes[0])
        add_curve(mod, nodes=nodes, layer=layer, stroke=stroke, transform=transform)


@dataclass
class ArcCenter:
    """
    Center point of an arc for a node list to add_curve()

    This must be preceded and followed by a Vec2 in the list, which form the
    start and end points of the arc.
    """

    x: Number
    y: Number

    @property
    def center(self):
        """Center point as a Vector2D"""
        return Vector2D(self.x, self.y)


def add_curve(
    mod: Footprint,
    nodes: list[Vec2 | ArcCenter],
    layer=F_SILK,
    stroke=DEFAULT_STROKE,
    transform=IDENTITY,
):
    """
    Add a list of connected line segments and/or arcs to the footprint.

    :param mod: Footprint to modify
    :param nodes: List of corner points or arc centers
    :param layer: Layer on which the shape is drawn
    :param stroke: Stroke width (default: 0.15)
    :param transform: 2D transform to apply
    """
    arc_start: Vec2 = None
    for first, second in pairwise(nodes):
        match first, second:
            case ArcCenter(), ArcCenter():
                raise TypeError("Cannot have two adjacent arc centers")

            case start, ArcCenter(center=center):
                arc_start = start

            case ArcCenter(center=center), end:
                add_arc(mod, arc_start, center, end, layer, stroke, transform)

            case start, end:
                add_line(mod, start, end, layer, stroke, transform)


def add_text(
    mod: Footprint,
    kind: str,
    text: str,
    center: Vec2,
    rotation=0,
    size: Optional[Vec2] = None,
    stroke=DEFAULT_STROKE,
    layer=F_SILK,
    transform=IDENTITY,
    **kwargs
):
    """
    Add text to the footprint.

    :param mod: Footprint to modify
    :param kind: The type of text. Use one of the Text.TYPE_* values.
    :param text: The text to draw
    :param center: Center point of the text
    :param size: Font size
    :param rotation: Text rotation in degrees
    :param layer: Layer on which the text is drawn
    :param stroke: Stroke width (default: 0.15)
    :param transform: 2D transform to apply
    :param kwargs: Any arguments to KicadModTree.Text()
    """
    mod.append(
        Text(
            type=kind,
            text=text,
            at=transform(center),
            rotation=rotation + transform.rotate,
            size=size,
            thickness=stroke,
            layer=layer,
            **kwargs,
        )
    )
