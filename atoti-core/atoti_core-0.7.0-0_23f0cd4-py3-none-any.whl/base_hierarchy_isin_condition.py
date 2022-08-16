from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple

from .base_single_condition import BaseSingleCondition
from .coordinates import HierarchyCoordinates, LevelName
from .keyword_only_dataclass import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class BaseHierarchyIsinCondition(BaseSingleCondition):
    operator: str = field(default="hi", init=False)
    hierarchy_coordinates: HierarchyCoordinates
    level_names: Tuple[LevelName, ...]
    member_paths: Tuple[Tuple[Any, ...], ...]

    def __post_init__(self) -> None:
        for member_path in self.member_paths:
            if len(member_path) > len(self.level_names):
                raise ValueError(
                    f"Member path {member_path} contains more than {len(self.level_names)} elements which is the number of levels of the {self.hierarchy_coordinates} hierarchy."
                )

            if None in member_path:
                raise ValueError("None is not a valid member.")
