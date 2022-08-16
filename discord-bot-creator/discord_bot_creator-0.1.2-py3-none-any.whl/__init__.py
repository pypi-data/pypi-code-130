"""
DIscord Bot Creator
~~~~~~~~~~~~~~~~~~~
A basic discord bot creator for discord.py v2.0
:copyright: (c) 2022 CedricXBG
:license: MIT, see LICENSE for more details.
"""

__title__ = 'bot_creator'
__author__ = 'CedricXBG'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022 CedricXBG'
__version__ = '0.1.2'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=1, micro=2, releaselevel='final', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging, NamedTuple, Literal, VersionInfo