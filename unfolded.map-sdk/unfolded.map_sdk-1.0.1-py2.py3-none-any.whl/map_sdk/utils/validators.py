from functools import wraps
from typing import Any, Callable, Optional, Sequence, TypeVar

from unfolded.map_sdk.errors import MapSDKException

__all__ = ("validate_kwargs", "assert_not_rendered")

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def validate_kwargs(n_args: int = 2, positional_only: Optional[Sequence[str]] = None):
    """Checks to make sure both positional args and kwargs are not used"""
    # Note the default for n_args is 2 to account for self

    def decorator(func: FuncT) -> FuncT:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if len(args) >= n_args and len(kwargs) > 0:
                raise MapSDKException(
                    "Cannot pass in both positional arguments and kwargs, use one or the other."
                )

            # Language support for declaring positional-only arguments with / began in 3.8, and we
            # support 3.7
            # https://peps.python.org/pep-0570/
            if positional_only:
                positional_only_used = set(kwargs.keys()).intersection(positional_only)
                if len(positional_only_used) == 1:
                    raise MapSDKException(
                        f"'{list(positional_only_used)[0]}' is a positional-only argument."
                    )
                elif len(positional_only_used) > 1:
                    arg_list = ", ".join([f"'{arg}'" for arg in positional_only_used])
                    raise MapSDKException(f"{arg_list} are positional-only arguments.")

            return func(*args, **kwargs)

        # Incompatible return value type (got "Callable[[VarArg(Any), KwArg(Any)], Any]", expected "FuncT")
        return wrapper  # type:ignore[return-value]

    return decorator


def assert_not_rendered(func):
    """Assert that the class has not yet been rendered before calling this function"""

    @wraps(func)
    def wrap(self, *args, **kwargs):
        if self.rendered:
            raise MapSDKException(
                f"Cannot call {func.__name__} on already-rendered map"
            )

        return func(self, *args, **kwargs)

    return wrap
