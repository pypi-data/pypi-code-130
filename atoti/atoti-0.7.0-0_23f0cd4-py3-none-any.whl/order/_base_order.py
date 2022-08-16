from abc import ABC, abstractmethod
from dataclasses import dataclass

from atoti_core import keyword_only_dataclass


@keyword_only_dataclass
# See https://github.com/python/mypy/issues/5374.
@dataclass(frozen=True)  # type: ignore[misc]
class BaseOrder(ABC):
    """Base class for orders."""

    @property
    @abstractmethod
    def _key(self) -> str:
        ...
