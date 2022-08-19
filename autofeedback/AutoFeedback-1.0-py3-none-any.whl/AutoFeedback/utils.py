"""utilities for ensuring modules are installed"""


def check_module(modname):
    """ check if modname is installed, and if not, attempt to use pip to
    install it"""
    from importlib.util import find_spec
    installed = find_spec(modname) is not None
    if not installed:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", modname])
    return
