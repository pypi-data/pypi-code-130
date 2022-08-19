# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 14:22:06 2022

@author: elog-admin
"""

import logging
from pathlib import Path

#
# LOGGING PARAMETERS
#
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warn': logging.WARNING,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
#
# ELOG PARAMETERS
#
ELOG_USER = 'log-robot'
ELOG_PASSWORD = 'IchBinRoboter'
ELOG_HOSTNAME = 'https://10.166.16.24'
ELOG_PORT = 8080
#
# EXTERNAL TOOLS
#
NOTEPAD_BEST = Path("C:\\Program Files\\Notepad++\\notepad++.exe")
ROBOCOPY_EXE = Path("C:\\Windows\\System32\\Robocopy.exe")
#
# WATCHDOGS
#
AUTOLOGBOOK_WATCHDOG_MAX_ATTEMPTS = 5
AUTOLOGBOOK_WATCHDOG_WAIT_MIN = 1
AUTOLOGBOOK_WATCHDOG_WAIT_MAX = 5
AUTOLOGBOOK_WATCHDOG_WAIT_INCREMENT = 1
AUTOLOGBOOK_WATCHDOG_MIN_DELAY = 45
#
# MIRRORING WATCHDOG
#
AUTOLOGBOOK_MIRRORING_MAX_ATTEMPTS = 2
AUTOLOGBOOK_MIRRORING_WAIT = 0.5
#
# AUTOPROTOCOL
#
IMAGE_SERVER_BASE_PATH = Path('R:\\A226\\Results')
IMAGE_SERVER_ROOT_URL = 'https://10.166.16.24/micro'
IMAGE_SAMPLE_THUMB_MAX_WIDTH = 400
#
# QUATTRO
#
IMAGE_NAVIGATION_MAX_WIDTH = 500
QUATTRO_LOGBOOK = 'Quattro-Analysis'
#
# VERSA
#
VERSA_LOGBOOK = 'Versa-Analysis'
#