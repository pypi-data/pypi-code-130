#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``typing`` module of ``backend`` package."""

from typing import NewType
from types import ModuleType

BackendType = NewType("BackendType", ModuleType)
