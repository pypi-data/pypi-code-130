__author__ = "antonio"

import time
import datetime
import threading
import logging
from abc import abstractmethod
from scicam.io.cameras.plugins import ROISPlugin, CameraUtils, SquareCamera
from scicam.class_utils.time import TimeUtils
import cv2

class AbstractCamera:

    @property
    @abstractmethod
    def running_for_seconds(self):
        raise NotImplementedError


    @abstractmethod
    def is_open(self):
        raise NotImplementedError

    @abstractmethod
    def save_features(self, path):
        raise NotImplementedError

    @abstractmethod
    def open(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def restart(self):
        raise NotImplementedError

    @abstractmethod
    def is_last_frame(self):
        raise NotImplementedError

    @abstractmethod
    def _next_image_square(self):
        raise NotImplementedError

    @abstractmethod
    def _next_image_default(self):
        raise NotImplementedError

    @abstractmethod
    def _next_image_rois(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def width(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def height(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def framerate(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def exposure(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def temperature(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def temperature_unit(self):
        raise NotImplementedError
        
    @property
    @abstractmethod
    def model_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def serial_number(self):
        raise NotImplementedError


    @property
    @abstractmethod
    def friendly_name(self):
        raise NotImplementedError


class BaseCamera(ROISPlugin, SquareCamera, AbstractCamera, TimeUtils, CameraUtils):

    def __init__(
        self,
        start_time,
        width=None,
        height=None,
        framerate=30,
        framerate_offset=0,
        info_freq=60,
        exposure=15000,
        iso=0,
        drop_each=1,
        timeout=30000,
        duration=None,
        resolution_decrease=1.0,
        rois=None,
        document_path=None,
        idx=0,
        roi_helper=None,
    ):
        """
        Abstract camera class template
        Inspired by the Ethoscope project.
        """


        self.camera=None
        self._target_width = width
        self._target_height = height
        self._target_exposure = exposure
        self._target_framerate = framerate
        self._framerate_offset = framerate_offset
        self._target_iso = iso
        self._drop_each = drop_each
        self._timeout = timeout
        self._duration = duration
        self._rois = rois
        self._time_s = None
        self._last_ticks = {}
        self._idx = None
        self._acquisition_lock = threading.Lock()

        self._info_freq = info_freq

        self._last_offset = 0
        self._frames_this_second = 0
        self._frame_idx = 0
        self._document_path = document_path
        self.idx = idx
        self.start_time = start_time
        self.isColor = False

        if resolution_decrease != 1.0:
            logging.warning("Resolution decrease is not implemented. Ignoring")
        self.open(idx=idx)
        start_time_iso=datetime.datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{self.friendly_name} initialized with timestamp {self.start_time} ({start_time_iso})")

        super().__init__(roi_helper=roi_helper)


    @property
    def resolution(self):
        r"""
        Convenience function to return resolution of camera.
        Resolution = (number_horizontal_pixels, number_vertical_pixels)
        """
        return (
            self.width,
            self.height,
        )
        
    @property
    def shape(self):
        r"""
        Convenience function to return shape of camera
        Shape = (number_vertical_pixels, number_horizontal_pixels, number_channels)
        """
        
        if self.isColor:
            return (
                self.height,
                self.width,
                3
            )
        else:
            return (
                self.height,
                self.width
            )

    @property
    def computed_framerate(self):
        return self._frames_this_second

    @property
    def duration(self):
        return self._duration

    def is_closed(self):
        return not self.is_open()

    def is_last_frame(self):
        if self._duration is None:
            return False
        return self._duration < self.running_for_seconds
 

    def _next_image(self):

        if self._rois is None:
            status, img = self._next_image_square()
            # img = cv2.putText(img, str(self.time_stamp()), org=(100, 100), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=5, color=0)
        else:
            status, img = self._next_image_rois()
            # img = [cv2.putText(img[0], str(self.time_stamp()), org=(100, 100), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=5, color=0)]

        return status, img


    def _init_read(self):
        """
        Try reading a frame and check its resolution
        """
        status, img = self._next_image_square()

        if status and img is not None:

            logging.info(f"P{self} opened successfully")
            logging.info(
                "Resolution of incoming frames: %dx%d",
                img.shape[1],
                img.shape[0],
            )
        else:
            raise Exception("The initial grab did not work")


    def time_stamp(self):
        if self.start_time is None:
            return 0
        else:
            now = time.time()
            self._time_s = now - self.start_time
            # print(f"{self}: {self._time_s}")

        return self._time_s

    def _next_time_image(self):
        status, image = self._next_image()
        timestamp = self.time_stamp()

        if image is not None:
            self._frame_idx += 1

        return timestamp, image

    
    def _get_info(self):
        if self._info_freq is not None and self.tick(self._info_freq):
            info = {
                "temperature": self.temperature
            }
        else:
            info = None

        return info


    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):  
        self.close()
   
    def __iter__(self):
        """
        Iterate thought consecutive frames of this camera.

        Returns:
        
            * t_ms (int): time of the frame in ms
            * out (np.ndarray): frame
        """
        
        try:
            while self.is_open():
                time_s, out = self._next_time_image()

                if out is None:
                    break

                t_ms = int(1000 * time_s)

                info = self._get_info()
                yield t_ms, out, info

        except KeyboardInterrupt:
            self.close()

class CV2Compatible(BaseCamera):
    """
    Make the camera behave like a cv2.VideoCapture object
    for 'duck-typing' compatibility
    """

    def read(self):
        return self._next_image()

    def release(self):
        return self.close()

    def set(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError
