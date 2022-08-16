from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_single_condition import BaseSingleCondition
from .comparison_operator import ComparisonOperator
from .coordinates import LevelCoordinates
from .keyword_only_dataclass import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class BaseLevelCondition(BaseSingleCondition):
    level_coordinates: LevelCoordinates
    operator: ComparisonOperator
    value: Any
