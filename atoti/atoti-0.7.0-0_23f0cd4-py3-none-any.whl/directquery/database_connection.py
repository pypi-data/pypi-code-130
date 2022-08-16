from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Mapping, Optional, TypeVar

from atoti_core import keyword_only_dataclass

from atoti.type import DataType

from .._directquery_core import ExternalTableId
from .._java_api import JavaApi
from .external_table import ExternalTable, ExternalTableT
from .external_tables import ExternalDatabaseTables


@keyword_only_dataclass
# See https://github.com/python/mypy/issues/5374.
@dataclass(frozen=True)  # type: ignore[misc]
class ExternalDatabaseConnection(Generic[ExternalTableT], ABC):
    """Connection to an external database."""

    _java_api: JavaApi
    _database_key: str

    @property
    def tables(self) -> ExternalDatabaseTables[ExternalTableT]:
        """All the tables of the external database."""
        table_descriptions = self._java_api.get_external_tables(self._database_key)
        return ExternalDatabaseTables(
            _tables=table_descriptions,
            _database_key=self._database_key,
            _create_table=lambda table_id: self._discover_and_create_table(table_id),
        )

    @abstractmethod
    def _create_table(
        self,
        table_id: ExternalTableId,
        /,
        *,
        types: Mapping[str, DataType],
    ) -> ExternalTableT:
        ...

    def _discover_and_create_table(
        self,
        table_id: ExternalTableId,
    ) -> ExternalTableT:
        columns = self._java_api.get_external_table_schema(
            self._database_key, table=table_id
        )
        return self._create_table(table_id, types=columns)


class ExternalDatabaseWithCache(ExternalDatabaseConnection[ExternalTableT]):
    """A database where caching can be toggled."""

    @property
    def cache(self) -> Optional[bool]:
        """Whether the external database should cache the query results or not."""
        return self._java_api.get_external_database_cache(self._database_key)

    @cache.setter
    def cache(self, value: bool) -> None:
        self._java_api.set_external_database_cache(self._database_key, value)


ExternalDatabaseConnectionT = TypeVar(
    "ExternalDatabaseConnectionT",
    bound=ExternalDatabaseConnection[ExternalTable],
)
