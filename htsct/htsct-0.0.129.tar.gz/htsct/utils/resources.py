from . import _common

from importlib import import_module


def _resolve(name):
    """If name is a string, resolve to a module."""
    if hasattr(name, '__spec__'):
        return name
    return import_module(name)


def _get_package(package):
    """Take a package name or module object and return the module.

    If a name, the module is imported.  If the resolved module
    object is not a package, raise an exception.
    """
    module = _resolve(package)
    if module.__spec__.submodule_search_locations is None:
        raise TypeError('{!r} is not a package'.format(package))
    return module


def files(package):
    """
    Get a Traversable resource from a package
    """
    return _common.from_package(_get_package(package))
