"""A min testing package."""
from .sub_module import just_a_test
import pathlib
from importlib.metadata import PackageNotFoundError, version

VERSION = version(__package__)
