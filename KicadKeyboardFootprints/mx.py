from typing import Dict, List, Literal
from KicadModTree import Footprint, Model, Pad, Vector2D, Vector3D, Text
from KicadModTree.util.paramUtil import round_to
from .layer import B_FAB, B_SILK, F_COURT, F_FAB, F_SILK, USER_DRAWING
from .model import LIB_PATH_PLACEHOLDER
from .shapes import (
    IDENTITY,
    ArcCenter,
    Transform,
    add_circle,
    add_curve,
    add_npth,
    add_polygon,
    add_rect,
    add_smt_pad,
    add_square,
    add_text,
    add_tht_pad,
    normalize_angle,
    to_vec3,
)

from .types import Number, Switch, Mount, Led, Stabilizer, Vec2


UNIT_SIZE = 19.05
UNIT_SCALE = Transform(scale=UNIT_SIZE)


def make_mx_switch(
    units: Number = 1,
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    led=Led.NONE,
    stabilizer=Stabilizer.NORMAL,
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

    transform = Transform(translate=switch_offset * UNIT_SIZE, rotate=switch_angle)

    add_mx_reference(mod, switch=switch, transform=transform)
    add_mx_value(mod, show_value=show_value, transform=transform)
    add_mx_switch(
        mod,
        switch=switch,
        mount=mount,
        front_silk=front_silk,
        transform=transform,
    )
    add_mx_stabilizer(mod, units=units, vertical=vertical, stabilizer=stabilizer)
    add_mx_led(mod, switch=switch, led=led, transform=transform)
    add_mx_keycap_outline(mod, units=units, vertical=vertical)
    add_mx_3d_model(mod, switch=switch, transform=transform)

    return mod


def make_mx_iso_enter(
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    led=Led.NONE,
    stabilizer=Stabilizer.NORMAL,
    front_silk=True,
    show_value=True,
    switch_angle=0,
) -> Footprint:
    """
    Generate a footprint for a Cherry MX ISO enter switch.

    :param switch: Switch connection type.
    :param mount: Switch mounting style.
    :param led: Switch LED type.
    :param stabilizer: Stabilizer type. Defaults to NORTH for sizes >= 2U.
    :param front_silk: Add a rectangle for the switch on the front silkscreen layer.
    :param show_value: Display symbol value on the back silkscreen layer.
    :param switch_angle: Rotation of the switch in degrees CW. Must be a multiple of 90.
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

    transform = Transform(rotate=switch_angle)

    add_mx_reference(mod, switch=switch, transform=transform)
    add_mx_value(mod, show_value=show_value, transform=transform)
    add_mx_switch(
        mod, switch=switch, mount=mount, front_silk=front_silk, transform=transform
    )
    add_mx_stabilizer(mod, units=2.25, vertical=True, stabilizer=stabilizer)
    add_mx_led(mod, switch=switch, led=led, transform=transform)
    add_mx_iso_enter_keycap_outline(mod)
    add_mx_3d_model(mod, switch=switch, transform=transform)

    return mod


def make_mx_led_only(led=Led.NORMAl):
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


def add_mx_reference(mod: Footprint, switch=Switch.SOLDER, transform=IDENTITY):
    """Add a reference label for a switch footprint"""
    REF_POS = Vector2D(0, 3)

    layer = USER_DRAWING
    mirror = False

    if switch == Switch.HOTSWAP or switch == Switch.HOTSWAP_ANTISHEAR:
        layer = B_FAB
        mirror = True

    add_text(
        mod,
        type=Text.TYPE_REFERENCE,
        text="REF**",
        at=REF_POS,
        mirror=mirror,
        layer=layer,
        transform=transform.with_rotation(0),
    )


def add_mx_value(mod: Footprint, show_value=True, bottom=True, transform=IDENTITY):
    """Add a value label for a switch footprint"""
    VALUE_POS = Vector2D(0, -8)
    VALUE_SIZE = Vector2D(1.27, 1.27)

    mirror = bottom
    layer = B_SILK if bottom else F_SILK

    add_text(
        mod,
        type=Text.TYPE_VALUE,
        text="Val**",
        at=VALUE_POS,
        size=VALUE_SIZE,
        layer=layer,
        mirror=mirror,
        transform=transform.with_rotation(0),
        hide=not show_value,
    )


def add_mx_keycap_outline(mod: Footprint, units: Number, vertical: bool):
    """Add a switch keycap outline to a footprint as a user drawing"""
    LAYER = USER_DRAWING
    STROKE = 0.15
    TEXT_POS = Vector2D(0, 8)

    if vertical:
        key_size = Vector2D(1, units)
    else:
        key_size = Vector2D(units, 1)

    add_rect(
        mod,
        center=(0, 0),
        size=key_size,
        layer=LAYER,
        stroke=STROKE,
        transform=UNIT_SCALE,
    )
    add_text(mod, type=Text.TYPE_USER, text=f"{units:g}U", at=TEXT_POS, layer=LAYER)


def add_mx_iso_enter_keycap_outline(mod: Footprint):
    """Add an ISO Enter keycap outline to a footprint as a user drawing"""
    LAYER = USER_DRAWING
    STROKE = 0.15
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

    add_polygon(mod, POINTS, layer=LAYER, stroke=STROKE, transform=UNIT_SCALE)
    add_text(mod, type=Text.TYPE_USER, text="ISO", at=TEXT_POS, layer=LAYER)


def add_mx_switch(
    mod: Footprint,
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    front_silk=True,
    transform=IDENTITY,
):
    """Add an MX switch to a footprint"""
    if switch == Switch.NONE:
        return

    F_FAB_SIZE = 12.7
    F_FAB_STROKE = 0.1
    F_COURTYARD_SIZE = 13.2
    F_COURTYARD_STROKE = 0.05
    F_SILK_SIZE = 13.87
    F_SILK_STROKE = 0.12
    CENTER_HOLE_SIZE = 4

    # Front fab
    add_square(
        mod,
        center=(0, 0),
        size=F_FAB_SIZE,
        stroke=F_FAB_STROKE,
        layer=F_FAB,
        transform=transform,
    )

    # Front courtyard
    add_square(
        mod,
        center=(0, 0),
        size=F_COURTYARD_SIZE,
        stroke=F_COURTYARD_STROKE,
        layer=F_COURT,
        transform=transform,
    )

    # Front silkscreen
    if front_silk:
        add_square(
            mod,
            center=(0, 0),
            size=F_SILK_SIZE,
            stroke=F_SILK_STROKE,
            layer=F_SILK,
            transform=transform,
        )

    add_npth(mod, at=(0, 0), size=CENTER_HOLE_SIZE, transform=transform)

    if mount == Mount.PCB:
        _add_pcb_mount(mod, transform)

    match switch:
        case Switch.SOLDER:
            _add_solder_pads(mod, transform)
        case Switch.HOTSWAP:
            _add_hotswap_socket(mod, transform)
        case Switch.HOTSWAP_ANTISHEAR:
            _add_hotswap_socket_antishear(mod, transform)


def add_mx_stabilizer(
    mod: Footprint, units: Number = 1, stabilizer=Stabilizer.NORMAL, vertical=False
):
    """Add a Cherry stabilizer to a footprint"""
    if stabilizer == stabilizer.NONE:
        return

    width = get_mx_stabilizer_width(units)
    if width == 0:
        return

    TOP_SIZE = 3.05
    BOTTOM_SIZE = 4
    TOP_Y = -7
    BOTTOM_Y = TOP_Y + 15.24

    transform = IDENTITY.with_rotation(-90 if vertical else 0)
    if stabilizer == Stabilizer.REVERSE:
        transform = transform.with_scale((1, -1))

    top_left = Vector2D(-width / 2, TOP_Y)
    top_right = Vector2D(width / 2, TOP_Y)

    bottom_left = Vector2D(-width / 2, BOTTOM_Y)
    bottom_right = Vector2D(width / 2, BOTTOM_Y)

    add_npth(mod, at=top_left, size=TOP_SIZE, transform=transform)
    add_npth(mod, at=top_right, size=TOP_SIZE, transform=transform)
    add_npth(mod, at=bottom_left, size=BOTTOM_SIZE, transform=transform)
    add_npth(mod, at=bottom_right, size=BOTTOM_SIZE, transform=transform)


def add_mx_led(
    mod: Footprint,
    switch=Switch.NONE,
    led=Led.NORMAl,
    transform=IDENTITY,
):
    """Add an LED to a footprint"""
    if led == Led.NONE:
        return

    PAD_X = 1.27
    PAD_Y = 5.08
    PAD_SIZE = Vector2D(1.905, 1.905)
    PAD_DRILL = 1.04

    if led == Led.REVERSE:
        transform = transform.with_scale((-1, 1))

    switch_pins = 0 if switch == Switch.NONE else 2

    def add_pad(number: int, shape: str, at: Vec2):
        add_tht_pad(
            mod,
            switch_pins + number,
            at=at,
            size=PAD_SIZE,
            drill=PAD_DRILL,
            shape=shape,
            transform=transform,
        )

    add_pad(1, Pad.SHAPE_CIRCLE, (-PAD_X, PAD_Y))
    add_pad(2, Pad.SHAPE_RECT, (PAD_X, PAD_Y))


def add_mx_3d_model(mod: Footprint, switch=Switch.SOLDER, transform=IDENTITY):
    """Add 3D models for mounting hardware to a footprint"""
    match switch:
        case Switch.HOTSWAP | Switch.HOTSWAP_ANTISHEAR:
            _add_kailh_hotswap_model(mod, transform)


def _add_kailh_hotswap_model(mod: Footprint, transform: Transform):
    HOTSWAP_MODEL = f"{LIB_PATH_PLACEHOLDER}/3dshapes/CPG151101S11.wrl"
    HOTSWAP_POS = Vector3D(0, 0, -1.4868)
    HOTSWAP_SCALE = to_vec3(0.3937)

    angle = Vector3D(0, 0, transform.rotate)
    center = Vector3D(transform.translate) + HOTSWAP_POS

    # For some reason "at" is in inches, while "offset" is in mm,
    # but KicadModTree only lets me set "at" and not "offset".
    center = center / 25.4

    mod.append(
        Model(
            filename=HOTSWAP_MODEL,
            at=center,
            scale=HOTSWAP_SCALE,
            angle=angle,
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
    Led.NORMAl: ["LED"],
    Led.REVERSE: ["ReversedLED"],
}  # type: Dict[Switch, List[str]]

_LED_DESC = {
    Led.NONE: [],
    Led.NORMAl: ["LED"],
    Led.REVERSE: ["reverse polarity LED"],
}  # type: Dict[Switch, List[str]]

_STAB_NAME = {
    Stabilizer.NONE: ["NoStabilizers"],
    Stabilizer.NORMAL: [],
    Stabilizer.REVERSE: ["ReversedStabilizers"],
}  # type: Dict[Switch, List[str]]

_STAB_DESC = {
    Stabilizer.NONE: ["no stabilizers"],
    Stabilizer.NORMAL: [],
    Stabilizer.REVERSE: ["reversed stabilizers"],
}  # type: Dict[Switch, List[str]]


def _get_footprint_name_desc(
    size: float | Literal["iso"] = 1,
    switch=Switch.SOLDER,
    mount=Mount.PCB,
    led=Led.NONE,
    stabilizer=Stabilizer.NORMAL,
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


def _add_pcb_mount(mod: Footprint, xfrm: Transform):
    MOUNT1_POS = Vector2D(5.08, 0)
    MOUNT2_POS = Vector2D(-5.08, 0)
    MOUNT_SIZE = 1.7

    add_npth(mod, MOUNT1_POS, size=MOUNT_SIZE, transform=xfrm)
    add_npth(mod, MOUNT2_POS, size=MOUNT_SIZE, transform=xfrm)


def _add_solder_pads(mod: Footprint, transform: Transform):
    PAD1_POS = Vector2D(2.54, -5.08)
    PAD2_POS = Vector2D(-3.81, -2.54)
    SIZE = 2.2
    DRILL = 1.5

    add_tht_pad(mod, 1, PAD1_POS, size=SIZE, drill=DRILL, transform=transform)
    add_tht_pad(mod, 2, PAD2_POS, size=SIZE, drill=DRILL, transform=transform)


def _add_hotswap_socket(mod: Footprint, xfrm: Transform):
    PAD1_POS = Vector2D(-7.085, -2.54)
    PAD2_POS = Vector2D(5.842, -5.08)
    PAD_SIZE = Vector2D(2.55, 2.5)
    PAD_LAYERS = ["B.Cu", "B.Mask", "B.Paste"]

    MOUNT1_POS = Vector2D(-3.81, -2.54)
    MOUNT2_POS = Vector2D(2.54, -5.08)
    MOUNT_SIZE = 3

    add_smt_pad(mod, 1, PAD1_POS, size=PAD_SIZE, layers=PAD_LAYERS, transform=xfrm)
    add_smt_pad(mod, 1, PAD2_POS, size=PAD_SIZE, layers=PAD_LAYERS, transform=xfrm)

    add_npth(mod, MOUNT1_POS, size=MOUNT_SIZE, transform=xfrm)
    add_npth(mod, MOUNT2_POS, size=MOUNT_SIZE, transform=xfrm)

    _add_hotswap_courtyard(mod, xfrm)


def _add_hotswap_socket_antishear(mod: Footprint, xfrm: Transform):
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

    add_smt_pad(mod, 1, PAD1_POS, PAD_SIZE, layers=PAD_LAYERS, transform=xfrm)
    add_smt_pad(mod, 2, PAD2_POS, PAD_SIZE, layers=PAD_LAYERS, transform=xfrm)

    add_smt_pad(mod, 1, PASTE1_POS, PASTE_SIZE, layers=PASTE_LAYERS, transform=xfrm)
    add_smt_pad(mod, 1, PASTE2_POS, PASTE_SIZE, layers=PASTE_LAYERS, transform=xfrm)

    add_tht_pad(mod, 1, MOUNT1_POS, MOUNT_SIZE, MOUNT_DRILL, transform=xfrm)
    add_tht_pad(mod, 2, MOUNT2_POS, MOUNT_SIZE, MOUNT_DRILL, transform=xfrm)

    add_tht_pad(mod, 1, ANCHOR11_POS, ANCHOR_SIZE, ANCHOR_DRILL, transform=xfrm)
    add_tht_pad(mod, 1, ANCHOR12_POS, ANCHOR_SIZE, ANCHOR_DRILL, transform=xfrm)
    add_tht_pad(mod, 2, ANCHOR21_POS, ANCHOR_SIZE, ANCHOR_DRILL, transform=xfrm)
    add_tht_pad(mod, 2, ANCHOR22_POS, ANCHOR_SIZE, ANCHOR_DRILL, transform=xfrm)

    _add_hotswap_courtyard(mod, xfrm)


def _add_hotswap_courtyard(mod: Footprint, xfrm: Transform):
    MOUNT1_POS = Vector2D(-3.81, -2.54)
    MOUNT2_POS = Vector2D(2.54, -5.08)
    RADIUS = 1.524
    STROKE = 0.127
    LAYER = "B.CrtYd"

    POINTS = [
        (-0.4, -2.6),
        (5.3, -2.6),
        (5.3, -7),
        (-4, -7),
        ArcCenter(-4, -4.5),
        (-6.5, -4.5),
        (-6.5, -0.6),
        (-2.4, -0.6),
        ArcCenter(-0.4, -0.6),
        (-0.4, -2.6),
    ]

    add_circle(mod, MOUNT1_POS, RADIUS, layer=LAYER, stroke=STROKE, transform=xfrm)
    add_circle(mod, MOUNT2_POS, RADIUS, layer=LAYER, stroke=STROKE, transform=xfrm)

    add_curve(mod, POINTS, layer=LAYER, stroke=STROKE, transform=xfrm)
