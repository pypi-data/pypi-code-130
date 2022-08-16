from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple

from .base_single_condition import BaseSingleCondition
from .coordinates import LevelCoordinates
from .keyword_only_dataclass import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class BaseLevelIsinCondition(BaseSingleCondition):
    operator: str = field(default="li", init=False)
    level_coordinates: LevelCoordinates
    members: Tuple[Any, ...]

    def __post_init__(self) -> None:
        if None in self.members:
            raise ValueError("None is not a valid member.")
