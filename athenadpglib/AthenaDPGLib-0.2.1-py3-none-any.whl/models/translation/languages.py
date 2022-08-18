# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import enum

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
class Languages(enum.Enum):
    """
    Support Enum for the `Translation` class as the sqllite table is divided into columns with the languages below.
    """
    english="english"
    nederlands="nederlands"