#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Open Sound Control (OSC) network protocol package."""

from .osc import OSC

__all__ = [
  "OSC",
  "channel",
  "typing"
]
