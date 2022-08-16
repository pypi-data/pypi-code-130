from abc import ABC
from typing import Generic

from .external_table import ExternalTableT


class BaseExternalTableOptions(Generic[ExternalTableT], ABC):
    """Options to customize an external table."""
