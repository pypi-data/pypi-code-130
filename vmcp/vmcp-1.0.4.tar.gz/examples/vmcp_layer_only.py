#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""VMCP protocol layer only example."""

from vmcp.typing import (
    CoordinateVector,
    Quaternion
)
from vmcp.protocol import root_transform
from vmcp.events import (
    Event,
    RootTransformEvent
)


def received(event: Event):
    """Receive transmission."""
    print(repr(event))


position = CoordinateVector(1.0, 2.0, 3.0)
rotation = Quaternion.identity()

print(
    root_transform(
        position,
        rotation
    )
)
received(
    RootTransformEvent.from_message_data(
        "example",
        RootTransformEvent.ADDRESS_PATTERN,
        (
            "root",
            position.x, position.y, position.z,
            rotation.x, rotation.y, rotation.z, rotation.w
        )
    )
)
