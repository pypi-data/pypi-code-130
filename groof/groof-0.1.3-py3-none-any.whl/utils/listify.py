import typing

T = typing.TypeVar('T')


def listify(obj: T, cast_tuple=True) -> T | list[T]:
    if cast_tuple:
        if isinstance(obj, tuple):
            return list(obj)

    if isinstance(obj, list):
        return obj

    return [obj]
