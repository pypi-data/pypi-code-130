
import sys, os, inspect
from pathlib import Path

__all__ = ["get_root"]

def get_root():
    file = _get_inspectable_path()
    for i in range(len(file.parts) - 1):
        directory = file.parents[i]
        if (directory/".git").is_dir() or (directory/".project-root").is_file():
            return directory

    assert False, "Project root not found. Please add an empty .project-root file to the root or turn it into a git repository."

def _get_inspectable_path():
    stack = inspect.stack()
    this_file = stack[0].filename
    for frame in stack:
        if frame.filename == this_file:
            continue
        if frame.filename[0] == "<":
            continue
        return Path(frame.filename).resolve()
    return Path(os.getcwd()).resolve()

def _append_to_path(pth):
    pth = str(pth)
    if pth not in sys.path:
        sys.path.insert(1, pth)

_append_to_path(get_root())
