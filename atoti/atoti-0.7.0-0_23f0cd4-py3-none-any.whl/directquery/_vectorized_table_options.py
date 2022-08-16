from abc import ABC
from dataclasses import dataclass
from typing import Sequence

from atoti_core import keyword_only_dataclass

from .external_table import ExternalTableT
from .table_options import BaseExternalTableOptions


@keyword_only_dataclass
@dataclass(frozen=True)
class ExternalVectorizedTableOptions(BaseExternalTableOptions[ExternalTableT], ABC):

    index_column: str
    """Name of the column used as an index for the vectors."""

    vector_columns: Sequence[str]
    """Names of the columns that contain the vectors values."""
