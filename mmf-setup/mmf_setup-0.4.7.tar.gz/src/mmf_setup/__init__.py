import os.path

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

from .notebook_configuration import nbinit
from .set_path import set_path

__version__ = metadata.version(__name__)

__all__ = [
    "nbinit",
    "set_path",
    "MMF_SETUP",
    "DATA",
    "HGTHEMES",
    "NBTHEMES",
    "HGRC_LGA",
    "HGRC_FULL",
]

MMF_SETUP = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(MMF_SETUP, "_data")
HGRC_LGA = os.path.join(DATA, "hgrc.lga")
HGRC_FULL = os.path.join(DATA, "hgrc.full")
HGTHEMES = os.path.join(DATA, "hgthemes")
NBTHEMES = os.path.join(DATA, "nbthemes")
