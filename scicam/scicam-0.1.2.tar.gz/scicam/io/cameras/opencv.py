
import traceback
import time
import os.path
import logging

import numpy as np
import simple_pyspin
from scicam.io.cameras.core import CV2Compatible
from scicam.decorators import timeit
import cv2


logger = logging.getLogger(__name__)


class OpenCVCamera(CV2Compatible):

    def __init__(self, *args, **kwargs):
        self._isgrabbing = False
        self._isopen = False
        super(OpenCVCamera, self).__init__(*args, **kwargs)
    
    @property
    def width(self):
        return int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def model_name(self):
        # TODO
        return "PS Eye"
        # return self.camera.DeviceModelName

    @property
    def serial_number(self):
        # TODO
        # return self.camera.DeviceSerialNumber
        return 0 

    @property
    def friendly_name(self):
        return f"{self.model_name} ({self.serial_number})"

    @property
    def temperature(self):
        return 0

    @property
    def temperature_unit(self):
        raise "C"

    @property
    def framerate(self):
        return float(self.camera.get(cv2.CAP_PROP_FPS))

    @framerate.setter
    def framerate(self, framerate):
        logging.warning("Setting framerate is not recommended in scicam")
        self.camera.set(cv2.CAP_PROP_FPS, framerate)
        self._target_framerate = framerate

    @property
    def exposure(self):
        return self.camera.get(cv2.CAP_PROP_EXPOSURE)

    @exposure.setter
    def exposure(self, exposure):
        logging.warning("Setting exposure time is not recommended in scicam")
        self.camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
        self._target_exposure = exposure

    def is_open(self):
        """
        Return True if camera is opened
        """
        return self._isopen

    def IsGrabbing(self):
        return self._isgrabbing


    def _init_camera(self, idx):
        try:
            self.camera = cv2.VideoCapture(idx)
        
        except Exception as error:
            logger.error(
                "The OpenCV camera cannot be opened."\
                " Please check error trace for more info"
            )
            logger.error(traceback.print_exc())
            raise error         


    @timeit 
    def _next_image_default_timeit(self):
        if self.IsGrabbing():
            with self._acquisition_lock:
                ret, img = self.camera.read()
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = img[:, :, 0]

                if isinstance(img, np.ndarray):
                    code = 0
                else:
                    code = 1

                return code, img


    def _next_image_default(self):
        (code, img), msec = self._next_image_default_timeit()
        logger.debug(f"Read image from {self.model_name} in {msec} ms")
        status = 1 - code
        return status, img

    def save_features(self, path):
        logger.warning(f"{self.__class__}.save_features is not implemented. Ignoring")

    def open(self, maxframes=None, buffersize=5, idx=0):
        """
        Detect a Basler camera using pylon
        Assign it to the camera slot and try to open it
        Try to fetch a frame
        """

        self.maxframes = maxframes
        self._init_camera(idx)
        print("Using device ", self.model_name)

        self.camera.set(cv2.CAP_PROP_FPS, self._target_framerate)
        # self.camera.ExposureAuto = "Off"
        self.camera.set(cv2.CAP_PROP_EXPOSURE, self._target_exposure)
        
        if self._target_width is None:
            self._target_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)


        if self._target_height is None:
            self._target_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self._target_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self._target_height)

        # self.camera.start()
        self._isgrabbing = True

        # Print the model name of the camera.
        logger.info(f"Using device {self.model_name}")
        self._init_read()
        self._isopen = True
    
    def close(self):
        self.stopped = True
        self._isgrabbing = False
        self.camera.release()

