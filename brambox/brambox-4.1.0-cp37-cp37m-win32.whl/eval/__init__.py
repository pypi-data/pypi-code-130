"""
Brambox evaluation module |br|
This package contains functionality to automatically compute statistics with the correct values for certain packages.

The goal of this package is twofold:

    - Make sure that you use the correct settings when evaluating detections on a certain dataset
    - Learn how to use the brambox package by reading the source code of these implementations
"""
from ._coco import *
from ._tide import *
from ._tidal import *
