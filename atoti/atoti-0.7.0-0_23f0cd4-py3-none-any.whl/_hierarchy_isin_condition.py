from __future__ import annotations

from dataclasses import dataclass

from atoti_core import BaseHierarchyIsinCondition, keyword_only_dataclass

from ._level_condition import LevelCondition
from ._single_condition import SingleCondition
from .measure_description import MeasureDescription


@keyword_only_dataclass
@dataclass(frozen=True)
class HierarchyIsinCondition(SingleCondition, BaseHierarchyIsinCondition):
    @property
    def _measure_description(self) -> MeasureDescription:
        from ._measures.boolean_measure import BooleanMeasure

        operands = []

        for member_path in self.member_paths:
            condition = None
            for level_name, value in zip(self.level_names, member_path):
                level_coordinates = (
                    self.hierarchy_coordinates[0],
                    self.hierarchy_coordinates[1],
                    level_name,
                )

                if condition is not None:
                    condition = condition & LevelCondition(
                        level_coordinates=level_coordinates,
                        operator="eq",
                        value=value,
                    )
                else:
                    condition = LevelCondition(
                        level_coordinates=level_coordinates,
                        operator="eq",
                        value=value,
                    )

            if condition is not None:
                operands.append(condition._measure_description)

        if len(operands) == 1:
            return operands[0]

        return BooleanMeasure("or", (*operands,))
