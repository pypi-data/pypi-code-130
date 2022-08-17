# -*- coding: utf-8 -*-

from __future__ import annotations

from .compiler import *
from .parser import *
from .transformer import *
from .visitor import *

__version__ = "v0.1.0"
__author__ = "Andy"


class VersionInfo:
    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def __repr__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other: VersionInfo) -> bool:
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )


version = VersionInfo(0, 1, 0)
