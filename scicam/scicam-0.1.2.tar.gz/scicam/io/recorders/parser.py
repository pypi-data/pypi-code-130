import argparse
import datetime
import math
from imgstore.stores.utils.formats import get_formats
FMT_TO_CODEC=get_formats(video=True)

ENCODER_FORMAT_CPU="divx/avi"
ENCODER_FORMAT_GPU="h264_nvenc/mp4"

from scicam.utils import load_config
from scicam.constants import CONFIG_FILE

from .record import RECORDERS


def select_encoder():

    config = load_config()

    if config["cuda"]:
        return ENCODER_FORMAT_GPU
    else:
        return ENCODER_FORMAT_CPU

def get_parser(ap=None):

    if ap is None:
        ap = argparse.ArgumentParser(conflict_handler="resolve")

    ap.add_argument(
        "--config",
        help="Config file in json format",
        default=CONFIG_FILE,
    )
    ap.add_argument(
        "--output",
        default=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        help="Path to output video (directory for ImgStore). It will be placed in the video folder as stated in the config file. See --config",
    )
    ap.add_argument(
        "--fps",
        type=int,
        help="Frames Per Second of the video",
        required=False,
    )
    ap.add_argument(
        "--chunk-duration",
        dest="chunk_duration",
        type=int,
        help="Seconds per chunk",
        required=False,
        default=300,
    )
    ap.add_argument("--sensor", type=str, default=None)
    ap.add_argument("--duration", type=int, default=math.inf, help="Recording duration in seconds")
    ap.add_argument("--format", type=str, default=select_encoder())
    ap.add_argument("--crf", type=int)
    ap.add_argument("--buffer-size", dest="buffer_size", type=int, default=500)
    ap.add_argument(
        "--recorder",
        choices=list(RECORDERS.keys()),
        default="ImgStoreRecorder",
    )
    return ap
