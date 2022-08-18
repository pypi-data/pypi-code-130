"""Integrate LaminDB ingestion with bBFX pipelines.

Import the package::

   import lndb_bfx_pipeline

This is the complete API reference:

.. autosummary::
   :toctree: .

   BfxRun
"""

__version__ = "0.1.0"  # denote a pre-release for 0.1.0 with 0.1a1

from . import schema
from ._core import BfxRun, get_bfx_files_from_folder, parse_bfx_file_type  # noqa
