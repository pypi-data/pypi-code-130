"""
OtoPy.

A Otoma Systems developed Lib Containing useful Tools and More.
"""
from pathlib import Path

VFile = Path(__file__).with_name('VERSION')
with VFile.open('r') as file:
    OtoPyVersion = file.read()

__version__ = OtoPyVersion
__author__ = 'Otoma Systems'
__name__= 'OtoPy'