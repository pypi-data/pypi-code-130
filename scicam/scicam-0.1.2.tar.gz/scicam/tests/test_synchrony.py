import unittest
import time

import imgstore 
import math
import numpy as np
import cv2

imgshape = (500, 500)
secs = 10


format="mjpeg/avi"

def interact_with_store(store, timestamp, tick, tock, i):
    if tick > tock:
        tock = tick
        frame = np.zeros(imgshape, np.uint8)
        frame = cv2.putText(frame, str(timestamp), org=(100, 100), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=255)
        store.add_image(frame, i, timestamp)
        i+=1
    return i, tock

class TestSynchrony(unittest.TestCase):

    

    def test_synchrony(self):
        
        quick_tock = 0
        highres_tock = 0
        highres_store = imgstore.new_for_format(
            mode="w",
            fmt=format,
            framerate=40,
            basedir="scicam/tests/static_data/store_1",
            imgshape=imgshape,
            chunksize=40 * secs,
            imgdtype=np.uint8,
            extra_cameras=["lowres/metadata.yaml"]
        )



        quick_store = imgstore.new_for_format(
            mode="w",
            fmt=format,
            framerate=100,
            basedir="scicam/tests/static_data/store_1/lowres",
            imgshape=imgshape,
            chunksize=100 * secs,
            imgdtype=np.uint8,
        )

        start_time = time.time() * 1000
        i=0
        j=0

        while True:
            now = time.time() * 1000
            timestamp = now - start_time

            if (timestamp) > 100000:
                break

            highres_tick = math.floor(timestamp / 25)
            quick_tick = math.floor(timestamp / 10)
            i, highres_tock = interact_with_store(highres_store, timestamp, highres_tick, highres_tock, i)
            j, quick_tock = interact_with_store(quick_store, timestamp, quick_tick, quick_tock, j)


        with open("scicam/tests/static_data/store_1/metadata.yaml", "w") as filehandle:
            filehandle.write(
                'extra_cameras: ["lowres/metadata.yaml"]\n'
            )

if __name__ == "__main__":
    unittest.main()