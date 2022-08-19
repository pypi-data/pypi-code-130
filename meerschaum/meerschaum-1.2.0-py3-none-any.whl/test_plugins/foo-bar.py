#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
This is a test plugin.
"""

required = ['dash-extensions']

from meerschaum.plugins import make_action

@make_action
def test_action(**kw):
    return True, "Yay it works"
