#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from os import path
from typing import Optional


def find_file(name: str, required: bool) -> Optional[str]:
    """
    Search for a file or directory in the script's parent folders.

    Args:
        name: Name of the file or directory to search.
        required: If True, raise an exception if the file is not found.

    Returns:
        File path, if found, None otherwise.

    Raises:
        FileNotFoundError: if the file was not found.
    """
    cur_path = os.getcwd()
    while cur_path:
        bin_path = path.join(cur_path, name)
        if path.exists(bin_path):
            return bin_path
        old_path = cur_path
        cur_path = path.dirname(cur_path)
        if cur_path == old_path:
            break
    if required:
        raise FileNotFoundError(f"Cannot find {name} in parent folders")
    return None
