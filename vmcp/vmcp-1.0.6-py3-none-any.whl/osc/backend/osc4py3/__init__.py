#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``osc4py3`` backend package."""

from ..typing import BackendType
from . import _as_eventloop
from . import _as_comthreads
from . import _as_allthreads

as_eventloop = BackendType(_as_eventloop)
as_comthreads = BackendType(_as_comthreads)
as_allthreads = BackendType(_as_allthreads)

__all__ = [
    "as_eventloop",
    "as_comthreads",
    "as_allthreads"
]
