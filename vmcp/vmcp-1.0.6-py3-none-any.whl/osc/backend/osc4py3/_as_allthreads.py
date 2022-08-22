#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``_as_allthreads`` module of ``osc4py3`` backend package."""

from osc4py3.as_allthreads import (  # noqa: F401
    osc_startup as startup,
    osc_udp_server as server,
    osc_udp_client as client,
    osc_send as as_allthreads,
    osc_process as process,
    osc_terminate as terminate
)
from . import common
# pylint: disable=unused-wildcard-import,wildcard-import
from .common import *  # noqa: F401, F403

send = create_send(as_allthreads)  # noqa: F405

# pylint: disable=duplicate-code
__all__ = [
    "startup",
    "server",
    "client",
    "send",
    "process",
    "terminate"
] + common.__all__
