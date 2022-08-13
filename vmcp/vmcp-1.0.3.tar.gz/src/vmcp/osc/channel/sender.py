#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``sender`` module of ``channel`` package."""

from ..typing import (
    Message,
    TimeTagType
)
from .common import AbstractChannel


class Sender(AbstractChannel):
    """Sender."""

    def open(self) -> 'Sender':
        """Open channel.

        Returns:
            Class:
                Object instance.

        """
        if not self.is_open:
            super().open()
            self.system.backend.client(self.host, self.port, self.name)
        return self

    def send(
        self,
        messages: Message | tuple[Message, ...] | list[Message],
        delay: TimeTagType | None = None
    ) -> None:
        """Send message(s).

        Args:
            messages (Message | tuple[Message, ...] | list[Message]):
                One or many ``Message``(s).
            delay (TimeTagType | None):
                Message processing delay (Default: Depends on backend).

        """
        if delay is None:
            delay = self.system.backend.TIME_DEFAULT
        packet: tuple[Message, ...] = ()
        if isinstance(messages, Message):
            packet = (messages,)
        else:
            packet = tuple(messages)
        self.system.backend.send(
            self.name,
            packet,
            delay
        )

    def __repr__(self) -> str:
        """Return a string, representing the object in a reconstructable way.

        Returns:
            str:
                Representing the object in a reconstructable way.

        """
        return f"Sender({self})"

    def close(self) -> None:
        """Close channel."""
        self.system.backend.get_channel(self.name).terminate()
        super().close()
