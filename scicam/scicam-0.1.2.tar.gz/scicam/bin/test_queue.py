import argparse
import logging
import multiprocessing
import sys
import time

import joblib
import numpy as np

from scicam.io.cameras.__main__ import setup_and_run as flir_run

# from scicam.cameras import setup_camera as flir_setup
from scicam.io.cameras.__main__ import get_parser as flir_parser

from scicam.io.cameras.basler import setup_and_run as basler_run

# from scicam.io.cameras.basler import setup_camera as basler_setup
from scicam.io.cameras.basler import get_parser as basler_parser


logger = logging.getLogger(__name__)
LEVELS = {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30}
CAMERAS = {"Flir": flir_run, "Basler": basler_run}


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


def get_queue(process, queues):
    if process in queues and not queues[process].empty():
        timestamp, frame = queues[process].get()
        return timestamp, frame
    else:
        return (None, np.uint8())


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
    for camera in args.cameras:
        logger.info(f"Initializing {camera} camera")
        main_funcs[camera] = CAMERAS[camera]

    processes = {}
    queues = {}
    for name, main_f in main_funcs.items():
        queue = multiprocessing.Queue(maxsize=1)
        p = multiprocessing.Process(
            target=main_f,
            name=name,
            kwargs={"args": args, "queue": queue},
            daemon=True,
        )
        processes[name] = p
        queues[name] = queue

    if "Flir" in processes:
        processes["Flir"].start()
    # give time for the Flir process to start
    # before Basler does.
    # Otherwise Basler starts before and crashes when Flir does

    if "Flir" in processes and "Basler" in processes:
        time.sleep(5)
    if "Basler" in processes:
        processes["Basler"].start()

    data = {camera: (None, np.uint8()) for camera in args.cameras}

    try:
        while True:
            for c in args.cameras:
                t, img = get_queue(c, queues)
                if t is not None:
                    data[c] = (t, img)
                    print(c, "camera sends:", t, img.shape, img.dtype)

            if all([not p.is_alive() for p in processes.values()]):
                return

    except KeyboardInterrupt:
        return

    sys.exit(0)


if __name__ == "__main__":
    main()
