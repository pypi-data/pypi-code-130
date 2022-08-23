
from .client import Client
from .dbapi import connect
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

VERSION = (0, 2, 4)
__version__ = '.'.join(str(x) for x in VERSION)

__all__ = ['Client', 'connect']
