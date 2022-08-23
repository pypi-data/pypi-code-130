from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version(__package__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"  # pragma: no cover
