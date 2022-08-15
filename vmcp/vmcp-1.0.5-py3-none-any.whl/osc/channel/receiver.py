#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``receiver`` module of ``channel`` package."""

from typing import (
    TYPE_CHECKING,
    Any
)
from collections.abc import Callable
from uuid import UUID, uuid4
from ..typing import ArgumentsScheme
from .common import AbstractChannel
if TYPE_CHECKING:
    from .. import OSC


class Receiver(AbstractChannel):
    """Receiver."""

    _handler_methods: dict[UUID, object]

    def __init__(
        self,
        system: 'OSC',
        host: str,
        port: int,
        name: str
    ) -> None:
        """Channel constructor.

        Args:
            system (OSC):
                OSC system instance.
            host (str):
                Host DNS or IP (recommended).
            port (int):
                Host port.
            name (str):
                Channel name (arbitrary, but needs to be unique).

        Raises:
            ValueError:
                If ``name`` is already used.

        """
        super().__init__(system, host, port, name)
        self._handler_methods = {}

    def open(self) -> 'Receiver':
        """Open channel.

        Returns:
            Class:
                Object instance.

        """
        if not self.is_open:
            super().open()
            self.system.backend.server(self.host, self.port, self.name)
        return self

    def register_handler(
        self,
        address: str,
        handler: Callable[..., None],
        scheme: ArgumentsScheme | None = None,
        extra: Any | None = None
    ) -> UUID:
        """Register receiving handler.

        Args:
            address (str):
                OSC address pattern filter string expression.
            handler (Callable[..., None]):
                Handler function.
            scheme (ArgumentsScheme | None):
                Argument schemes (Default: Depends on backend).
            extra (Any | None):
                Extra parameter(s) for your handler function.

        Return:
            UUID:
                UUID object, which identifies the handler.

        """
        if scheme is None:
            scheme = self.system.backend.ARG_DEFAULT
        uuid = uuid4()
        method = self.system.backend.MethodFilter(
            addrpattern=address,
            function=lambda *args: (
                handler(*args[1:]) if args[0] is self.name else ()
            ),
            argscheme=(self.system.backend.ARG_READERNAME + scheme).scheme,
            extra=extra
        )
        self.system.backend.register_method(method)
        self._handler_methods[uuid] = method
        return uuid

    def unregister_handler(
        self,
        uuid: UUID
    ) -> None:
        """Unregister receiving handler.

        Args:
            uuid (UUID):
                UUID object, which identifies the handler.

        """
        self.system.backend.unregister_method(self._handler_methods.pop(uuid))

    def __repr__(self) -> str:
        """Return a string, representing the object in a reconstructable way.

        Returns:
            str:
                Representing the object in a reconstructable way.

        """
        return f"Receiver({self})"

    def close(self) -> None:
        """Close channel."""
        for uuid in self._handler_methods:
            self.unregister_handler(uuid)
        self.system.backend.get_channel(self.name).terminate()
        super().close()
