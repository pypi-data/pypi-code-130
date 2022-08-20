import signal
import subprocess
import sys
import os
from typing import List, TextIO
import re

__all__ = ["linger", "tee_stdio", "purge_module_cache"]

def linger():
    "Prevents the process from being terminated when its containing shell exits."
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN) #! this interferes with tee?


def tee_stdio(out_file_path: str, targets: List[TextIO] = [sys.stdout, sys.stdout]):
    "Duplicates stdin and stdout to a specified file path."
    tee = subprocess.Popen(["tee", out_file_path], stdin=subprocess.PIPE)
    assert tee.stdin is not None
    for target in targets:
        os.dup2(tee.stdin.fileno(), target.fileno())


def purge_module_cache(module_name: str, ignore_pattern=r".*_static.py$"):
    "Give a module name, removes this module and any child module (recursively) from the sys.modules cache."
    for key in sys.modules.keys():
        if (
            re.match(rf"\.?{module_name}\.?", key)
            and not re.match(ignore_pattern, module_name)
        ):
            del sys.modules[key]