import typing

from . import models


def annotation(func: typing.Optional[typing.Callable] = None, /, **opts: typing.Any):
    if func is None:

        def wrapper(func):
            return annotation(func, **opts)

        return wrapper

    def wrapper(*args, **kwargs):
        return models.Annotation(
            **{
                **dict(key=func.__name__),
                **opts,
                **dict(value=func(*args, **kwargs)),
            }
        )

    return wrapper


def marker(func: typing.Optional[typing.Callable] = None, /, **opts: typing.Any):
    if func is None:

        def wrapper(func):
            return marker(func, **opts)

        return wrapper

    return annotation(func, **opts)()
