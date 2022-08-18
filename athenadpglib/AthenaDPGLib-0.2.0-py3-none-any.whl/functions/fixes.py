# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import sys
import ctypes
import dearpygui.dearpygui as dpg

# Custom Library

# Custom Packages
from AthenaDPGLib.data.dpg_item_names import DpgItemNames

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
def fix_icon_for_taskbar(app_model_id:str):
    # Define application ICON,
    #   makes sure the APPLICATION icon is shown in the taskbar
    #   make sure that dpg.viewport(large_icon=..., small_icon=...) kwargs are both set
    if (sys_platform := sys.platform) == "win32":
        # WINDOWS NEEDS THIS to make this possible
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_model_id)
    else:
        # TODO fix this! (aka, find out how to do this)
        raise NotImplementedError(f"the 'fix_icon_for_taskbar' function doe not work for the os: {sys_platform}")

def fix_grid_layout_equal_row_spacing(table_name:str):
    # Current dpg 1.6.2 doesn't support equal row spacing
    #   This is a fix that solves this 'issue'
    #   By example of the code Illu showed me
    if dpg.does_item_exist(table_name) and dpg.get_item_type(table_name) == DpgItemNames.table.value:
        # Always make sure the table exists and is actually a table
        tbl_height = dpg.get_item_height(table_name)
        for r in (rows := dpg.get_item_children(table_name)[1]):
            dpg.configure_item(r, height=tbl_height / len(rows))
