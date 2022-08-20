import multiprocessing
import time

import numpy as np
from .parser import get_parser
from .record import RECORDERS


def main(args=None):

    output = "trash.avi"

    if args is None:
        ap = get_parser()
        args = ap.parse_args()

    data_queue = multiprocessing.Queue(maxsize=0)
    stop_queue = multiprocessing.Queue(maxsize=1)
    for i in range(10):
        data_queue.put(
            (time.time(), np.uint8(np.random.randint(0, 255, (100, 100))))
        )

    recorder = setup(
        args,
        recorder_name="ImgStoreRecorder",
        source=data_queue,
        stop_queue=stop_queue,
        roi=(0, 0, 100, 100),
        resolution=(100, 100),
        framerate=30,
    )
    recorder.open(path=output, format=args.format)
    recorder.start()
    time.sleep(1)
    print("Started")
    while not data_queue.empty():
        print(data_queue.qsize())
        if (time.time() - recorder._start_time) > 3:
            print(data_queue.get())

    recorder.close()
    print("Done")
    print(data_queue.qsize())
    print(stop_queue.qsize())
    # recorder.join()
    # recorder.terminate()
    import sys

    sys.exit(0)


if __name__ == "__main__":
    main()
