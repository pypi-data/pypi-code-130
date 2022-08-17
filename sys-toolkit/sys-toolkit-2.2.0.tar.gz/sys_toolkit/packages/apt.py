"""
Apt package manager package list processing
"""

import re

from enum import Enum

from ..exceptions import PackageManagerError
from ..subprocess import run_command_lineoutput, CommandError

from .base import PackageList, Package


RE_PACKAGE_LINE = re.compile(
    r'(?P<status>[FRWchinprtu]+)\s+'
    r'(?P<name>[^\s]+)\s+'
    r'(?P<version>[^\s]+)\s+'
    r'(?P<architecture>[^\s]+)\s+'
    r'(?P<description>.*)'
)


class DpkgPackageDesiredState(Enum):
    """
    Desired deb package state (first letter in status output)
    """
    UNKNOWN = 'u'
    INSTALL = 'i'
    REMOVE = 'r'
    PURGE = 'p'
    HOLD = 'h'


class DpkgPackageCurrentState(Enum):
    """
    Current deb package state (second letter in status output)
    """
    NOT_INSTALLED = 'n'
    INSTALLED = 'i'
    CONFIG_FILES = 'c'
    UNPACKED = 'u'
    HALF_CONFIGURED = 'F'
    HALF_INSTALLED = 'h'
    TRIGGERS_AWAITING = 'W'
    TRIGGERS_PENDING = 't'


class DpkgPackageErrorState(Enum):
    """
    Error state for deb package (third letter in status output, usually missing)
    """
    REINSTALL_REQUIRED = 'R'


def parse_package_status_string(value: str):
    """
    Parse dpkg package status string (2-3 letter string with encoded states)
    """
    if not isinstance(value, str):
        return None, None, None
    if not 2 <= len(value) <= 3:
        raise PackageManagerError(f'Invalid package status string: {value}. String must be 2-3 letters long.')

    try:
        desired_state = DpkgPackageDesiredState(value[0])
    except ValueError as error:
        raise PackageManagerError(
            f'Invalid package status string: {value}: unexpected desired state {value[0]}'
        ) from error

    try:
        current_state = DpkgPackageCurrentState(value[1])
    except ValueError as error:
        raise PackageManagerError(
            f'Invalid package status string: {value}: unexpected current state {value[1]}'
        ) from error

    if len(value) == 3:
        try:
            error_state = DpkgPackageErrorState(value[2])
        except ValueError as error:
            raise PackageManagerError(
                f'Invalid package status string: {value}: unexpected error state {value[2]}'
            ) from error
    else:
        error_state = None

    return desired_state, current_state, error_state


# pylint: disable=too-few-public-methods
class DpkgPackage(Package):
    """
    Deb package in package listings
    """
    def __init__(self, name, version, architecture, description, status=None):
        super().__init__(name, version)
        self.architecture = architecture
        self.description = description
        self.desired_state, self.current_state, self.error_state = parse_package_status_string(status)


class DpkgPackageList(PackageList):
    """
    List of dpkg packages
    """
    def load_package_list(self):
        """
        Return list of deb packages using dpkg command
        """
        try:
            lines, _stderr = run_command_lineoutput('dpkg', '--list')
            for line in lines:
                match = RE_PACKAGE_LINE.match(line)
                if match:
                    package = DpkgPackage(**match.groupdict())
                    self[package.name] = package
        except CommandError as error:
            raise PackageManagerError(f'Error listing packages: {error}') from error
