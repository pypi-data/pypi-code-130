#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Basic VMC protocol example."""

from math import radians
# OSC
from vmcp.osc import OSC
from vmcp.osc.typing import Message
from vmcp.osc.backend.osc4py3 import as_comthreads as backend
# VMC protocol layer
from vmcp.events import (
    Event,
    RootTransformEvent,
    BoneTransformEvent,
    BlendShapeEvent,
    BlendShapeApplyEvent,
    DeviceTransformEvent,
    StateEvent,
    RelativeTimeEvent
)
from vmcp.typing import (
    CoordinateVector,
    Quaternion,
    Bone,
    DeviceType,
    BlendShapeKey as AbstractBlendShapeKey,
    ModelState,
    Timestamp
)
from vmcp.protocol import (
    root_transform,
    bone_transform,
    device_transform,
    blendshape,
    blendshape_apply,
    state,
    time
)
# Facades for easy usage (optional)
from vmcp.facades import on_receive


# Required, if blend shapes are used.
class BlendShapeKey(AbstractBlendShapeKey):
    """Example model blend shape keys.

    Depends on the used avatar model.

    """

    # Eye blink
    EYES_BLINK_R = "Blink_R"
    # Face expressions
    FACE_FUN = "Fun"


LISTENING = True


def received(event: Event):
    """Receive transmission."""
    print(event)
    if isinstance(event, DeviceTransformEvent):
        print(event.device_type)
        print(event.is_local)
    if isinstance(event, RelativeTimeEvent):
        global LISTENING  # pylint: disable=global-statement
        LISTENING = False


try:
    osc = OSC(backend)
    with osc.open():
        # Receiver
        in1 = osc.create_receiver("127.0.0.1", 39539, "receiver1").open()
        on_receive(in1, RootTransformEvent, received)
        on_receive(in1, BoneTransformEvent, received)
        on_receive(in1, DeviceTransformEvent, received)
        on_receive(in1, BlendShapeEvent, received)
        on_receive(in1, BlendShapeApplyEvent, received)
        on_receive(in1, StateEvent, received)
        on_receive(in1, RelativeTimeEvent, received)
        # Sender
        osc.create_sender("127.0.0.1", 39539, "sender1").open().send(
            (
                Message(*root_transform(
                    CoordinateVector(.5, .2, .5),
                    Quaternion.identity()
                )),
                Message(*bone_transform(
                    Bone.LEFT_UPPER_LEG,
                    CoordinateVector.identity(),
                    Quaternion.from_euler(0, 0, radians(-45))
                )),
                Message(*bone_transform(
                    Bone.RIGHT_LOWER_ARM,
                    CoordinateVector.identity(),
                    Quaternion(0, 0, 0.3826834323650898, 0.9238795325112867)
                )),
                Message(*device_transform(
                    DeviceType.HMD,
                    "Head",
                    CoordinateVector.identity(),
                    Quaternion.identity()
                )),
                Message(*blendshape(
                    BlendShapeKey.FACE_FUN,
                    1.0
                )),
                Message(*blendshape(
                    BlendShapeKey.EYES_BLINK_R,
                    1.0
                )),
                Message(*blendshape_apply()),
                Message(*state(ModelState.LOADED)),
                Message(*time(Timestamp()))
            )
        )
        # Processing
        while LISTENING:
            osc.run()
except KeyboardInterrupt:
    print("Canceled.")
finally:
    osc.close()
