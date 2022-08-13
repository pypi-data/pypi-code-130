#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``events`` module of ``vmcp`` package."""

from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from typing import (
    ClassVar,
    Any
)
from .typing import (
    CoordinateVector,
    Quaternion,
    Scale,
    Bone,
    DeviceType,
    ModelState,
    CalibrationState,
    CalibrationMode,
    TrackingState
)


@dataclass(frozen=True, slots=True)  # type: ignore
class Event(metaclass=ABCMeta):
    """Abstract event class."""

    ADDRESS_PATTERN: ClassVar[str]
    """str: OSC address pattern matching."""

    channel: str
    """str: Channel name."""

    address: str
    """str: Called OSC address."""

    def __post_init__(self) -> None:
        """Post event initialization.

        Raises:
            NotImplementedError:
                If abstract `Event` is instantiated directly.

        """
        # pylint: disable=unidiomatic-typecheck
        if type(self) is Event:
            raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'Event':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            Event:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """


@dataclass(frozen=True, slots=True)  # type: ignore
class TransformEvent(Event, metaclass=ABCMeta):
    """Abstract transform event class."""

    joint: str
    """str: Joint name."""

    position: CoordinateVector
    """CoordinateVector: 3D position."""

    rotation: Quaternion
    """Quaternion: 3D rotation."""

    def __post_init__(self) -> None:
        """Post event initialization.

        Raises:
            NotImplementedError:
                If abstract `TransformEvent` is instantiated directly.

        """
        # pylint: disable=unidiomatic-typecheck
        if type(self) is TransformEvent:
            raise NotImplementedError


@dataclass(frozen=True, slots=True)
class RootTransformEvent(TransformEvent):
    """Root transform event."""

    ADDRESS_PATTERN: ClassVar[str] = "/VMC/Ext/Root/Pos"
    """str: OSC address pattern matching."""

    scale: Scale
    """Scale: Additional scaling (division)."""

    offset: CoordinateVector
    """CoordinateVector: Additional (negative) offset."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'RootTransformEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            RootTransformEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        scale_width: float = 1.0
        scale_heigth: float = 1.0
        scale_length: float = 1.0
        offset_x: float = 0.0
        offset_y: float = 0.0
        offset_z: float = 0.0
        match len(arguments):
            case 14:
                # Since VMC protocol specification v2.1.0.
                scale_width = arguments[8]
                scale_heigth = arguments[9]
                scale_length = arguments[10]
                offset_x = arguments[11]
                offset_y = arguments[12]
                offset_z = arguments[13]
            case 8:
                # Since VMC protocol specification v2.0.0.
                pass
            case _:
                raise ValueError(f"Invalid arguments: {arguments}")
        return cls(
            str(channel),
            str(address),
            joint=str(arguments[0]),
            position=CoordinateVector(
                x=arguments[1],
                y=arguments[2],
                z=arguments[3]
            ),
            rotation=Quaternion(
                x=arguments[4],
                y=arguments[5],
                z=arguments[6],
                w=arguments[7]
            ),
            scale=Scale(
                scale_width,
                scale_heigth,
                scale_length
            ),
            offset=CoordinateVector(
                x=offset_x,
                y=offset_y,
                z=offset_z
            )
        )


@dataclass(frozen=True, slots=True)
class BoneTransformEvent(TransformEvent):
    """Bone transform event."""

    ADDRESS_PATTERN: ClassVar[str] = "/VMC/Ext/Bone/Pos"
    """str: OSC address pattern matching."""

    joint: Bone
    """Bone: Joint bone."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'BoneTransformEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            BoneTransformEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        return cls(
            str(channel),
            str(address),
            joint=Bone(arguments[0]),
            position=CoordinateVector(
                x=arguments[1],
                y=arguments[2],
                z=arguments[3]
            ),
            rotation=Quaternion(
                x=arguments[4],
                y=arguments[5],
                z=arguments[6],
                w=arguments[7]
            )
        )


@dataclass(frozen=True, slots=True)
class DeviceTransformEvent(TransformEvent):
    """Device transform receiving event."""

    ADDRESS_PATTERN: ClassVar[str] = (
        f"/VMC/Ext/{{{','.join([t.value for t in DeviceType])}}}//"
    )
    """str: OSC address pattern matching."""

    joint: str
    """str: OpenVR device label or serial."""

    device_type: DeviceType
    """DeviceType: Device type."""

    is_local: bool
    """bool: If transform is relative to avatar, word space otherwise."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'DeviceTransformEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            DeviceTransformEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        return cls(
            str(channel),
            str(address),
            joint=str(arguments[0]),
            position=CoordinateVector(
                x=arguments[1],
                y=arguments[2],
                z=arguments[3]
            ),
            rotation=Quaternion(
                x=arguments[4],
                y=arguments[5],
                z=arguments[6],
                w=arguments[7]
            ),
            device_type=DeviceType(address.split('/')[3]),
            is_local=bool(address.count('/') > 4)
        )


@dataclass(frozen=True, slots=True)
class BlendShapeEvent(Event):
    """Blend shape event."""

    ADDRESS_PATTERN: ClassVar[str] = "/VMC/Ext/Blend/Val"
    """str: OSC address pattern matching."""

    key: str
    """str: Blend shape key."""

    value: float
    """float: Blend shape value."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'BlendShapeEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            BlendShapeEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        return cls(
            str(channel),
            str(address),
            key=arguments[0],
            value=arguments[1]
        )


@dataclass(frozen=True, slots=True)
class BlendShapeApplyEvent(Event):
    """Blend shape apply event."""

    ADDRESS_PATTERN: ClassVar[str] = "/VMC/Ext/Blend/Apply"
    """str: OSC address pattern matching."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'BlendShapeApplyEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            BlendShapeApplyEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        if len(arguments) != 0:
            raise ValueError(f"Arguments not empty: {arguments}")
        return cls(
            channel,
            address
        )


@dataclass(frozen=True, slots=True)
class StateEvent(Event):
    """Availability state event."""

    ADDRESS_PATTERN: ClassVar[str] = "/VMC/Ext/OK"
    """str: OSC address pattern matching."""

    model_state: ModelState
    """ModelState: Model state."""

    calibration_state: CalibrationState | None
    """CalibrationState | None: Calibration state."""

    calibration_mode: CalibrationMode | None
    """CalibrationMode | None: Calibration mode."""

    tracking_state: TrackingState | None
    """TrackingState | None: Tracking state."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'StateEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            StateEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        calibration_state: CalibrationState | None = None
        calibration_mode: CalibrationMode | None = None
        tracking_state: TrackingState | None = None
        match len(arguments):
            case 4:
                # Since VMC protocol specification v2.7.0.
                calibration_state = CalibrationState(arguments[1])
                calibration_mode = CalibrationMode(arguments[2])
                tracking_state = TrackingState(arguments[3])
            case 3:
                # Since VMC protocol specification v2.5.0.
                calibration_state = CalibrationState(arguments[1])
                calibration_mode = CalibrationMode(arguments[2])
            case 1:
                pass
            case _:
                raise ValueError(f"Invalid arguments: {arguments}")
        return cls(
            str(channel),
            str(address),
            model_state=ModelState(arguments[0]),
            calibration_state=calibration_state,
            calibration_mode=calibration_mode,
            tracking_state=tracking_state
        )


@dataclass(frozen=True, slots=True)
class RelativeTimeEvent(Event):
    """Relative time event."""

    ADDRESS_PATTERN: ClassVar[str] = "/VMC/Ext/T"
    """str: OSC address pattern matching."""

    delta: float
    """float: Relative frame time."""

    @classmethod
    def from_message_data(
        cls,
        channel: str,
        address: str,
        arguments: tuple[Any, ...]
    ) -> 'RelativeTimeEvent':
        """Abstract event constructor.

        Args:
            channel (str):
                Channel name.
            address (str):
                OSC address.
            arguments (tuple[Any, ...]):
                OSC arguments.

        Returns:
            RelativeTimeEvent:
                Instance.

        Raises:
            ValueError:
                If invalid arguments are given.

        """
        if len(arguments) != 1:
            raise ValueError(f"Invalid arguments: {arguments}")
        return cls(
            str(channel),
            str(address),
            delta=float(arguments[0])
        )
