import argparse
import sys
import time
import os.path
import signal

import numpy as np
import yaml
from datetime import datetime
import logging
import logging.config
from scicam.constants import LOGGING_CONFIG
from EasyROI import EasyROI

from scicam.io.cameras.__main__ import get_parser as flir_parser
from scicam.io.cameras.basler.parser import get_parser as basler_parser
from scicam.io.cameras import CAMERAS
from scicam.io.recorders.parser import get_parser as recorder_parser
from scicam.web_utils.sensor import setup as setup_sensor
from scicam.core.manager import Manager
from scicam.exceptions import ServiceExit
from scicam.utils import load_config, service_shutdown

logger = logging.getLogger(__name__)

config = load_config()

# this start time will be shared by all cameras running in parallel and will give name to the experiment
start_time = time.time()
time_iso_8601=datetime.fromtimestamp(start_time).strftime("%Y-%m-%d_%H-%M-%S")
root_output = os.path.join(config["videos"]["folder"], time_iso_8601)


with open(LOGGING_CONFIG, 'r') as filehandle:
    logging_config = yaml.load(filehandle, yaml.SafeLoader)
    logging.config.dictConfig(logging_config)

LOGFILE = os.path.join(config["logs"]["folder"], f"{time_iso_8601}.log")
file_handler = logging.FileHandler(LOGFILE, mode='w')

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

def get_parser(ap=None):

    if ap is None:
        ap = argparse.ArgumentParser(conflict_handler="resolve")

    ap.add_argument(
        "--cameras",
        nargs="+",
        required=True,
        choices=CAMERAS,
        default=None,
    )
    ap.add_argument(
        "--flir-exposure",
        dest="flir_exposure",
        type=int,
        default=9900,
        help="Exposure time in microseconds of the Flir camera",
    )
    ap.add_argument(
        "--basler-exposure",
        dest="basler_exposure",
        type=int,
        default=25000,
        help="Exposure time in microseconds of the Basler camera",
    )
    ap.add_argument(
        "--flir-framerate",
        type=int,
        default=100,
        help="Frames Per Second of the Flir camera",
    )
    ap.add_argument(
        "--basler-framerate",
        type=int,
        default=30,
        help="Frames Per Second of the Basler camera",
    )
    ap.add_argument(
        "--sensor",
        type=int,
        default=9000,
        help="Port of environmental sensor",
    )
    ap.add_argument(
        "--select-rois",
        default=False,
        action="store_true",
        dest="select_rois",
        help="""
        Whether a region of interest (ROI)
        of the input should be cropped or not.
        In that case, a pop up will show for the user to select it
        """,
    )
    ap.add_argument(
        "--rois",
        default=None,
        type=str
    )
    return ap


def get_queue(process, queues):
    if process in queues and not queues[process].empty():
        timestamp, frame = queues[process].get()
        return timestamp, frame
    else:
        return (None, np.uint8())


def setup_and_run(args):
    sensor = setup_sensor(args.sensor)
    managers = {}
    
    if args.select_rois:
        roi_helper = EasyROI(verbose=True)
    else:
        roi_helper = None


    monitors=[]

    for i, camera_name in enumerate(args.cameras):

        if camera_name == "FlirCamera":
            output = os.path.join(root_output, "lowres")
        else:
            output = root_output

        manager = Manager(
            idx=i,
            chunk_duration=args.chunk_duration,
            camera_name=camera_name, output=output, format=args.format,
            sensor=sensor,  select_rois=args.select_rois, roi_helper=roi_helper, rois=args.rois
        )
        managers[camera_name] = manager
        monitors.append(manager.init(start_time=start_time))

    for monitor in monitors:
        monitor.start()

    for monitor in monitors:
        monitor.join()


    try:
        logger.debug(f"Starting {len(managers)} processes")
        run_processes(managers)
    except KeyboardInterrupt:
        return


def run_processes(managers):

    if "FlirCamera" in managers:
        managers["FlirCamera"].start()
    # give time for the Flir process to start
    # before Basler does.
    # Otherwise Basler starts before and crashes when Flir does

    if "FlirCamera" in managers and "BaslerCamera" in managers:
        time.sleep(5)
    if "BaslerCamera" in managers:
        managers["BaslerCamera"].start()
    time.sleep(1)

    try:
        for p in managers.values():
            p.join()
    except ServiceExit:
        print(
            """
          Service Exit captured.
          Please wait until processes finish
        """
        )
        for manager in managers.values():
            manager.stop_queue.put("STOP")

        for m in managers.values():
            m.join()
        sys.exit(0)

    if all([not p.is_alive() for p in managers.values()]):
        sys.exit(0)


def main(args=None, ap=None):

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    if args is None:
        if ap is None:
            ap = get_parser()
            ap = basler_parser(ap=ap)
            ap = flir_parser(ap=ap)
            ap = recorder_parser(ap)
        args = ap.parse_args()

    setup_and_run(args)


if __name__ == "__main__":
    main()
