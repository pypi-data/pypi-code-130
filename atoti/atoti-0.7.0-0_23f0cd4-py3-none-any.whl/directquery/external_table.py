from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Mapping, TypeVar

from atoti_core import ReprJson, keyword_only_dataclass

from .._directquery_core import ExternalTableId
from ..type import DataType


@keyword_only_dataclass
@dataclass(frozen=True)
class ExternalTable(ABC):
    """Table of an external database."""

    table_id: ExternalTableId
    """The ID of the table."""

    types: Mapping[str, DataType]
    """Mapping from the name of each column to their type."""

    _database_key: str

    def _repr_json_(self) -> ReprJson:
        data = {name: str(datatype) for name, datatype in self.types.items()}
        return data, {"expanded": True, "root": self.table_id.table_name}

    @property
    def name(self) -> str:
        """Name of the table."""
        return self.table_id.table_name


ExternalTableT = TypeVar("ExternalTableT", bound=ExternalTable, covariant=True)
