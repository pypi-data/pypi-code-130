#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``osc4py3.as_allthreads`` backend test."""

from pytest import fixture
from vmcp.osc.backend.osc4py3 import as_eventloop
# pylint: disable=wildcard-import,unused-wildcard-import
from .common import *  # noqa: F401, F403


@fixture
def backend():
    """Return the backend module.

    Returns:
        BackendType:
            Module.

    """
    return as_eventloop
