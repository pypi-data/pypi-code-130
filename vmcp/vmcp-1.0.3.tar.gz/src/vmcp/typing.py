#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``typing`` module of ``vmcp`` package."""

from typing import overload
from dataclasses import dataclass
from enum import Enum
from math import (
    cos,
    sin,
    atan2,
    asin,
    sqrt
)
from time import time


# Availability
class ModelState(Enum):
    """VMC model state."""

    NOT_LOADED = 0
    LOADED = 1


class CalibrationState(Enum):
    """VMC calibration state."""

    UNCALIBRATED = 0
    WAITING_FOR_CALIBRATING = 1
    CALIBRATING = 2
    CALIBRATED = 3


class CalibrationMode(Enum):
    """VMC calibration mode."""

    NORMAL = 0
    MR_HAND = 1
    MR_FLOOR = 2


class TrackingState(Enum):
    """VMC tracking state."""

    BAD = 0
    OK = 1


# Devices
class DeviceType(str, Enum):
    """VMC device types."""

    HMD = "Hmd"
    CONTROLLER = "Con"
    TRACKER = "Tra"


# 3D Space
class Bone(str, Enum):
    """All 55 HumanBodyBones from Unity."""

    HIPS = "Hips"
    LEFT_UPPER_LEG = "LeftUpperLeg"
    RIGHT_UPPER_LEG = "RightUpperLeg"
    LEFT_LOWER_LEG = "LeftLowerLeg"
    RIGHT_LOWER_LEG = "RightLowerLeg"
    LEFT_FOOT = "LeftFoot"
    RIGHT_FOOT = "RightFoot"
    SPINE = "Spine"
    CHEST = "Chest"
    UPPER_CHEST = "UpperChest"
    NECK = "Neck"
    HEAD = "Head"
    LEFT_SHOULDER = "LeftShoulder"
    RIGHT_SHOULDER = "RightShoulder"
    LEFT_UPPER_ARM = "LeftUpperArm"
    RIGHT_UPPER_ARM = "RightUpperArm"
    LEFT_LOWER_ARM = "LeftLowerArm"
    RIGHT_LOWER_ARM = "RightLowerArm"
    LEFT_HAND = "LeftHand"
    RIGHT_HAND = "RightHand"
    LEFT_TOES = "LeftToes"
    RIGHT_TOES = "RightToes"
    LEFT_EYE = "LeftEye"
    RIGHT_EYE = "RightEye"
    JAW = "Jaw"
    LEFT_THUMB_PROXIMAL = "LeftThumbProximal"
    LEFT_THUMB_INTERMEDIATE = "LeftThumbIntermediate"
    LEFT_THUMB_DISTAL = "LeftThumbDistal"
    LEFT_INDEX_PROXIMAL = "LeftIndexProximal"
    LEFT_INDEX_INTERMEDIATE = "LeftIndexIntermediate"
    LEFT_INDEX_DISTAL = "LeftIndexDistal"
    LEFT_MIDDLE_PROXIMAL = "LeftMiddleProximal"
    LEFT_MIDDLE_INTERMEDIATE = "LeftMiddleIntermediate"
    LEFT_MIDDLE_DISTAL = "LeftMiddleDistal"
    LEFT_RING_PROXIMAL = "LeftRingProximal"
    LEFT_RING_INTERMEDIATE = "LeftRingIntermediate"
    LEFT_RING_DISTAL = "LeftRingDistal"
    LEFT_LITTLE_PROXIMAL = "LeftLittleProximal"
    LEFT_LITTLE_INTERMEDIATE = "LeftLittleIntermediate"
    LEFT_LITTLE_DISTAL = "LeftLittleDistal"
    RIGHT_THUMB_PROXIMAL = "RightThumbProximal"
    RIGHT_THUMB_INTERMEDIATE = "RightThumbIntermediate"
    RIGHT_THUMB_DISTAL = "RightThumbDistal"
    RIGHT_INDEX_PROXIMAL = "RightIndexProximal"
    RIGHT_INDEX_INTERMEDIATE = "RightIndexIntermediate"
    RIGHT_INDEX_DISTAL = "RightIndexDistal"
    RIGHT_MIDDLE_PROXIMAL = "RightMiddleProximal"
    RIGHT_MIDDLE_INTERMEDIATE = "RightMiddleIntermediate"
    RIGHT_MIDDLE_DISTAL = "RightMiddleDistal"
    RIGHT_RING_PROXIMAL = "RightRingProximal"
    RIGHT_RING_INTERMEDIATE = "RightRingIntermediate"
    RIGHT_RING_DISTAL = "RightRingDistal"
    RIGHT_LITTLE_PROXIMAL = "RightLittleProximal"
    RIGHT_LITTLE_INTERMEDIATE = "RightLittleIntermediate"
    RIGHT_LITTLE_DISTAL = "RightLittleDistal"


class BlendShapeKey(str, Enum):
    """BlendShapeKey interface."""


@dataclass(frozen=True, slots=True)
class CoordinateVector:
    """Cartesian coordinate vector."""

    x: float  # pylint: disable=invalid-name
    """float: x coordinate."""

    y: float  # pylint: disable=invalid-name
    """float: y coordinate."""

    z: float  # pylint: disable=invalid-name
    """float: z coordinate."""

    @classmethod
    def identity(cls) -> 'CoordinateVector':
        """Create an identity position.

        Returns:
            Position:
                Created identity position (x, y, z).

        >>> CoordinateVector.identity()
        CoordinateVector(0.0, 0.0, 0.0)

        """
        return cls(0.0, 0.0, 0.0)


@dataclass(frozen=True, slots=True)
class Quaternion:
    """Quaternion."""

    x: float  # pylint: disable=invalid-name
    """float: x component."""

    y: float  # pylint: disable=invalid-name
    """float: y component."""

    z: float  # pylint: disable=invalid-name
    """float: z component."""

    w: float  # pylint: disable=invalid-name
    """float: w component."""

    def __post_init__(self) -> None:
        """Post quaternion initialization.

        Raises:
            ValueError:
                If invalid component values are given.

        """
        if (
            pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2) + pow(self.w, 2)
        ) != 1:
            raise ValueError(
                (
                    f"Invalid quaternion values: "
                    f"x={self.x}, y={self.y}, z={self.z}, w={self.w}"
                )
            )

    @classmethod
    def identity(cls) -> 'Quaternion':
        """Create an identity quaternion.

        Returns:
            Quaternion:
                Created identity quaternion (x, y, z, w).

        >>> Quaternion.identity()
        0.0, 0.0, 0.0, 1.0

        """
        return cls(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def from_rotvec(
        cls,
        x: float,  # pylint: disable=invalid-name
        y: float,  # pylint: disable=invalid-name
        z: float  # pylint: disable=invalid-name
    ) -> 'Quaternion':
        """Create from rotation vector.

        Args:
            x (float):
                x dimension.
            y (float):
                y dimension.
            z (float):
                z dimension.

        .. _Source:
            https://github.com/scipy/scipy/blob/main/scipy/spatial/transform/_rotation.pyx#L872-L876

        """
        angle: float = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2))

        # Stolen from the `scipy` package
        if angle <= 1e-3:
            # small angle
            angle2 = angle * angle
            scale = 0.5 - angle2 / 48 + angle2 * angle2 / 3840
        else:
            # large angle
            scale = sin(angle / 2) / angle

        return cls(
            x * scale,
            y * scale,
            z * scale,
            cos(angle / 2)
        )

    @classmethod
    def from_euler(
        cls,
        phi: float,
        theta: float,
        psi: float
    ) -> 'Quaternion':
        """Create from euler angles.

        Args:
            phi (float):
                Rotation angle around the X axis (radian).
            theta (float):
                Rotation angle around the Y axis (radian).
            psi (float):
                Rotation angle around the Y axis (radian).

        Returns:
            Quaternion:
                Created quaternion (x, y, z, w).

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # x axis rotation angle
        cos_phi_half = cos(phi / 2)
        sin_phi_half = sin(phi / 2)
        # y axis rotation angle
        cos_theta_half = cos(theta / 2)
        sin_theta_half = sin(theta / 2)
        # z axis rotation angle
        cos_psi_half = cos(psi / 2)
        sin_psi_half = sin(psi / 2)
        # Calculation
        return cls(
            x=float(
                sin_phi_half * cos_theta_half * cos_psi_half -
                cos_phi_half * sin_theta_half * sin_psi_half
            ),
            y=float(
                cos_phi_half * sin_theta_half * cos_psi_half +
                sin_phi_half * cos_theta_half * sin_psi_half
            ),
            z=float(
                cos_phi_half * cos_theta_half * sin_psi_half -
                sin_phi_half * sin_theta_half * cos_psi_half
            ),
            w=float(
                cos_phi_half * cos_theta_half * cos_psi_half +
                sin_phi_half * sin_theta_half * sin_psi_half
            )
        )

    def to_euler(self) -> tuple[float, float, float]:
        """Convert to euler angles.

        Returns:
            tuple[float, float, float]:
                Phi, theta and psi (radian).

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # x axis rotation angle
        term0 = 2 * (self.w * self.x + self.y * self.z)
        term1 = 1 - 2 * (self.x * self.x + self.y * self.y)
        phi = atan2(term0, term1)
        # y axis rotation angle
        term2 = 2 * (self.w * self.y - self.z * self.x)
        term2 = 1 if term2 > 1 else term2
        term2 = -1 if term2 < -1 else term2
        theta = asin(term2)
        # y axis rotation angle
        term3 = 2 * (self.w * self.z + self.x * self.y)
        term4 = 1 - 2 * (self.y * self.y + self.z * self.z)
        psi = atan2(term3, term4)
        return phi, theta, psi

    def conjugate(self) -> 'Quaternion':
        """Return conjugated quaternion.

        Returns:
            Quaternion:
                Conjugated quaternion (x, y, z, w).

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # Calculation
        return Quaternion(
            x=-self.x,
            y=-self.y,
            z=-self.z,
            w=self.w
        )

    def multiply_by(
        self,
        quaternion: 'Quaternion'
    ) -> 'Quaternion':
        """Multiplicate quaternion with an given one and return the product.

        Returns:
            Quaternion:
                Multiplication product quaternion (x, y, z, w)

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # Calculation
        return Quaternion(
            x=float(
                self.w * quaternion.x +
                self.x * quaternion.w +
                self.y * quaternion.z -
                self.z * quaternion.y
            ),
            y=float(
                self.w * quaternion.y +
                self.y * quaternion.w +
                self.z * quaternion.x -
                self.x * quaternion.z
            ),
            z=float(
                self.w * quaternion.z +
                self.z * quaternion.w +
                self.x * quaternion.y -
                self.y * quaternion.x
            ),
            w=float(
                self.w * quaternion.w -
                self.x * quaternion.x -
                self.y * quaternion.y -
                self.z * quaternion.z
            )
        )


@dataclass(frozen=False, slots=True, init=False)
class Scale:
    """Scale."""

    width: float
    """float: Width dimension."""

    height: float
    """float: Height dimension."""

    length: float
    """float: Length dimension."""

    @overload
    def __init__(
        self,
        uniformly: float
    ) -> None:
        """Scale constructor.

        Args:
            uniformly (float):
                All dimensions.

        """

    @overload
    def __init__(
        self,
        width: float,
        height: float,
        length: float
    ) -> None:
        """Scale constructor.

        Args:
            width (float):
                Width dimension.
            height (float):
                Height dimension.
            length (float):
                Length dimension.

        """

    def __init__(
        self,
        *args: float,
        **kwargs: float
    ) -> None:
        """Implement scale constructor.

        Args:
            *args (float):
                1 OR 3 dimension arguments.
        Raises:
            ValueError:
                If invalid arguments are given.

        """
        args += tuple(kwargs.values())
        match len(args):
            case 1:
                self.width = self.height = self.length = args[0]
            case 3:
                self.width = args[0]
                self.height = args[1]
                self.length = args[2]
            case _:
                raise ValueError(f"Invalid parameters given: {str(args)}")


# Communication
class Timestamp(float):
    """Timestamp since the epoch in seconds with it's fractions."""

    def __new__(
        cls,
        at: float = None
    ) -> 'Timestamp':
        """Create a new instance of class ``Timestamp``.

        Args:
            at (Optional[float]):
                Seconds with it's fractions since the epoch.

        Returns:
            Timestamp:
                Object instance.

        """
        return super().__new__(cls, time() if at is None else at)

    def elapsed(self) -> float:
        """Return elapsed time in seconds with it's fractions as float.

        Returns:
            float:
                Elapsed time in seconds with it's fractions.

        >>> Timestamp().elapsed()
        0.0

        """
        return time() - self

    def __str__(self) -> str:
        """Return string representation of the object.

        Returns:
            str:
                Representation of the object.

        """
        return super().__repr__()

    def __repr__(self) -> str:
        """Return a string, representing the object in a reconstructable way.

        Returns:
            str:
                Representing the object in a reconstructable way.

        """
        return f"{self.__class__.__qualname__}(at={self})"
