"""Predefined packages to use, if you want to use specific modules in MFF Pytex"""


from mff_pytex.utils import command
from typing import List


class Package:
    """Package class for adding packages to tex file.
    """
    def __init__(self, name: str, *params: str) -> None:
        """Initialize Package

        Args:
            name (str): Name of package.
            *params (str, optional): Optional parameters for package
        """
        self.name = name
        self.optional = params

    def __str__(self) -> str:
        """Return content string in tex form

        Returns:
            str: Content.
        """
        return command('usepackage', self.name, *self.optional)


package_list: List[Package] = list()
"""Package_list contains all packages used in tex document."""


def find_package(package: Package) -> bool:
    """Find package in package_list

    Args:
        package (Package)

    Returns:
        bool
    """
    global package_list
    for pkg in package_list:
        if pkg.name == package.name:
            return True
    return False


def add_package(*packages: Package) -> None:
    """Adds packages to package_list

    Args:
        *packages (Package): packages to add.
    """
    global package_list
    for package in packages:
        if not find_package(package):
            package_list.append(package)


def get_packages() -> List[Package]:
    """Returns package_list

    Returns:
        list[Package]: package_list
    """
    global package_list
    return package_list


def clear_packages() -> None:
    """Clears package_list
    """
    global package_list
    package_list.clear()
