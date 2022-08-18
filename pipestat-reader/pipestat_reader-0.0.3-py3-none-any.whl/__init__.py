import logmuse

from ._version import __version__
from .graphql import *

__classes__ = ["PipestatReader"]
__all__ = __classes__

logmuse.init_logger("pipestat_reader")
