# --------------------------------------------------------------------------- #
#   Proofscape Utilities                                                      #
#                                                                             #
#   Copyright (c) 2021-2022 Proofscape contributors                           #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
# --------------------------------------------------------------------------- #

import importlib


def from_import(mod_name, attr_name):
    """
    mod_name: (str) the name (possibly dotted) of the module
    attr_name: (str, list) name or names of objects to import from the module

    return: single imported object if a single attr_name was given, or list of
        imported objects if multiple names were given.
    """
    mod = importlib.import_module(mod_name)
    if isinstance(attr_name, str):
        return getattr(mod, attr_name)
    else:
        assert isinstance(attr_name, list)
        return (getattr(mod, name) for name in attr_name)
