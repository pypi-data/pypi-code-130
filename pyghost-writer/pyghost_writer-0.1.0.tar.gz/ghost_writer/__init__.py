# -*- coding: utf-8 -*-

"""Top-level package for ghost_writer."""

__author__ = """J. Michael Burgess"""
__email__ = 'jburgess@mpe.mpg.de'


from .ghost_writer import ScriptGenerator
from .scriptify import scriptify_python

from .utils.logging import ghost_writer_config

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions
