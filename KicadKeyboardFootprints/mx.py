from enum import Enum
from itertools import pairwise
from typing import Dict, List, Literal
from KicadModTree import (
    Footprint,
    Model,
    Pad,
    Vector2D,
    Vector3D,
    Arc,
    Circle,
    Line,
    Text,
)
from KicadModTree.util.paramUtil import round_to

from KicadKeyboardFootprints.model import MODEL_PATH_PLACEHOLDER

from .types import Number, Switch, Mount, Led, Stabilizer, Vec2
from .util import make_npth, make_rect, normalize_angle, rotate, rotate_rect


UNIT_SIZE = 19.05


def make_mx_switch(
    units: Number = 1,
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    led=Led.NONE,
    stabilizer=Stabilizer.STANDARD,
    vertical=False,
    front_silk=True,
    show_value=True,
    switch_offset: Vec2 = Vector2D(0, 0),
    switch_angle=0,
) -> Footprint:
    """
    Generate a footprint for a Cherry MX switch.

    :param units: Unit size of the key cap.
    :param switch: Switch connection type.
    :param mount: Switch mounting style.
    :param led: Switch LED type.
    :param stabilizer: Stabilizer type. Defaults to NORTH for sizes >= 2U.
    :param vertical: Rotate key cap 90 degrees.
    :param front_silk: Add a rectangle for the switch on the front silkscreen layer.
    :param show_value: Display symbol value on the back silkscreen layer.
    :param switch_offset: Offset in units from the key center to the switch.
    :param switch_angle: Rotation of the switch in degrees CW. Must be a multiple of 90.
    """
    switch_offset = Vector2D(switch_offset)

    name, desc = _get_footprint_name_desc(
        size=units,
        switch=switch,
        mount=mount,
        led=led,
        stabilizer=stabilizer,
        vertical=vertical,
        switch_offset=switch_offset,
        switch_angle=switch_angle,
    )

    mod = Footprint(name)
    mod.description = desc

    add_mx_reference(mod, switch=switch, offset=switch_offset)
    add_mx_value(mod, offset=switch_offset, show_value=show_value)
    add_mx_switch(
        mod,
        switch=switch,
        mount=mount,
        front_silk=front_silk,
        offset=switch_offset,
        angle=switch_angle,
    )
    add_mx_stabilizer(mod, units=units, vertical=vertical, stabilizer=stabilizer)
    add_mx_led(mod, switch=switch, led=led, offset=switch_offset, angle=switch_angle)
    add_mx_keycap_outline(mod, units=units, vertical=vertical)
    add_mx_3d_model(mod, switch=switch, offset=switch_offset, angle=switch_angle)

    return mod


def make_mx_iso_enter(
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    led=Led.NONE,
    stabilizer=Stabilizer.STANDARD,
    front_silk=True,
    show_value=True,
    switch_angle=0,
) -> Footprint:
    """
    Generate a footprint for a Cherry MX ISO enter switch.
    """
    name, desc = _get_footprint_name_desc(
        size="iso",
        switch=switch,
        mount=mount,
        led=led,
        stabilizer=stabilizer,
        switch_angle=switch_angle,
    )

    mod = Footprint(name)
    mod.description = desc

    add_mx_reference(mod, switch=switch)
    add_mx_value(mod, show_value=show_value)
    add_mx_switch(
        mod, switch=switch, mount=mount, front_silk=front_silk, angle=switch_angle
    )
    add_mx_stabilizer(mod, units=2.25, vertical=True, stabilizer=stabilizer)
    add_mx_led(mod, switch=switch, led=led, angle=switch_angle)
    add_mx_iso_enter_keycap_outline(mod)
    add_mx_3d_model(mod, switch=switch, angle=switch_angle)

    return mod


def make_mx_led_only(led=Led.STANDARD):
    pass


def get_mx_stabilizer_width(units: Number) -> float:
    """
    Get the horizontal spacing in millimeters between the sides of a Cherry MX stabilizer.

    Returns 0 if no stabilizer size is defined for the key size.
    """
    if units < 2:
        return 0

    # 2-2.75u all use the same spacing as a 2.25u key would.
    if units < 3:
        units = 2.25

    # Stabilizers are 1/2 unit from each end.
    return round_to((units - 1) * UNIT_SIZE, 0.05)


def add_mx_reference(
    mod: Footprint, switch=Switch.SOLDER, offset: Vec2 = Vector2D(0, 0)
):
    REF_POS = Vector2D(0, 3)

    offset = Vector2D(offset)

    layer = "Dwgs.User"
    mirror = False

    match switch:
        case Switch.HOTSWAP | Switch.HOTSWAP_ANTISHEAR:
            layer = "B.Fab"
            mirror = True

    center = offset * UNIT_SIZE
    ref_pos = center + REF_POS

    mod.append(
        Text(
            type=Text.TYPE_REFERENCE,
            text="REF**",
            at=ref_pos,
            mirror=mirror,
            layer=layer,
        )
    )


def add_mx_value(mod: Footprint, offset: Vec2 = Vector2D(0, 0), show_value=True):
    VALUE_POS = Vector2D(0, -8)
    VALUE_SIZE = Vector2D(1.27, 1.27)

    offset = Vector2D(offset)
    center = offset * UNIT_SIZE
    value_pos = center + VALUE_POS

    mod.append(
        Text(
            type=Text.TYPE_VALUE,
            text="Val**",
            at=value_pos,
            mirror=True,
            layer="B.SilkS",
            size=VALUE_SIZE,
            hide=not show_value,
        )
    )


def add_mx_keycap_outline(mod: Footprint, units: Number, vertical: bool):
    LAYER = "Dwgs.User"
    TEXT_POS = Vector2D(0, 8)

    if vertical:
        key_size = Vector2D(1, units) * UNIT_SIZE
    else:
        key_size = Vector2D(units, 1) * UNIT_SIZE

    mod.append(make_rect(at=Vector2D(0, 0), size=key_size, width=0.15, layer=LAYER))
    mod.append(
        Text(
            type=Text.TYPE_USER,
            text=f"{units:g}U",
            at=TEXT_POS,
            layer=LAYER,
        )
    )


def add_mx_iso_enter_keycap_outline(mod: Footprint):
    LAYER = "Dwgs.User"
    TEXT_POS = Vector2D(0, 8)
    POINTS = [
        (0.625, 1),
        (0.625, -1),
        (-0.875, -1),
        (-0.875, 0),
        (-0.625, 0),
        (-0.625, 1),
        (0.625, 1),
    ]

    points = [Vector2D(p) * UNIT_SIZE for p in POINTS]

    for start, end in pairwise(points):
        mod.append(Line(start=start, end=end, width=0.15, layer=LAYER))

    mod.append(
        Text(
            type=Text.TYPE_USER,
            text="ISO",
            at=TEXT_POS,
            layer=LAYER,
        )
    )


def add_mx_switch(
    mod: Footprint,
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    front_silk=True,
    offset: Vec2 = Vector2D(0, 0),
    angle=0,
):
    if switch == Switch.NONE:
        return

    F_FAB_SIZE = 12.7
    F_FAB_WIDTH = 0.1
    F_COURTYARD_SIZE = 13.2
    F_COURTYARD_WIDTH = 0.05
    F_SILK_SIZE = 13.87
    F_SILK_WIDTH = 0.12
    CENTER_HOLE_SIZE = 4

    offset = Vector2D(offset)
    origin = offset * UNIT_SIZE

    # Front fab
    mod.append(make_rect(at=origin, size=F_FAB_SIZE, width=F_FAB_WIDTH, layer="F.Fab"))

    # Front courtyard
    mod.append(
        make_rect(
            at=origin,
            size=F_COURTYARD_SIZE,
            width=F_COURTYARD_WIDTH,
            layer="F.CrtYd",
        )
    )

    # Front silkscreen
    if front_silk:
        mod.append(
            make_rect(at=origin, size=F_SILK_SIZE, width=F_SILK_WIDTH, layer="F.SilkS")
        )

    # Pads
    mod.append(make_npth(at=origin, size=CENTER_HOLE_SIZE))

    if mount == Mount.PCB:
        _add_pcb_mount(mod, origin, angle)

    match switch:
        case Switch.SOLDER:
            _add_solder_pads(mod, origin, angle)
        case Switch.HOTSWAP:
            _add_hotswap_socket(mod, origin, angle)
        case Switch.HOTSWAP_ANTISHEAR:
            _add_hotswap_socket_antishear(mod, origin, angle)


def add_mx_stabilizer(
    mod: Footprint, units: Number = 1, stabilizer=Stabilizer.STANDARD, vertical=False
):

    if stabilizer == stabilizer.NONE:
        return

    width = get_mx_stabilizer_width(units)
    if width == 0:
        return

    TOP_SIZE = 3.05
    BOTTOM_SIZE = 4
    TOP_Y = -7
    BOTTOM_Y = TOP_Y + 15.24

    y_scale = 1 if stabilizer == Stabilizer.STANDARD else -1

    top_left = Vector2D(-width / 2, TOP_Y * y_scale)
    top_right = Vector2D(width / 2, TOP_Y * y_scale)

    bottom_left = Vector2D(-width / 2, BOTTOM_Y * y_scale)
    bottom_right = Vector2D(width / 2, BOTTOM_Y * y_scale)

    if vertical:
        top_left, top_right, bottom_left, bottom_right = [
            x.rotate(-90) for x in (top_left, top_right, bottom_left, bottom_right)
        ]

    mod.append(make_npth(at=top_left, size=TOP_SIZE))
    mod.append(make_npth(at=top_right, size=TOP_SIZE))
    mod.append(make_npth(at=bottom_left, size=BOTTOM_SIZE))
    mod.append(make_npth(at=bottom_right, size=BOTTOM_SIZE))


def add_mx_led(
    mod: Footprint,
    switch=Switch.NONE,
    led=Led.STANDARD,
    offset: Vec2 = Vector2D(0, 0),
    angle=0,
):
    if led == Led.NONE:
        return

    PAD_X = 1.27
    PAD_Y = 5.08
    PAD_SIZE = Vector2D(1.905, 1.905)
    PAD_DRILL = 1.04

    number_offset = 0 if switch == Switch.NONE else 2
    scale = Vector2D(1 if led == Led.STANDARD else -1, 1)

    offset = Vector2D(offset)
    origin = offset * UNIT_SIZE

    def make_pad(number: int, shape: str, at: Vector2D):
        return Pad(
            number=number_offset + number,
            type=Pad.TYPE_THT,
            shape=shape,
            layers=Pad.LAYERS_THT,
            at=origin + rotate(at * scale, angle),
            size=PAD_SIZE,
            drill=PAD_DRILL,
        )

    mod.append(make_pad(1, Pad.SHAPE_CIRCLE, Vector2D(-PAD_X, PAD_Y)))
    mod.append(make_pad(2, Pad.SHAPE_RECT, Vector2D(PAD_X, PAD_Y)))


def add_mx_3d_model(
    mod: Footprint, switch=Switch.SOLDER, offset: Vec2 = Vector2D(0, 0), angle=0
):
    HOTSWAP_MODEL = f"{MODEL_PATH_PLACEHOLDER}.3dshapes/CPG151101S11.wrl"
    HOTSWAP_OFFSET = Vector3D(0, 0, -1.4868)
    HOTSWAP_SCALE = Vector3D(0.3937, 0.3937, 0.3937)

    offset = Vector2D(offset)
    center = Vector3D(offset.x, offset.y, 0) * UNIT_SIZE

    # For some reason "at" is in inches, while "offset" is in mm, but KicadModTree
    # doesn't let me set an offset.
    hotswap_pos = (center + HOTSWAP_OFFSET) / 25.4

    match switch:
        case Switch.HOTSWAP | Switch.HOTSWAP_ANTISHEAR:
            mod.append(
                Model(
                    filename=HOTSWAP_MODEL,
                    at=hotswap_pos,
                    scale=HOTSWAP_SCALE,
                    angle=Vector3D(0, 0, angle),
                )
            )


_SWITCH_NAME = {
    Switch.NONE: ["NoSwitch"],
    Switch.SOLDER: [],
    Switch.HOTSWAP: ["Hotswap"],
    Switch.HOTSWAP_ANTISHEAR: ["Hotswap", "Antishear"],
}  # type: Dict[Switch, List[str]]

_SWITCH_DESC = {
    Switch.NONE: ["no switch"],
    Switch.SOLDER: [],
    Switch.HOTSWAP: ["hotswap"],
    Switch.HOTSWAP_ANTISHEAR: ["hotswap", "anti-shear pads"],
}  # type: Dict[Switch, List[str]]

_MOUNT_NAME = {
    Mount.PCB: [],
    Mount.PLATE: ["Plate"],
}  # type: Dict[Switch, List[str]]

_MOUNT_DESC = {
    Mount.PCB: ["PCB mount"],
    Mount.PLATE: ["plate mount"],
}  # type: Dict[Switch, List[str]]

_LED_NAME = {
    Led.NONE: [],
    Led.STANDARD: ["LED"],
    Led.REVERSE: ["ReversedLED"],
}  # type: Dict[Switch, List[str]]

_LED_DESC = {
    Led.NONE: [],
    Led.STANDARD: ["LED"],
    Led.REVERSE: ["reverse polarity LED"],
}  # type: Dict[Switch, List[str]]

_STAB_NAME = {
    Stabilizer.NONE: ["NoStabilizers"],
    Stabilizer.STANDARD: [],
    Stabilizer.REVERSE: ["ReversedStabilizers"],
}  # type: Dict[Switch, List[str]]

_STAB_DESC = {
    Stabilizer.NONE: ["no stabilizers"],
    Stabilizer.STANDARD: [],
    Stabilizer.REVERSE: ["reversed stabilizers"],
}  # type: Dict[Switch, List[str]]


def _get_footprint_name_desc(
    size: float | Literal["iso"] = 1,
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    led=Led.NONE,
    stabilizer=Stabilizer.STANDARD,
    vertical=False,
    switch_offset=Vector2D(0, 0),
    switch_angle=0,
) -> str:
    if size == "iso":
        name_size = "ISOEnter"
        desc_size = "ISO Enter"
        has_stab = True
    else:
        name_size = f"{size:.2f}u"
        desc_size = name_size
        has_stab = get_mx_stabilizer_width(size) != 0

    name = ["Cherry_MX", name_size]
    name += _SWITCH_NAME[switch]
    name += _MOUNT_NAME[mount]
    name += ["Vertical"] if vertical else []
    name += _get_offset_name(switch_offset)
    name += _get_angle_name(switch_angle)
    name += _LED_NAME[led]
    name += _STAB_NAME[stabilizer] if has_stab else []

    desc = ["Cherry MX keyswitch", desc_size]
    desc += _SWITCH_DESC[switch]
    desc += _MOUNT_DESC[mount]
    desc += ["vertical"] if vertical else []
    desc += _get_offset_desc(switch_offset)
    desc += _get_angle_desc(switch_angle)
    desc += _LED_DESC[led]
    desc += _STAB_DESC[stabilizer] if has_stab else []

    return "_".join(name), ", ".join(desc)


def _get_offset_name(offset: Vector2D) -> List[str]:
    if offset.x == 0 and offset.y == 0:
        return []

    name = ["Offset", f"{offset.x:g}u"]
    if offset.y != 0:
        name += [f"{offset.y:g}u"]

    return name


def _get_offset_desc(offset: Vector2D) -> List[str]:
    if offset.x == 0 and offset.y == 0:
        return []

    desc = f"offset {offset.x:g}u"

    if offset.y != 0:
        desc += f" x {offset.y:g}u"

    return [desc]


def _get_angle_name(angle: int) -> List[str]:
    if angle == 0:
        return []

    return ["Rotate", str(normalize_angle(angle))]


def _get_angle_desc(angle: int) -> List[str]:
    if angle == 0:
        return []

    return [f"switch rotated {normalize_angle(angle)}"]


def _add_pcb_mount(mod: Footprint, origin: Vector2D, angle: int):
    MOUNT1_POS = Vector2D(5.08, 0)
    MOUNT2_POS = Vector2D(-5.08, 0)
    MOUNT_SIZE = 1.7

    def make_mount(at: Vector2D):
        return make_npth(at=origin + rotate(at, angle), size=MOUNT_SIZE)

    mod.append(make_mount(at=MOUNT1_POS))
    mod.append(make_mount(at=MOUNT2_POS))


def _add_solder_pads(mod: Footprint, origin: Vector2D, angle: int):
    PAD1_POS = Vector2D(2.54, -5.08)
    PAD2_POS = Vector2D(-3.81, -2.54)
    PAD_SIZE = 2.2
    HOLE_SIZE = 1.5

    def make_pad(number: int, at=Vector2D):
        return Pad(
            number=number,
            type=Pad.TYPE_THT,
            shape=Pad.SHAPE_CIRCLE,
            layers=Pad.LAYERS_THT,
            at=origin + rotate(at, angle),
            size=PAD_SIZE,
            drill=HOLE_SIZE,
        )

    mod.append(make_pad(number=1, at=PAD1_POS))
    mod.append(make_pad(number=2, at=PAD2_POS))


def _add_hotswap_socket(mod: Footprint, origin: Vector2D, angle: int):
    PAD_SIZE = Vector2D(2.55, 2.5)
    PAD1_POS = Vector2D(-7.085, -2.54)
    PAD2_POS = Vector2D(5.842, -5.08)
    PAD_LAYERS = ["B.Cu", "B.Mask", "B.Paste"]

    MOUNT1_POS = Vector2D(-3.81, -2.54)
    MOUNT2_POS = Vector2D(2.54, -5.08)
    MOUNT_SIZE = 3

    def make_pad(number: int, at: Vector2D):
        return Pad(
            number=number,
            type=Pad.TYPE_SMT,
            shape=Pad.SHAPE_RECT,
            layers=PAD_LAYERS,
            at=origin + rotate(at, angle),
            size=rotate_rect(PAD_SIZE, angle),
        )

    def make_mount(at: Vector2D):
        return make_npth(at=origin + rotate(at, angle), size=MOUNT_SIZE)

    mod.append(make_pad(number=1, at=PAD1_POS))
    mod.append(make_pad(number=2, at=PAD2_POS))

    mod.append(make_mount(at=MOUNT1_POS))
    mod.append(make_mount(at=MOUNT2_POS))

    _add_hotswap_courtyard(mod, origin, angle)


def _add_hotswap_socket_antishear(mod: Footprint, origin: Vector2D, angle: int):
    PAD1_POS = Vector2D(-7.085, -2.54)
    PAD2_POS = Vector2D(5.842, -5.08)
    PAD_SIZE = Vector2D(4.5, 2.5)
    PAD_LAYERS = ["B.Cu"]

    PASTE1_POS = Vector2D(-7.085, -2.54)
    PASTE2_POS = Vector2D(5.815, -5.08)
    PASTE_SIZE = Vector2D(2.55, 2.5)
    PASTE_LAYERS = ["B.Mask", "B.Paste"]

    MOUNT1_POS = Vector2D(-3.81, -2.54)
    MOUNT2_POS = Vector2D(2.54, -5.08)
    MOUNT_SIZE = 4
    MOUNT_DRILL = 3

    ANCHOR11_POS = Vector2D(-8.89, -3.302)
    ANCHOR12_POS = Vector2D(-8.89, -1.778)
    ANCHOR21_POS = Vector2D(7.62, -5.842)
    ANCHOR22_POS = Vector2D(7.62, -4.318)
    ANCHOR_SIZE = 0.8
    ANCHOR_DRILL = 0.4

    def make_pad(number: int, at: Vector2D):
        return Pad(
            number=number,
            type=Pad.TYPE_SMT,
            shape=Pad.SHAPE_RECT,
            layers=PAD_LAYERS,
            at=origin + rotate(at, angle),
            size=rotate_rect(PAD_SIZE, angle),
        )

    def make_paste(number: int, at: Vector2D):
        return Pad(
            number=number,
            type=Pad.TYPE_SMT,
            shape=Pad.SHAPE_RECT,
            layers=PASTE_LAYERS,
            at=origin + rotate(at, angle),
            size=rotate_rect(PASTE_SIZE, angle),
        )

    def make_anchor(number: int, at: Vector2D):
        return Pad(
            number=number,
            type=Pad.TYPE_THT,
            shape=Pad.SHAPE_CIRCLE,
            layers=Pad.LAYERS_THT,
            at=origin + rotate(at, angle),
            size=ANCHOR_SIZE,
            drill=ANCHOR_DRILL,
        )

    def make_mount(number: int, at: Vector2D):
        return Pad(
            number=number,
            type=Pad.TYPE_THT,
            shape=Pad.SHAPE_CIRCLE,
            layers=Pad.LAYERS_THT,
            at=origin + rotate(at, angle),
            size=MOUNT_SIZE,
            drill=MOUNT_DRILL,
        )

    mod.append(make_pad(number=1, at=PAD1_POS))
    mod.append(make_pad(number=2, at=PAD2_POS))

    mod.append(make_paste(number=1, at=PASTE1_POS))
    mod.append(make_paste(number=2, at=PASTE2_POS))

    mod.append(make_anchor(number=1, at=ANCHOR11_POS))
    mod.append(make_anchor(number=1, at=ANCHOR12_POS))
    mod.append(make_anchor(number=2, at=ANCHOR21_POS))
    mod.append(make_anchor(number=2, at=ANCHOR22_POS))

    mod.append(make_mount(number=1, at=MOUNT1_POS))
    mod.append(make_mount(number=2, at=MOUNT2_POS))

    _add_hotswap_courtyard(mod, origin, angle)


def _add_hotswap_courtyard(mod: Footprint, origin: Vector2D, angle: int):
    MOUNT1_POS = Vector2D(-3.81, -2.54)
    MOUNT2_POS = Vector2D(2.54, -5.08)
    MOUNT_R = 1.524
    WIDTH = 0.127
    LAYER = "B.CrtYd"

    POINTS = [
        (-0.4, -2.6),  # line
        (5.3, -2.6),  # line
        (5.3, -7),  # line
        (-4, -7),  # arc start
        (-4, -4.5),  # arc center
        (-6.5, -4.5),  # line
        (-6.5, -0.6),  # line
        (-2.4, -0.6),  # arc start
        (-0.4, -0.6),  # arc center
    ]

    p = [origin + x for x in POINTS]  # type: List[Vector2D]

    def make_mount(center: Vector2D):
        return Circle(
            center=origin + rotate(center, angle),
            radius=MOUNT_R,
            layer=LAYER,
            width=WIDTH,
        )

    def make_line(start: Vector2D, end: Vector2D):
        return Line(
            start=origin + rotate(start, angle),
            end=origin + rotate(end, angle),
            layer=LAYER,
            width=WIDTH,
        )

    def make_arc(start: Vector2D, center: Vector2D, end: Vector2D):
        return Arc(
            start=origin + rotate(start, angle),
            center=origin + rotate(center, angle),
            end=origin + rotate(end, angle),
            layer=LAYER,
            width=WIDTH,
        )

    mod.append(make_mount(center=MOUNT1_POS))
    mod.append(make_mount(center=MOUNT2_POS))

    mod.append(make_line(start=p[0], end=p[1]))
    mod.append(make_line(start=p[1], end=p[2]))
    mod.append(make_line(start=p[2], end=p[3]))
    mod.append(make_arc(start=p[3], center=p[4], end=p[5]))
    mod.append(make_line(start=p[5], end=p[6]))
    mod.append(make_line(start=p[6], end=p[7]))
    mod.append(make_arc(start=p[7], center=p[8], end=p[0]))
