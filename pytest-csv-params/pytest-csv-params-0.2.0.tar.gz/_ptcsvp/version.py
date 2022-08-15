"""
Check Version Information
"""
import sys
from typing import Tuple

from attr.exceptions import PythonTooOldError
from packaging.version import parse


def check_python_version(min_version: Tuple[int, int] = (3, 8)) -> None:
    """
    Check if the current version is at least 3.8
    """

    if sys.version_info < min_version:
        raise PythonTooOldError(f"At least Python {'.'.join(map(str, min_version))} required")


def check_pytest_version(min_version: Tuple[int, int] = (7, 1)) -> None:
    """
    Check if the current version is at least 7.1
    """

    from pytest import __version__ as pytest_version  # pylint: disable=import-outside-toplevel

    pytest_min_version = ".".join(map(str, min_version))
    parsed_min_version = parse(pytest_min_version)
    parsed_actual_version = parse(pytest_version)
    if parsed_actual_version < parsed_min_version:
        raise RuntimeError(f"At least Pytest {pytest_min_version} required")
