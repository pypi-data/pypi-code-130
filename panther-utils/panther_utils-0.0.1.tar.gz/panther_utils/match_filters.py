import typing

from panther_config import detection

__all__ = ["deep_equal"]


def deep_equal(path: str, value: typing.Any) -> detection.PythonFilter:
    return detection.PythonFilter(
        func=_deep_equal,
        params={"path": path, "expected": value},
    )


def _deep_equal(obj: typing.Any, params: typing.Any) -> bool:
    import functools
    import collections

    path = params["path"]
    keys = path.split(".")
    expected = params["expected"]

    actual = functools.reduce(
        lambda d, key: d.get(key, None) if isinstance(d, collections.Mapping) else None,
        keys,
        obj,
    )

    return bool(actual == expected)
