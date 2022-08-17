"""
Generate a single source of version for reporting from the package/cli.

This approach is used to be compatible with how poetry manages version, which
requires the version to be a literal in the pyproject.toml file (as of this
writing).
"""

try:
    from importlib.metadata import PackageNotFoundError  # type: ignore[import]
    from importlib.metadata import version as get_version
except ImportError:
    # fallback for python <3.8
    from importlib_metadata import PackageNotFoundError  # type: ignore[import,no-redef]
    from importlib_metadata import version as get_version  # type: ignore[no-redef]

# when running tests on the repo, provide a fallback value, since the
# memfault-cli package is not installed at that time
try:
    VERSION = get_version(__package__)
except PackageNotFoundError:
    VERSION = "dev"
