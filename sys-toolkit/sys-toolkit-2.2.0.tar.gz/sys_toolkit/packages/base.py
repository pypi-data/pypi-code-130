"""
Base class for operating system package manager package handling
"""
import re

from ..collection import CachedMutableMapping
from ..exceptions import PackageManagerError


# pylint: disable=too-few-public-methods
class Package:
    """
    Abstract base class for packages
    """
    def __init__(self, name, version=None):
        self.name = name
        self.version = version

    def __repr__(self):
        return self.name


class PackageList(CachedMutableMapping):
    """
    Base class for package manager package lists
    """
    # pylint: disable=arguments-differ
    def update(self):
        """
        Update cached list of packaging manager packages
        """
        self.__start_update__()
        try:
            self.load_package_list()
        except PackageManagerError as error:
            self.__reset__()
            raise PackageManagerError(error) from error
        self.__finish_update__()

    def load_package_list(self):
        """
        Update list of packages
        """
        raise NotImplementedError('load_package_list() must be implemented in child class')

    def filter(self, pattern):
        """
        Filter package names matching specified regexp pattern
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        matches = []
        for package in self.values():
            if pattern.match(package.name):
                matches.append(package)
        return matches
