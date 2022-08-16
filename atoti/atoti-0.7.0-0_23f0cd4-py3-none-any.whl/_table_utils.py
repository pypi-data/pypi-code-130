from __future__ import annotations

from dataclasses import dataclass

from atoti_core import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class ColumnCoordinates:
    table_name: str
    column_name: str

    def __str__(self) -> str:
        return f"{self.table_name}.{self.column_name}"
