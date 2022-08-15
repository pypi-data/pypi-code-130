#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Common module of ``channel`` package."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import OSC


class AbstractChannel(metaclass=ABCMeta):
    """Abstract channel."""

    @property
    def system(self) -> 'OSC':
        """OSC: Returns ``OSC`` system instance."""
        return self._system

    @property
    def is_open(self) -> bool:
        """bool: Returns whether the channel is currently open."""
        return self._opened

    @property
    def host(self) -> str:
        """str: Host DNS or IP address."""
        return str(self._host)

    @property
    def port(self) -> int:
        """int: Host port."""
        return int(self._port)

    @property
    def name(self) -> str:
        """str: Channel name."""
        return str(self._name)

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
        self._opened = False
        self._host, self._port, self._name = host, port, name
        self._system = system

    @abstractmethod
    def open(self) -> 'AbstractChannel':
        """Open channel.

        Returns:
            Class:
                Object instance.

        """
        self._opened = True
        return self

    def __eq__(self, other) -> bool:
        """Return ``True`` if an object is identical to ``other`` object.

        Args:
            other (Client):
                Other object for comparison.

        Returns:
            bool:
                ``True`` if identical, otherwise ``False``.

        """
        return (
            self.host == other.host and
            self.port == other.port and
            self.name == other.name
        )

    def __hash__(self) -> int:
        """Return hash value to quickly compare keys for dictionary lookup.

        Returns:
            int:
                Hash value.

        """
        return hash((self.host, self.port, self.name))

    def __str__(self) -> str:
        """Return string representation of the object.

        Returns:
            str:
                Representation of the object.

        """
        return f"{self.host}, {self.port}, {self.name}"

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string, representing the object in a reconstructable way.

        Returns:
            str:
                Representing the object in a reconstructable way.

        """
        return f"({self})"

    @abstractmethod
    def close(self) -> None:
        """Close channel."""
        self._opened = False
