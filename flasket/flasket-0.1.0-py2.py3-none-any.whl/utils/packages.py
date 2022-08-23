import importlib
import os
import sys
import traceback

from boltons.fileutils import iter_find_files


def load_package(name: str, refresh: bool = False) -> object:
    """
    Import a package by name

    Parameters
    ----------
    package: str
        The name argument specifies what module to import in absolute terms
        (e.g. pkg.mod.example).

    refresh: bool
        Reload the module to apply changes if file was modified.

    Returns
    -------
    object:
        the package
    """
    try:
        pkg = importlib.import_module(name)
        if refresh:
            importlib.reload(pkg)
        return pkg
    except Exception:
        print(traceback.print_exc(), file=sys.stderr)
        raise


def load_packages(path: str, logger: object = None, callback: callable = None) -> None:
    """
    Recursively load all packages in path.

    Parameters
    ----------
    path: str
        Path to search.

    logger: object
        Logger

    callback: callable
        Function to call after each succesful import.
    """
    files = list(iter_find_files(path, "*.py"))
    packages = sorted([os.path.relpath(f).replace("/", ".").replace(".py", "") for f in files])

    # Try to load every package
    try:
        for package in sorted(packages):
            if logger:
                logger.debug(f"Loading package '{package}'...")
            pkg = load_package(package)
            if callback and pkg:
                callback(pkg)
    except Exception:
        sys.exit(1)
