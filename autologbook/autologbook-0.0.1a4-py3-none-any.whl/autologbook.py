# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 11:01:34 2022

@author: elog-admin
"""

import argparse
import ctypes
import logging
import sys
from pathlib import Path

from autologbook import autocli, autogui, autotools

log = logging.getLogger()
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warn': logging.WARNING,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

# use this to catch all exceptions in the GUI
sys.excepthook = autotools.my_excepthook


def main_parser():
    """
    Define the main argument parser.

    Returns
    -------
    parser : ArgumentParser
        The main parser.

    """
    parser = argparse.ArgumentParser(description='''
                                     GUI of the automatic
                                     logbook generation tool for microscopy
                                     ''')
    parser.add_argument('-c', '--conf-file', type=Path, dest='conffile',
                        default=(Path.cwd() / Path('autolog-conf.ini')),
                        help='Specify a configuration file to be loaded.')
    parser.add_argument('-l', '--log', dest='loglevel',
                        choices=('debug', 'info', 'warning',
                                 'error', 'critical'),
                        default='info',
                        help='''
                        The verbosity of the logging messages.
                        ''')
    parser.add_argument('-m', '--mirroring-engine', type=str, dest='engine',
                        choices=('watchdog', 'robocopy'), default='watchdog',
                        help='''
                        Set the mirroring engine either to watchdog
                        (faster and rather stable) or robocopy
                        (slower and very stable)
                        ''')
    parser.add_argument('-e', '--exp-file', type=Path, dest='expfile',
                        help='Specify an experiment file to be loaded')
    parser.add_argument('-x', '--auto-exec', dest='autoexec', action='store_true',
                        help='When used in conjunction with -e, if the start watchdog is '
                        'enabled, the wathdog will be started right away')
    parser.add_argument('-t', '--cli', dest='cli', action='store_true',
                        help='When set, a simplified command line interface will '
                        'be started. It implies the -x option and it requires '
                        'an experiment file to be specified with -e.\n'
                        'A valid combination is -txe <experiment_file>')

    return parser


def main(cli_args, prog):
    """
    Define main function to start the event loop.

    Returns
    -------
    None.

    """
    # get the cli args from the parser
    parser = main_parser()
    if prog:
        parser.prog = prog

    args = parser.parse_args(cli_args)

    # to set the icon on the window task bar
    myappid = u'ecjrc.autologook.gui.v1.0.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    if args.cli:
        autocli.main_cli(args)
    else:
        autogui.main_gui(args)
