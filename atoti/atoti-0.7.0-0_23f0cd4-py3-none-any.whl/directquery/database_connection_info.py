from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Mapping, Optional

from atoti_core import EMPTY_MAPPING, keyword_only_dataclass

from .._java_api import JavaApi
from .database_connection import ExternalDatabaseConnectionT
from .external_table import ExternalTableT


@keyword_only_dataclass
# See https://github.com/python/mypy/issues/5374.
@dataclass(frozen=True)  # type: ignore[misc]
class ExternalDatabaseConnectionInfo(
    Generic[ExternalDatabaseConnectionT, ExternalTableT], ABC
):
    """Information to connect to an external database."""

    _database_key: str
    _url: Optional[str]
    _password: Optional[str] = None
    _options: Mapping[str, Optional[str]] = EMPTY_MAPPING

    @abstractmethod
    def _get_database_connection(
        self, java_api: JavaApi
    ) -> ExternalDatabaseConnectionT:
        ...
