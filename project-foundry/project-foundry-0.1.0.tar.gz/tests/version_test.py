from __future__ import annotations

from packaging.version import parse


def test_version_package() -> None:
    """Test that __version__ is a valid version when importing from package."""
    from project_foundry import __version__

    parse(__version__)
