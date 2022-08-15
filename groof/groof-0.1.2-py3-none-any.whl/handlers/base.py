import typing
from dataclasses import dataclass, field

from ..filters.base import Filter


@dataclass
class Handler:
    func: typing.Callable[..., None]
    filters: list[Filter] = field(default_factory=list)
    exclusive: bool = True
    check_first: bool = False
    check_last: bool = False
    check_after_any: bool = False
