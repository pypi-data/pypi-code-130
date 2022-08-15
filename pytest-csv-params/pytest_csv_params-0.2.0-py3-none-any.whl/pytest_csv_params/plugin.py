"""
Pytest Plugin Entrypoint
"""

from _ptcsvp.cmdline import pytest_addoption as _pytest_addoption
from _ptcsvp.configure import pytest_configure as _pytest_configure
from _ptcsvp.configure import pytest_unconfigure as _pytest_unconfigure
from _ptcsvp.version import check_pytest_version, check_python_version

# Fist at all, check if the python & pytest version matches
check_python_version()
check_pytest_version()

# Basic config
pytest_configure = _pytest_configure
pytest_unconfigure = _pytest_unconfigure

# Command Line Arguments
pytest_addoption = _pytest_addoption
