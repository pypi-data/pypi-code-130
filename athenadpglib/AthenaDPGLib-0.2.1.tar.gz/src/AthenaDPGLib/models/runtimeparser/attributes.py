# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import collections.abc
from typing import Any

# Custom Library
from AthenaLib.functions.mappings import skip_keys_in_mapping

# Custom Packages
from AthenaDPGLib.data.dpg_policies import DPG_TABLE_POLICIES
from AthenaDPGLib.data.text import POLICY

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
class Attributes(collections.abc.Mapping):
    """
    Class which holds all the attributes of an item.
    Will fix any attributes that have to be mapped to another non-JSON-Storable data type
    """
    attrib:dict[str:Any]

    def __init__(self, attrib:dict):
        # skip all attributes that start with `_`
        #   This is because these are used within the parser to define special args, child items, etc...
        self.attrib = {k:v for k,v in  attrib.items() if not k.startswith("_")}

        # fix any attributes that have to be mapped to another non-JSON-Storable data type
        self.map_attrib_policy()

    # ------------------------------------------------------------------------------------------------------------------
    # - Mapping abstract methods - (this way we can 'unpack' the Attributes Class)
    # ------------------------------------------------------------------------------------------------------------------
    def __iter__(self):
        return iter(self.attrib.keys()) # thanks for eivl in showing me collections.abc.Mapping

    def __getitem__(self, key):
        return self.attrib[key]

    def __len__(self):
        return len(self.attrib)

    # ------------------------------------------------------------------------------------------------------------------
    # - Fixes to non JSON Storable data types -
    # ------------------------------------------------------------------------------------------------------------------
    def map_attrib_policy(self):
        """
        Checks if the string 'policy' is in the attributes' dictionary.
        When present, it will map the string to the correct DPG policy.
        """
        if POLICY in self.attrib:
            self.attrib[POLICY] = DPG_TABLE_POLICIES[self.attrib[POLICY]]