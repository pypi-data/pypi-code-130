from enum import auto
from typing import Literal

from typing_extensions import TypeAlias

from .enums import NoValue


class Sentinel(NoValue):
    Missing = auto()


MissingType: TypeAlias = Literal[Sentinel.Missing]

Missing: MissingType = Sentinel.Missing
