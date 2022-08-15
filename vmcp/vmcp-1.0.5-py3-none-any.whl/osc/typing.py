#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``typing`` module of ``osc`` package."""

from dataclasses import dataclass
from typing import (
    TypeVar,
    Any
)
from abc import (
    ABCMeta,
    abstractmethod
)


@dataclass(frozen=True, slots=True)
class ArgumentsScheme:
    """Arguments scheme."""

    scheme: tuple[str, ...]
    """tuple[str, ...]: Scheme."""

    def __add__(
        self,
        other: 'ArgumentsScheme'
    ) -> 'ArgumentsScheme':
        """Combine with another arguments scheme and return it.

        Args:
            other (ArgumentsScheme):
                Another arguments scheme.

        Returns:
            ArgumentsScheme:
                Combined arguments scheme.

        """
        return ArgumentsScheme(self.scheme + other.scheme)


TimeTagClass = TypeVar(
    "TimeTagClass",
    bound="TimeTagType"
)


class TimeTagType(metaclass=ABCMeta):  # pylint: disable=too-few-public-methods
    """Time tag interface."""

    @classmethod
    @abstractmethod
    def from_unixtime(
        cls: type[TimeTagClass],
        time: float
    ) -> TimeTagClass:
        """Create ``TimeTag`` from UNIX epoch time.

        Args:
            time (float): UNIX epoch time (seconds since 1/1/1970).

        Returns:
            TimeTag: Seconds since 1/1/1900 (based on NTP timestamps).

        """


@dataclass(frozen=True, slots=True)
class Message:
    """Message."""

    address: str
    """str: OSC address pattern (beginng with '/')."""

    typetags: str
    """str: OSC type tag string (beginning with ',')."""

    arguments: Any
    """Any: OSC arguments."""
