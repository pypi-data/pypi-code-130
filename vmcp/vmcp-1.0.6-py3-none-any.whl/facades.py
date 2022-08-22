#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``facades`` module of ``vmcp`` package."""

from collections.abc import Callable
from .osc.channel import Receiver
from .events import Event


def on_receive(
    receiver: Receiver,
    event: type[Event],
    handler: Callable[[Event], None]
) -> None:
    """Event-based receiving handler registration facade method.

    Args:
        receiver (Receiver):
            OSC receiver instance.
        event (type[Event]):
            Event type class.
        handler (Callable[[Event], None]):
            Arbitrary handler function or method.

    """
    receiver.register_handler(
        event.ADDRESS_PATTERN,
        lambda *args, **kwargs: handler(
            event.from_message_data(*args, **kwargs)
        ),
        (
            receiver.system.backend.ARG_READERNAME +
            receiver.system.backend.ARG_ADDRESS +
            receiver.system.backend.ARG_DATA
        )
    )
