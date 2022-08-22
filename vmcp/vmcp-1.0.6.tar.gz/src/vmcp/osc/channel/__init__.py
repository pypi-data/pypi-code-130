#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Open Sound Control (OSC) network protocol channel package."""

from .sender import Sender
from .receiver import Receiver

__all__ = [
  "Sender",
  "Receiver",
  "common"
]
