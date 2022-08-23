
import sys, os, traceback
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
    stack = traceback.extract_stack()
    for frame in reversed(stack):
        try:
            return Path(frame.filename).resolve()
        except OSError:
            continue
    return os.getcwd()

def _append_to_path(pth):
    pth = str(pth)
    if pth not in sys.path:
        sys.path.insert(1, pth)

_append_to_path(get_root())

if __name__ == "__main__":
    from src.root_directory import __init__ # Test if importing works
    print("Project root: " + str(get_root()))
    print("Test successful!")
