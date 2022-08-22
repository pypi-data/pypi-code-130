import sys
import subprocess
"""
System manager in a nutshell. Execute commands outside of Python\'s programming range.
"""
def python_version(encoding=sys.getdefaultencoding()):
    """
    Get the current version of Python.
    Be warned this refers to sys.executable as python.
    Modules in use:
    sys, subprocess
    """
    return (subprocess.run([sys.executable, "--version"], capture_output=True).stdout).decode(encoding)
