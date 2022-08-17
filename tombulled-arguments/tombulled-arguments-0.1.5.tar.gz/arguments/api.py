import functools
import inspect
import itertools
from inspect import Signature
from typing import Any, Callable, Dict, Iterable, Tuple

from typing_extensions import Self


class Arguments:
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        args: Iterable[str] = (f"{arg!r}" for arg in self.args)
        kwargs: Iterable[str] = (
            f"{key}={value!r}" for key, value in self.kwargs.items()
        )

        return ", ".join(itertools.chain(args, kwargs))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"

    def __eq__(self, rhs: Self) -> bool:
        return self.args == rhs.args and self.kwargs == rhs.kwargs

    def __iter__(self) -> Iterable[Any]:
        value: Any
        for value in itertools.chain(self.args, self.kwargs.values()):
            yield value

    def __getitem__(self, index: int) -> Any:
        return list(self)[index]

    def __len__(self) -> int:
        return len(self.args) + len(self.kwargs)

    def __call__(self, func: Callable) -> Any:
        return self.call(func)

    def __or__(self, rhs: Self) -> Self:
        args: Tuple[Any, ...] = self.args + rhs.args
        kwargs: Dict[str, Any] = {**self.kwargs, **rhs.kwargs}

        return Arguments(*args, **kwargs)

    def union(self, *arguments: Self) -> Self:
        args: Arguments = self

        argument: Arguments
        for argument in arguments:
            args |= argument

        return args

    def call(self, func: Callable) -> Any:
        return func(*self.args, **self.kwargs)

    def partial(self, func: Callable, *args: Any, **kwargs: Any) -> Callable:
        return functools.partial(func, *(self.args + args), **{**self.kwargs, **kwargs})

    def bind(self, obj: Callable, /) -> "BoundArguments":
        return self.bind_signature(inspect.signature(obj))

    def bind_signature(self, signature: Signature, /) -> "BoundArguments":
        return BoundArguments(signature, *self.args, **self.kwargs)


class BoundArguments(Arguments):
    signature: Signature

    def __init__(self, signature: Signature, *args: Any, **kwargs: Any) -> None:
        bound_arguments: inspect.BoundArguments = signature.bind(*args, **kwargs)

        bound_arguments.apply_defaults()

        self.signature = signature

        super().__init__(*bound_arguments.args, **bound_arguments.kwargs)

    def asdict(self) -> Dict[str, Any]:
        return dict(self.signature.bind(*self.args, **self.kwargs).arguments)

    def get(self, parameter: str, /) -> Any:
        return self.asdict()[parameter]

    def has(self, parameter: str, /) -> bool:
        return parameter in self.asdict()
