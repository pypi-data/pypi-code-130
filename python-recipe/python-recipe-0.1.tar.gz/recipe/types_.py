from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class RecipeResult:
    actual_value: str = ""
    last_value: str = ""
    error: Optional[Exception] = None


class _NULL:
    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __eq__(self, other):
        return isinstance(other, _NULL)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "NULL"

    def __repr__(self):
        return "NULL"


NULL = _NULL()
