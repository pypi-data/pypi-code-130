# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from typing import Callable

# Custom Library

# Custom Packages
from AthenaDPGLib.data.globals import global_custom_dpg_items

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
def custom_dpg_item(name:str) -> Callable:
    """
    Decorator which assigns the method as a custom dpg item which can be used within the json ui files.
    Meant to be used within an inherited class of RunTimeParser
    """
    def decorator(fnc:Callable):
        global_custom_dpg_items[name] = fnc
    return decorator