#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""System module of ``osc`` package."""

from logging import Logger
from typing import (
    Literal,
    TypeVar
)
from types import TracebackType
from .backend.typing import BackendType
from .channel import (
    Sender,
    Receiver
)

OSCClass = TypeVar("OSCClass", bound='OSC')


class OSC:
    """Open Sound Control (OSC) network protocol system."""

    _senders: dict[str, Sender]
    """dict[str, Sender]: Holds sender channel references."""

    _receivers: dict[str, Receiver]
    """dict[str, Receiver]: Holds receiver channel references."""

    @property
    def backend(self) -> BackendType:
        """BackendType: Returns system's currently used backend module."""
        return self._backend

    @property
    def is_open(self) -> bool:
        """bool: Returns whether the system is currently ready to use."""
        return self._opened

    def __init__(
        self,
        backend: BackendType,
        logger: Logger = None
    ) -> None:
        """OSC constructor.

        Args:
            backend (BackendType):
                Backend module.
            logger (Optional[Logger]):
                Logger instance.

        """
        self._senders = {}
        self._receivers = {}
        self._opened = False
        self._backend = backend
        self._logger = logger

    def open(self) -> 'OSC':
        """Start system.

        Returns:
            OSC:
                Object instance.

        """
        if not self.is_open:
            self.backend.startup(
                logger=self._logger
            )
            self._opened = True
        return self

    def __enter__(self: OSCClass) -> OSCClass:
        """Return the object instance for usage of the ``with`` statement.

        Returns:
            OSCClass:
                Object instance.

        """
        self.open()
        return self

    def create_sender(
        self,
        host: str,
        port: int,
        name: str
    ) -> Sender:
        """Create sender channel.

        Args:
            host (str):
                Host DNS or IP (recommended).
            port (int):
                Port.
            name (str):
                Channel name (arbitrary, but need to be unique).

        Returns:
            Sender:
                Channel instance.

        Raises:
            ValueError:
                If ``name`` is already used.

        """
        sender = Sender(self, host, port, name)
        self._senders[name] = sender
        return sender

    def get_sender(
        self,
        name: str
    ) -> Sender:
        """Get sender channel instance by it's name.

        Args:
            name (str):
                Channel name.

        Returns:
            Sender:
                Channel instance.

        Raises:
            KeyError:
                If ``name`` does not exists.

        """
        return self._senders[name]

    def create_receiver(
        self,
        host: str,
        port: int,
        name: str
    ) -> Receiver:
        """Create receiver channel.

        Args:
            host (str):
                Host DNS or IP (recommended).
            port (int):
                Port.
            name (str):
                Channel name (arbitrary, but need to be unique).

        Returns:
            Receiver:
                Channel instance.

        Raises:
            ValueError:
                If ``name`` is already used.

        """
        receiver = Receiver(self, host, port, name)
        self._receivers[name] = receiver
        return receiver

    def get_receiver(
        self,
        name: str
    ) -> Receiver:
        """Get receiver channel instance by it's name.

        Args:
            name (str):
                Channel name.

        Returns:
            Receiver:
                Channel instance.

        Raises:
            KeyError:
                If ``name`` does not exists.

        """
        return self._receivers[name]

    def run(self) -> None:
        """Process on every invoke."""
        self.backend.process()

    def __str__(self) -> str:
        """Return string representation of the object.

        Returns:
            str:
                Representation of the object.

        """
        return (
            f"{{'sender': {list(self._senders.values())},"
            f" 'receiver': {list(self._receivers.values())}}}"
        )

    def close(self) -> None:
        """Shut down system."""
        self.backend.terminate()
        self._opened = False

    def __exit__(
        self,
        exc_type: type[BaseException] = None,
        exc_value: BaseException = None,
        traceback: TracebackType = None
    ) -> Literal[False]:
        """Return everytime ``False`` if exiting the runtime context.

        Args:
            exc_type (Optional[type[BaseException]]):
                Exception type.
            exc_value (Optional[BaseException]):
                Exception instance.
            traceback (Optional[TracebackType]):
                Exception context.

        Returns:
            bool:
                Everytime ``False``.

        """
        self.close()
        return False
