from typing import Any, Callable, Hashable, Optional, Tuple, TypeVar, Union

from typing_extensions import ParamSpec

from .models import Annotation

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
PS = ParamSpec("PS")


def annotation(
    func: Optional[Callable[PS, V]] = None,
    /,
    *,
    key: Optional[K] = None,
    inherited: bool = False,
    repeatable: bool = False,
    stored: bool = True,
    targets: Tuple[type, ...] = (type, object),
) -> Union[
    Callable[[Callable[PS, V]], Callable[PS, Annotation[Any, V]]],
    Callable[PS, Annotation[Any, V]],
]:
    def decorator(func: Callable[PS, V], /) -> Callable[PS, Annotation[Any, V]]:
        def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> Annotation[Any, V]:
            return Annotation(
                key=key if key is not None else func.__name__,
                value=func(*args, **kwargs),
                inherited=inherited,
                repeatable=repeatable,
                stored=stored,
                targets=targets,
            )

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def marker(
    func: Optional[Callable[[], V]] = None,
    /,
    *,
    key: Optional[K] = None,
    inherited: bool = False,
    repeatable: bool = False,
    stored: bool = True,
    targets: Tuple[type, ...] = (type, object),
) -> Union[Callable[[Callable[[], V]], Annotation[Any, V]], Annotation[Any, V]]:
    def decorator(func: Callable[[], V], /) -> Annotation[Any, V]:
        return Annotation(
            key=key if key is not None else func.__name__,
            value=func(),
            inherited=inherited,
            repeatable=repeatable,
            stored=stored,
            targets=targets,
        )

    if func is None:
        return decorator

    return decorator(func)
