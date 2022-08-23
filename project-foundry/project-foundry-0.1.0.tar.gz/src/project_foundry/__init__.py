"""This file defines project-foundry's public API.

Everything explicitly re-exported using __all__ can be expected to only change in
backward compatible ways between minor versions.
"""
from __future__ import annotations

from ._version import __version__

__all__ = [
    "__version__",
]
