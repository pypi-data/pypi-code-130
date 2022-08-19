from typing import Callable, TypeVar, Union

from .models import ParameterSpecification
from .sentinels import Missing, MissingType

T = TypeVar("T")


def Param(
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing
) -> ParameterSpecification[T]:
    return ParameterSpecification(default=default, default_factory=default_factory)
