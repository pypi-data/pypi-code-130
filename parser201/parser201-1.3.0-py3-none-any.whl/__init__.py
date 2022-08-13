"""
.. include:: ../../docs/intro.md
"""

__version__ = '1.3.0'


from .classes import FMT
from .classes import TZ
from .classes import LogParser

# pdoc will look here to determine which members to leave out of the
# documentation.
__pdoc__ = {}
__pdoc__['classes.FMT'] = False
__pdoc__['classes.TZ'] = False
__pdoc__['classes.LogParser.__str__'] = True
__pdoc__['classes.LogParser.__eq__'] = True
