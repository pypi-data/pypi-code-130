#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``common`` module of ``osc4py3`` backend package."""

from typing import Callable
from osc4py3.oscmethod import (
    MethodFilter,
    OSCARG_DATA,
    OSCARG_DATAUNPACK,
    OSCARG_MESSAGE,
    OSCARG_MESSAGEUNPACK,
    OSCARG_ADDRESS,
    OSCARG_TYPETAGS,
    OSCARG_EXTRA,
    OSCARG_EXTRAUNPACK,
    OSCARG_METHODFILTER,
    OSCARG_PACKOPT,
    OSCARG_READERNAME,
    OSCARG_SRCIDENT,
    OSCARG_READTIME
)
from osc4py3.oscbuildparse import (
    OSCMessage,
    OSCBundle,
    OSCtimetag,
    unixtime2timetag,
    OSC_IMMEDIATELY
)
from osc4py3.oscdispatching import (
    register_method,
    unregister_method,
    globdisp,
    all_dispatchers
)
from osc4py3.oscchannel import get_channel
from ...typing import (
    ArgumentsScheme,
    TimeTagType,
    Message
)

# Arguments scheme constants
ARG_DATA = ArgumentsScheme(OSCARG_DATA)
ARG_DATAUNPACK = ArgumentsScheme(OSCARG_DATAUNPACK)
ARG_MESSAGE = ArgumentsScheme(OSCARG_MESSAGE)
ARG_MESSAGEUNPACK = ArgumentsScheme(OSCARG_MESSAGEUNPACK)
ARG_ADDRESS = ArgumentsScheme(OSCARG_ADDRESS)
ARG_TYPETAGS = ArgumentsScheme(OSCARG_TYPETAGS)
ARG_EXTRA = ArgumentsScheme(OSCARG_EXTRA)
ARG_EXTRAUNPACK = ArgumentsScheme(OSCARG_EXTRAUNPACK)
ARG_METHODFILTER = ArgumentsScheme(OSCARG_METHODFILTER)
ARG_PACKOPT = ArgumentsScheme(OSCARG_PACKOPT)
ARG_READERNAME = ArgumentsScheme(OSCARG_READERNAME)
ARG_SRCIDENT = ArgumentsScheme(OSCARG_SRCIDENT)
ARG_READTIME = ArgumentsScheme(OSCARG_READTIME)
ARG_DEFAULT = ARG_DATAUNPACK


class TimeTag(TimeTagType, OSCtimetag):
    """Time tag."""

    @classmethod
    def from_unixtime(cls, time: float) -> 'TimeTag':
        """Create ``TimeTag`` from UNIX epoch time.

        Args:
            time (float): UNIX epoch time (seconds since 1/1/1970).

        Returns:
            TimeTag: Seconds since 1/1/1900 (based on NTP timestamps).

        """
        return cls(*unixtime2timetag(time))


# TimeTag constants
TIME_IMMEDIATELY = TimeTag(*OSC_IMMEDIATELY)
TIME_DEFAULT = TIME_IMMEDIATELY


def create_send(
    send_function: Callable[[OSCBundle, str], None]
) -> Callable[[str, tuple[Message, ...], TimeTagType], None]:
    """Create send function.

    Arg:
        send_function (Callable[[OSCBundle, str], None]):
            Backend's send function.

    Returns:
        Callable[[str, tuple[Message, ...], TimeTagType], None]:
            Final send function.

    """
    def send(
        channel_name: str,
        packet: tuple[Message, ...],
        delay: TimeTagType
    ) -> None:
        """Send message(s).

        Args:
            channel_name (str):
                Channel name.
            packet (tuple[Message, ...]):
                Message(s).
            delay (TimeTagType):
                Time tag.

        """
        send_function(
            OSCBundle(
                delay,
                map(
                    lambda message: OSCMessage(
                        message.address,
                        message.typetags,
                        message.arguments
                    ),
                    packet
                )
            ),
            channel_name
        )
    return send


__all__ = [
    "MethodFilter",
    "ARG_DATA",
    "ARG_DATAUNPACK",
    "ARG_MESSAGE",
    "ARG_MESSAGEUNPACK",
    "ARG_ADDRESS",
    "ARG_TYPETAGS",
    "ARG_EXTRA",
    "ARG_EXTRAUNPACK",
    "ARG_METHODFILTER",
    "ARG_PACKOPT",
    "ARG_READERNAME",
    "ARG_SRCIDENT",
    "ARG_READTIME",
    "ARG_DEFAULT",
    "create_send",
    "TimeTag",
    "TIME_IMMEDIATELY",
    "TIME_DEFAULT",
    "register_method",
    "unregister_method",
    "globdisp",
    "all_dispatchers",
    "get_channel"
]
