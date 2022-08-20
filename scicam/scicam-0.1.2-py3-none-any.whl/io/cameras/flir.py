
import traceback
import time
import os.path
import logging
import random
import numpy as np
import simple_pyspin
from scicam.io.cameras.core import CV2Compatible
from scicam.decorators import timeit
from scicam.io.cameras.utils import validate_img, ensure_img 

logger = logging.getLogger(__name__)

class FlirCamera(CV2Compatible):

    AcquisitionFrameRateMax = 150
    
    """
    Drive a Flir camera using simple_pyspin
    """

    def __init__(self, *args, **kwargs):
        self._isgrabbing = False
        self._isopen = False
        super(FlirCamera, self).__init__(*args, **kwargs)


    @property
    def width(self):
        return self.camera.Width

    @property
    def height(self):
        return self.camera.Height

    @property
    def model_name(self):
        return self.camera.DeviceModelName

    @property
    def serial_number(self):
        return self.camera.DeviceSerialNumber

    @property
    def friendly_name(self):
        return f"{self.camera.DeviceModelName} ({self.camera.DeviceSerialNumber})"

    @property
    def temperature(self):
        return self.camera.DeviceTemperature

    @property
    def temperature_unit(self):
        raise "C"

    @property
    def framerate(self):
        return float(self.camera.AcquisitionFrameRate)

    @framerate.setter
    def framerate(self, framerate):
        logging.warning("Setting framerate is not recommended in scicam")
        self.camera.AcquisitionFrameRate = framerate
        self._target_framerate = framerate

    @property
    def exposure(self):
        return float(self.camera.ExposureTime)

    @exposure.setter
    def exposure(self, exposure):
        logging.warning("Setting exposure time is not recommended in scicam")
        self.camera.ExposureTime = exposure
        self._target_exposure = exposure

    def is_open(self):
        """
        Return True if camera is opened
        """
        return self._isopen

    def IsGrabbing(self):
        return self._isgrabbing

    def _compute_final_framerate_for_camera(self):
        """
        Add to the target framerate a little bit more,
        so the camera makes a bit more effort and actually hits the target
        """
        framerate = self._target_framerate + self._framerate_offset
        max_framerate = self.AcquisitionFrameRateMax
        if framerate >= max_framerate:
            logger.warning(
                f"Passed framerate is greater or equal than max ({max_framerate})"
            )
            final_framerate = max_framerate
        else:
            final_framerate = framerate
        return final_framerate


    def _init_camera(self, idx):
        try:
            self.camera = simple_pyspin.Camera(index=idx)
            self.camera.__enter__()
        
        except Exception as error:
            logger.error(
                "The Flir camera cannot be opened."\
                " Please check error trace for more info"
            )
            logger.error(traceback.print_exc())
            raise error         
            

    @timeit 
    def _next_image_default_timeit(self):
        if self.IsGrabbing():
            with self._acquisition_lock:
                img = self.camera.get_array()

                if isinstance(img, np.ndarray):
                    code = 0
                else:
                    code = 1

            # p = random.random()
            # if p > 0.9999:
            #     img = None

            if not validate_img(img):
                return ensure_img(self, 1)

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
        self._idx=idx
        print("Using device ", self.model_name)
        self.camera.AcquisitionFrameRateAuto = "Off"
        self.camera.AcquisitionFrameRateEnabled = True
        self.camera.AcquisitionFrameRate = self._compute_final_framerate_for_camera()
        
        self.camera.ExposureAuto = "Off"
        self.camera.ExposureTime = self._target_exposure
        
        if self._target_width is None:
            self._target_width = self.camera.SensorWidth


        if self._target_height is None:
            self._target_height = self.camera.SensorHeight

        self.camera.Width = self._target_width
        self.camera.Height = self._target_height

        self.camera.ReverseX = False
        self.camera.ReverseY = True

        if self._document_path is not None:
            self.save_features(
                os.path.join(
                    self._document_path,
                    self.model_name + ".pfs"
                )
            )

        self.camera.start()
        self._isgrabbing = True

        # Print the model name of the camera.
        logger.info(f"Using device {self.model_name}")
        self._init_read()
        self._isopen = True
    

    def close(self):
        self.stopped = True
        self._isgrabbing = False
        self.camera.stop()
        exc = BaseException("0")
        self.camera.__exit__(type(exc), exc, traceback=exc.__traceback__)
