import logging
import logging.config
import json
import os.path
import json
import sys
import signal

from scicam.utils import load_config

from scicam.io.cameras.basler.parser import (
    get_parser as camera_parser,
)

from scicam.io.recorders.parser import get_parser as recorder_parser
from scicam.core.monitor import run as run_monitor
from scicam.core.monitor import setup
from scicam.utils import load_config, service_shutdown

LEVELS = {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30}
logger = logging.getLogger(__name__)
recorder_logger = logging.getLogger("scicam.io.record")
recorder_logger.setLevel(logging.DEBUG)


def setup_logger(level):

    logger = logging.getLogger(__name__)
    # logger.setLevel(level)
    recorder_logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)
    logger.addHandler(console)
    recorder_logger.addHandler(console)


def setup_and_run(args):

    monitor = setup(args)
    run_monitor(monitor)


def main(args=None, ap=None):

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    if args is None:
        ap = recorder_parser(ap=ap)
        ap = camera_parser(ap=ap)
        args = ap.parse_args()

    setup_and_run(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
