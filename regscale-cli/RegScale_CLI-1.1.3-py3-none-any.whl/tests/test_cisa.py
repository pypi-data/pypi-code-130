#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from app.cisa import update_known_vulnerabilities, update_regscale
from app.logz import create_logger


class Test_Cisa:
    logger = create_logger()

    def test_kev(self):
        data = update_known_vulnerabilities()
        assert data
