import argparse
import time
import logging
import traceback
import math
import inspect

import cv2

from scicam.io.cameras.basler import BaslerCamera
from scicam.io.cameras.flir import FlirCamera
from scicam.io.cameras.opencv import OpenCVCamera

logger = logging.getLogger(__name__)
LEVELS = {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30}



def get_parser(ap=None):

    if ap is None:
        ap = argparse.ArgumentParser()

    ap.add_argument(
        "--framerate",
        type=int,
        default=150,
        help="Frames Per Second of the camera",
    )
    ap.add_argument(
        "--exposure-time",
        dest="exposure",
        type=int,
        default=6500,
        help="Exposure time in useconds (10^-6 s)",
    )

    ap.add_argument("--preview", action="store_true", default=False)

    return ap


def setup(camera_name, args=None, idx=0, **kwargs):

    camera_kwargs = {
        "framerate": getattr(
            args,
            f"{camera_name.lower()}_framerate",
            getattr(args, "framerate"),
        ),
        "exposure": getattr(
            args, f"{camera_name.lower()}_exposure", getattr(args, "exposure")
        ),
        "width": args.width,
        "height": args.height,
        "resolution_decrease": args.resolution_decrease,
        "idx": idx,
    }

    print(camera_kwargs)

    camera_kwargs.update(kwargs)
    if camera_name == "Flir":
        camera = FlirCamera(**camera_kwargs)
    elif camera_name == "Basler":
        camera = BaslerCamera(**camera_kwargs)
    elif camera_name == "OpenCVCamera":
        camera = OpenCVCamera(**camera_kwargs)
    else:
        raise Exception("Invalid camera name")

    return camera


def run(camera, queue=None, preview=False):
    try:
        for timestamp, frame in camera:
            if camera.rois:
                frame = frame[0]

            print(
                "Flir camera reads: ",
                timestamp,
                frame.shape,
                frame.dtype,
                camera.computed_framerate,
            )
            if queue is not None:
                queue.put((timestamp, frame))

            if preview:
                cv2.imshow("Flir", frame)
                if cv2.waitKey(1) == ord("q"):
                    break

    except KeyboardInterrupt:
        return


def setup_and_run(args, **kwargs):
    camera = setup(camera_name=args.cameras[0], args=args, **kwargs)
    maxframes = getattr(args, "maxframes", None)
    camera.open(maxframes=maxframes)
    run(camera, preview=args.preview)


def main(args=None, ap=None):
    """
    Initialize a FlirCamera
    """

    if args is None:
        ap = get_parser(ap=ap)
        ap.add_argument(
            "--maxframes",
            default=None,
            help="Number of frames to be acquired",
            type=int,
        )
        ap.add_argument(
            "--verbose", choices=list(LEVELS.keys()), default="WARNING"
        )

        args = ap.parse_args()

    setup_and_run(args)


if __name__ == "__main__":
    main()
