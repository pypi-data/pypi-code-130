#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``protocol`` module of ``vmcp`` package."""

from typing import overload
from .typing import (
    Bone,
    CoordinateVector,
    Quaternion,
    Scale,
    DeviceType,
    BlendShapeKey,
    ModelState,
    CalibrationState,
    CalibrationMode,
    TrackingState
)


@overload
def root_transform(
    position: CoordinateVector,
    rotation: Quaternion
) -> tuple[
    str,
    str,
    tuple[
        str,
        float, float, float,
        float, float, float, float
    ]
]:
    """Root transform.

    Since VMC protocol specification v2.0.0.

    Args:
        position (CoordinateVector):
            Transform position.
        rotation (Quaternion):
            Transform rotation.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                str,
                float, float, float,
                float, float, float, float
            ]:
                OSC arguments.

    """


@overload
def root_transform(
    position: CoordinateVector,
    rotation: Quaternion,
    scale: Scale,
    offset: CoordinateVector,
) -> tuple[
    str,
    str,
    tuple[
        str,
        float, float, float,
        float, float, float, float,
        float, float, float,
        float, float, float
    ]
]:
    """Root transform.

    Since VMC protocol specification v2.1.0.

    Args:
        position (CoordinateVector):
            Transform position.
        rotation (Quaternion):
            Transform rotation.
        scale (Size):
            Additional scaling (division).
        offset (CoordinateVector):
            Additional (negative) offset.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                str,
                float, float, float,
                float, float, float, float,
                float, float, float,
                float, float, float
            ]:
                OSC arguments.

    """


def root_transform(
    position: CoordinateVector,
    rotation: Quaternion,
    scale: Scale = None,
    offset: CoordinateVector = None,
) -> tuple[
    str,
    str,
    tuple[
        str,
        float, float, float,
        float, float, float, float
    ] | tuple[
        str,
        float, float, float,
        float, float, float, float,
        float, float, float,
        float, float, float
    ]
]:
    """Implement root transform.

    Since VMC protocol specification v2.0.0.
    ``scale`` and ``offset`` support since v2.1.0.

    Args:
        position (CoordinateVector):
            Transform position.
        rotation (Quaternion):
            Transform rotation.
        scale (Optional[Size]):
            Additional scaling (division).
        offset (Optional[CoordinateVector]):
            Additional (negative) offset.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                str,
                float, float, float,
                float, float, float, float
            ] | tuple[
                str,
                float, float, float,
                float, float, float, float,
                float, float, float,
                float, float, float
            ]:
                OSC arguments.

    """
    if scale is not None and offset is not None:
        # since VMC protocol specification v2.1.0
        return (
            "/VMC/Ext/Root/Pos",
            ",sfffffffffffff",
            (
                "root",
                position.x,
                position.y,
                position.z,
                rotation.x,
                rotation.y,
                rotation.z,
                rotation.w,
                scale.width,
                scale.height,
                scale.length,
                offset.x,
                offset.y,
                offset.z
            )
        )
    # since VMC protocol specification v2.0.0
    return (
        "/VMC/Ext/Root/Pos",
        ",sfffffff",
        (
            "root",
            position.x,
            position.y,
            position.z,
            rotation.x,
            rotation.y,
            rotation.z,
            rotation.w,
        )
    )


def bone_transform(
    bone: Bone,
    position: CoordinateVector,
    rotation: Quaternion
) -> tuple[
    str,
    str,
    tuple[
        str,
        float, float, float,
        float, float, float, float
    ]
]:
    """Bone transform.

    Args:
        bone (Bone):
            Bone.
        position (CoordinateVector):
            Transform position.
        rotation (Quaternion):
            Transform rotation.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                str,
                float, float, float,
                float, float, float, float
            ]:
                OSC arguments.

    """
    return (
        "/VMC/Ext/Bone/Pos",
        ",sfffffff",
        (
            bone.value,
            position.x,
            position.y,
            position.z,
            rotation.x,
            rotation.y,
            rotation.z,
            rotation.w
        )
    )


def device_transform(
    device_type: DeviceType,
    joint: str,
    position: CoordinateVector,
    rotation: Quaternion,
    local: bool = False
) -> tuple[
    str,
    str,
    tuple[
        str,
        float, float, float,
        float, float, float, float
    ]
]:
    """Device transform.

    Since VMC protocol specification v2.2.0.
    ``local`` transform support since v2.3.0.

    Args:
        device_type (DeviceType):
            Device type.
        joint (str):
            OpenVR device label or serial.
        position (CoordinateVector):
            Transform position.
        rotation (Quaternion):
            Transform rotation.
        local (bool):
            If ``True`` the transform is relative to the avatar,
            word space otherwise (Default).

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                str,
                float, float, float,
                float, float, float, float
            ]:
                OSC arguments.

    """
    if local:
        address = f"/VMC/Ext/{device_type.value}/Pos/Local"
    else:
        address = f"/VMC/Ext/{device_type.value}/Pos"
    return (
        address,
        ",sfffffff",
        (
            str(joint),
            position.x,
            position.y,
            position.z,
            rotation.x,
            rotation.y,
            rotation.z,
            rotation.w
        )
    )


def blendshape(
    key: BlendShapeKey,
    value: float
) -> tuple[
    str,
    str,
    tuple[
        str,
        float
    ]
]:
    """Blendshape.

    Requires `blendshape_apply()` afterwards to take effect.

    Args:
        key (BlendShapeKey):
            Blend shape key.
        value (float):
            Blend shape value.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                str,
                float
            ]:
                OSC arguments.

    """
    return (
        "/VMC/Ext/Blend/Val",
        ",sf",
        (
            key.value,
            value
        )
    )


def blendshape_apply(
) -> tuple[
    str,
    str,
    tuple
]:
    """Apply blendshape(s).

    Args:

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple:
                OSC arguments.

    """
    return (
        "/VMC/Ext/Blend/Apply",
        ",",
        ()
    )


@overload
def state(
    model_state: ModelState
) -> tuple[
    str,
    str,
    tuple[int]
]:
    """Availability state.

    Args:
        model_state (ModelState):
            Model state.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[int]:
                OSC argument.

    """


@overload
def state(
    model_state: ModelState,
    calibration_state: CalibrationState,
    calibration_mode: CalibrationMode
) -> tuple[
    str,
    str,
    tuple[
        int,
        int,
        int
    ]
]:
    """Availability state.

    Since VMC protocol specification v2.5.0.

    Args:
        model_state (ModelState):
            Model state.
        calibration_state (CalibrationState):
            Calibration state.
        calibration_mode (CalibrationMode):
            Calibration mode.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                int,
                int,
                int
            ]:
                OSC arguments.

    """


@overload
def state(
    model_state: ModelState,
    calibration_state: CalibrationState,
    calibration_mode: CalibrationMode,
    tracking_state: TrackingState
) -> tuple[
    str,
    str,
    tuple[
        int,
        int,
        int,
        int
    ]
]:
    """Availability state.

    Since VMC protocol specification v2.7.0.

    Args:
        model_state (ModelState):
            Model state.
        calibration_state (CalibrationState):
            Calibration state.
        calibration_mode (CalibrationMode):
            Calibration mode.
        tracking_state (TrackingState):
            Trackling state.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                int,
                int,
                int,
                int
            ]:
                OSC arguments.

    """


def state(
    model_state: ModelState,
    calibration_state: CalibrationState = None,
    calibration_mode: CalibrationMode = None,
    tracking_state: TrackingState = None
) -> tuple[
    str,
    str,
    tuple[
        int
    ] | tuple[
        int,
        int,
        int
    ] | tuple[
        int,
        int,
        int,
        int
    ]
]:
    """Implement availability state.

    Args:
        model_state (ModelState):
            Model state.
        calibration_state (Optional[CalibrationState]):
            Calibration state.
        calibration_mode (Optional[CalibrationMode]):
            Calibration mode.
        tracking_state (Optional[TrackingState]):
            Trackling state.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[
                int
            ] | tuple[
                int,
                int,
                int
            ] | tuple[
                int,
                int,
                int,
                int
            ]:
                OSC arguments.

    """
    if (
        calibration_state is not None and
        calibration_mode is not None
    ):
        if tracking_state is not None:
            # since VMC protocol specification v2.7.0
            return (
                "/VMC/Ext/OK",
                ",iiii",
                (
                    model_state.value,
                    calibration_state.value,
                    calibration_mode.value,
                    tracking_state.value
                )
            )
        # since VMC protocol specification v2.5.0
        return (
            "/VMC/Ext/OK",
            ",iii",
            (
                model_state.value,
                calibration_state.value,
                calibration_mode.value
            )
        )
    return (
        "/VMC/Ext/OK",
        ",i",
        (
            model_state.value,
        )
    )


def time(
    delta: float
) -> tuple[
    str,
    str,
    tuple[float]
]:
    """Relative frame time.

    Args:
        delta (float):
            Relative time.

    Returns:
        tuple: Arguments for usage with ``vmcp.osc.Message``
            str:
                OSC address pattern (beginng with '/').
            str:
                OSC type tag string (beginning with ',').
            tuple[float]:
                OSC argument.

    """
    return (
        "/VMC/Ext/T",
        ",f",
        (
            delta,
        )
    )
