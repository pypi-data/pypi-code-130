"""Adds a project directory to the start of sys.path.

The main export of this module is the function set_path() which will set mmf_utils.ROOT
and insert it at the start of sys.path.  The algorithm for determining ROOT is as
follows starting from ``cwd`` (which is `'.'` by default but can be specified in the
call to ``set_path()``:

* A current value of ``mmf_setup.ROOT`` will override everything.
* An environmental variable ``MMF_SETUP_ROOT`` will override everything else.
* An explicit entry in the first ``pyproject.toml``::
    
    ```toml
    [tool.mmf_setup]
    ROOT = 'src'
    ```
* An explict entry in ``setup.cfg``::
    
    ```cfg
    [mmf_setup]
    ROOT = src
    ```
* The first parent directory to contain any of the files in ``_CONFIG_FILES`` or directories
    in ``_CONFIG_DIRS``.  Currently one of ``pyproject.toml``, ``setup.cfg``,
    ``setup.py``, ``.git``, or ``.hg``.

If none of these yields a valid directory for ROOT, then it will not be set.
"""

import configparser
import logging
import os
from pathlib import Path
import sys

import tomlkit

# https://stackoverflow.com/a/8706331/1088938
mmf_setup = __import__(__name__.split(".")[0])

__all__ = ["set_path", "set_root"]

_CONFIG_FILES = ["pyproject.toml", "setup.cfg", "setup.py"]
_CONFIG_DIRS = [".git", ".hg"]

_ERRORS = []


def log(msg, level=logging.INFO):
    logging.getLogger(__name__).log(level=level, msg=msg)


def set_root(cwd="."):
    """Set mmf_setup.ROOT return root.

    Ensures that root exists and is a directory.
    """
    root = get_root(cwd=cwd)
    if root:
        mmf_setup.ROOT = root
    elif hasattr(mmf_setup, "ROOT"):
        del mmf_setup.ROOT

    return root


def set_path(cwd="."):
    """Set root, insert root at start of sys.path, and return root."""
    root = set_root(cwd=cwd)
    if root:
        root = str(Path(root))
        if root in sys.path:
            sys.path.remove(root)
        sys.path.insert(0, root)
    return root


def get_root(cwd="."):
    """Return the root directory.

    Ensures that it exists and is a directory, otherwise returns None."""

    root = getattr(mmf_setup, "ROOT", os.environ.get("MMF_SETUP_ROOT", None))
    if root:
        root = Path(root)
        if root.exists() and root.is_dir():
            return root
        root = None

    root_dirs = get_root_dirs(cwd=cwd)
    for root_dir, config_files in root_dirs:
        for config_file in config_files:
            if config_file.parts[-1] == "pyproject.toml":
                root = get_toml_root(config_file)
                if root:
                    break

            if config_file.parts[-1] == "setup.cfg":
                root = get_cfg_root(config_file)
                if root:
                    break
    if root:
        if not Path(root).is_absolute():
            root = str(Path(config_file).parents[0] / root)
        return root

    if root_dirs:
        root = root_dirs[0][0]
    return root


def get_root_dirs(cwd="."):
    """Return a list `(root_dir, config_files)` of possible root directories and config files.

    Moves up the file tree checking for the existence of files in _CONFIG_FILES or
    directories in _CONFIG_DIRS starting from cwd and moving up.

    Returns
    -------
    root_dir : Path
       Potential root directory that exists.
    config_files : [Path]
       List of existing config files in root_dir.
    """

    root_dirs = []

    try:
        parents = (Path(cwd) / "placeholder").resolve().parents
    except FileNotFoundError:
        # Happens if cwd is not a valid directory for example...
        return root_dirs

    for root_dir in parents:
        config_files = [
            config_file
            for _file in _CONFIG_FILES
            for config_file in [root_dir / _file]
            if config_file.exists() and config_file.is_file()
        ]

        if not config_files:
            if not any(
                config_dir.exists() and config_dir.is_dir()
                for _dir in _CONFIG_DIRS
                for config_dir in [root_dir / _dir]
            ):
                continue
        root_dirs.append((root_dir, config_files))

    return root_dirs


def get_toml_root(filename):
    with open(filename) as f:
        doc = tomlkit.parse(f.read())
        try:
            root = doc["tool"]["mmf_setup"]["ROOT"]
        except tomlkit.exceptions.NonExistentKey:
            root = None
    return root


def get_cfg_root(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    root = None
    if config.has_section("mmf_setup"):
        if config.has_option("mmf_setup", "ROOT"):
            root = config.get("mmf_setup", "ROOT").strip()
    return root
