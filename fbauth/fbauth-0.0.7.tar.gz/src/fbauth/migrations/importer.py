"""
    Auto-Importer
"""

import importlib
import pkgutil

def iter_namespace(ns_pkg):
    """https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/"""
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def import_module(single_app: str):
    """Import Single-Module"""
    try:
        module = importlib.import_module(single_app)
    except:
        module = None
    return module
