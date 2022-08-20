# Standard library
import logging
import warnings
import time
import traceback
import os.path
import random

# Optional modules
from pypylon import pylon

# Local library
from scicam.io.cameras.core import CV2Compatible
from scicam.io.cameras.utils import ensure_img, validate_img
from scicam.decorators import timeit

logger = logging.getLogger("scicam.io.camera")
LEVELS = {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30}

class BaslerCamera(CV2Compatible):

    """
    Drive a Basler camera using pypylon.
    """

    def __init__(self, *args, **kwargs):
        super(BaslerCamera, self).__init__(*args, **kwargs)

    @property
    def width(self):
        return self.camera.Width.GetValue()

    @property
    def height(self):
        return self.camera.Height.GetValue()

    @property
    def model_name(self):
        return self.camera.GetDeviceInfo().GetModelName()
    
    @property
    def serial_number(self):
        return self.camera.GetDeviceInfo().GetSerialNumber()


    @property
    def friendly_name(self):
        return self.camera.GetDeviceInfo().GetFriendlyName()

    @property
    def temperature(self):
        return round(self.camera.DeviceTemperature.GetValue(), 2)

    @property
    def temperature_unit(self):
        return self.camera.DeviceTemperature.GetUnit()


    @property
    def framerate(self):
        return float(self.camera.AcquisitionFrameRate.GetValue())

    @framerate.setter
    def framerate(self, framerate):
        logging.warning("Setting framerate is not recommended in scicam")
        self.camera.AcquisitionFrameRate.SetValue(framerate)
        self._target_framerate = framerate

    @property
    def exposure(self):
        return float(self.camera.ExposureTime.GetValue())

    @exposure.setter
    def exposure(self, exposure):
        logging.warning("Setting exposure time is not recommended in scicam")
        self.camera.ExposureTime.SetValue(exposure)
        self._target_exposure = exposure

    def is_open(self):
        """
        Return True if camera is opened
        """
        return self.camera.IsOpen()

    @timeit 
    def _next_image_default_timeit(self):
        if self.camera.IsGrabbing():
            with self._acquisition_lock:
                while True:
                    try:
                        grab = self.camera.RetrieveResult(
                            self._timeout, pylon.TimeoutHandling_ThrowException
                        )
                        break
                    except:
                        logger.warning("Calling _next_image_default_timeit again")
                        pass

                if grab.GrabSucceeded():
                    img = grab.GetArray()
                    grab.Release()
                    code = 0
                else:
                    img = None
                    code = 1

            # p = random.random()
            # if p > 0.999:
            #     img = None

            if not validate_img(img):
                code, img=ensure_img(self)

            return code, img
        else:
            return 1, None

    def _next_image_default(self):
        (code, img), msec = self._next_image_default_timeit()
        logger.debug(f"Read image from {self.model_name} in {msec} ms")
        status = 1 - code
        return status, img

    def _init_camera(self):
        
        # NOTE
        # When selecting a particular camera
        # you may want to use self.idx

        try:
            tl_factory = pylon.TlFactory.GetInstance()
            camera_device = tl_factory.CreateFirstDevice()
            self.camera = pylon.InstantCamera(
                camera_device
            )
        except Exception as error:
            logger.error(
                "The Basler camera cannot be opened."\
                " Please check error trace for more info"
            )
            logger.error(traceback.print_exc())
            raise error

    def _init_multi_camera(self, idx=0):
        
        # NOTE
        # When selecting a particular camera
        # you may want to use self.idx

        try:
            tl_factory = pylon.TlFactory.GetInstance()
            devices = tl_factory.EnumerateDevices()
            self.camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[idx]))
            self._idx = idx
            return 0

        except Exception as error:
            logger.error(
                "The Basler camera cannot be opened."\
                " Please check error trace for more info"
            )
            logger.error(traceback.print_exc())
            raise error
    

    def _compute_final_framerate_for_camera(self):
        """
        Add to the target framerate a little bit more,
        so the camera makes a bit more effort and actually hits the target
        """
        framerate = self._target_framerate + self._framerate_offset
        max_framerate = self.camera.AcquisitionFrameRate.GetMax()
        if framerate >= max_framerate:
            logger.warning(
                f"Passed framerate is greater or equal than max ({max_framerate})"
            )
            final_framerate = max_framerate
        else:
            final_framerate = framerate
        return final_framerate

    def save_features(self, pfs_file):
        assert self.is_open()
        return pylon.FeaturePersistence.Save(pfs_file, self.camera.GetNodeMap())


    def open(self, maxframes=None, buffersize=5, idx=0):
        """
        Detect a Basler camera using pylon
        Assign it to the camera slot and try to open it
        Try to fetch a frame
        """
        self._init_multi_camera(idx=idx)
        self.camera.Open()
        print("Using device ", self.model_name)
        self.camera.AcquisitionFrameRateEnable.SetValue(True)

        final_framerate=self._compute_final_framerate_for_camera()
        logger.debug(f"{self} setting framerate to {final_framerate}")
        self.camera.AcquisitionFrameRate.SetValue(
            final_framerate
        )
        logger.debug(f"{self} setting exposure to {self._target_exposure}")
        self.camera.ExposureTime.SetValue(self._target_exposure)

        if self._target_width is None:
            self._target_width = self.camera.Width.GetMax()

        if self._target_height is None:
            self._target_height = self.camera.Height.GetMax()

        self.camera.Width.SetValue(self._target_width)
        self.camera.Height.SetValue(self._target_height)
        self.camera.ReverseX.SetValue(True)
        self.camera.ReverseY.SetValue(True)
        self.camera.MaxNumBuffer = buffersize
        
        if self._document_path is not None:
            self.save_features(
                os.path.join(
                    self._document_path,
                    self.model_name + ".pfs"
                )
            )

        if maxframes is not None:
            self.camera.StartGrabbingMax(maxframes)
            # if we want to limit the number of frames
        else:
            self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

        # Print the model name of the camera.
        logger.info(f"Using device {self.model_name}")
        self._init_read()

    def close(self):
        while self._acquisition_lock.locked():
            time.sleep(.1)

        with self._acquisition_lock:
            self.camera.Close()
