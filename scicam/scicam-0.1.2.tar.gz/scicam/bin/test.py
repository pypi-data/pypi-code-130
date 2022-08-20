import argparse
import logging
import multiprocessing
import sys
import time

import joblib

from scicam.io.cameras.__main__ import main as flir_main

# from scicam.cameras import setup_camera as flir_setup
from scicam.io.cameras.__main__ import get_parser as flir_parser

from scicam.io.cameras.basler import main as basler_main

# from scicam.io.cameras.basler import setup_camera as basler_setup
from scicam.io.cameras.basler import get_parser as basler_parser


logger = logging.getLogger(__name__)
LEVELS = {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30}
CAMERAS = {"Flir": flir_main, "Basler": basler_main}


def get_parser(ap=None):

    if ap is None:
        ap = argparse.ArgumentParser(conflict_handler="resolve")

    ap.add_argument(
        "--cameras", nargs="+", required=True, choices=list(CAMERAS.keys())
    )
    ap.add_argument(
        "--verbose", choices=list(LEVELS.keys()), default="WARNING"
    )
    return ap


def setup_logger(level):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)
    logger.addHandler(console)


def main(args=None, ap=None):

    if args is None:
        if ap is None:
            ap = get_parser()
            ap = basler_parser(ap=ap)
            ap = flir_parser(ap=ap)
        args = ap.parse_args()

    level = LEVELS[args.verbose]
    setup_logger(level=level)

    main_funcs = {}

    camera = args.cameras[0]
    logger.info(f"Initializing {camera} camera")
    main_funcs[camera] = CAMERAS[camera]

    main_funcs[camera](ap=ap)
    
    try:
        pass
    except KeyboardInterrupt:
        return

    # joblib.Parallel(n_jobs=2)(joblib.delayed(f)(ap=ap) for f in main_funcs)
    sys.exit(0)


if __name__ == "__main__":
    main()
