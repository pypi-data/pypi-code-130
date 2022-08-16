from abc import ABC
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from atoti_core import EMPTY_MAPPING, keyword_only_dataclass

from .external_table import ExternalTableT
from .table_options import BaseExternalTableOptions


@keyword_only_dataclass
@dataclass(frozen=True)
class ExternalTableOptions(
    BaseExternalTableOptions[ExternalTableT], ABC
):  # pylint: disable=keyword-only-dataclass
    _keys: Optional[Sequence[str]] = None
    _options: Mapping[str, Any] = EMPTY_MAPPING
