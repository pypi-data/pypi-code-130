"""Importing this module will set `mmf_setup.ROOT` and insert it into sys.path()."""
import warnings
from . import set_path

warnings.warn(
    "import mmf_setup.set_path.hgroot is deprecated.  Use mmf_setup.set_path() instead",
    DeprecationWarning,
)

set_path()
