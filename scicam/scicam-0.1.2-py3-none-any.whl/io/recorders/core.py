import sys
import queue
import logging
import math
import multiprocessing
import threading
import traceback
import collections
from abc import abstractmethod

from scicam.class_utils.time import TimeUtils
from scicam.exceptions import ServiceExit
from scicam.decorators import timeit


logger = logging.getLogger(__name__)
run_logger = logging.getLogger(f"{__name__}.run")

# class AbstractRecorder(threading.Thread):
class AbstractRecorder(multiprocessing.Process):
    """
    Take an iterable source object which returns (timestamp, frame)
    in every iteration and save to a path determined in the open() method
    """

    def __init__(
        self,
        path,
        data_queue,
        stop_queue,
        idx=0,
        framerate=None,
        resolution=None,
        duration=math.inf,
        maxframes=math.inf,
        preview=False,
        sensor=None,
        roi=None,
        isColor=False,
        metadata = None,
    ):
        """
        Initialize a recorder with framerate equal to FPS of source
        or alternatively provide a custom framerate
        """
        self.idx = idx
        self._async_writer = None
        self._path = path
        self._first_img = None


        self._framerate = framerate
        self._duration = duration

        assert resolution is not None
        self._resolution = resolution

        if maxframes == 0:
            maxframes = math.inf
        self._maxframes = math.inf
        self._sensor = sensor
        self._time_s = 0


        self._preview = preview
        self._roi = roi
        
        self._data_queue = data_queue
        self._stop_queue = stop_queue

        self.start_time = None
        self._last_update = 0

        self.isColor = isColor

        if isColor:
            raise Exception("Color images not supported")

        if metadata is None:
            metadata = {}
        self.metadata = metadata
        
        self._camera_info = {} 


        super().__init__()
        self.daemon = True

        # TODO
        # Comment this line when using multiprocessing.Process
        # self.exitcode = 0

    @abstractmethod
    def _process_data(self):
        raise NotImplementedError

    @abstractmethod
    def write(self, frame, framecount, timestamp):
        raise NotImplementedError

    @abstractmethod
    def save_extra_data(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def open(self, path):
        raise NotImplementedError

    @abstractmethod
    def report_cache_usage(self):
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError


    @property
    @abstractmethod
    def running_for_seconds(self):
        raise NotImplementedError


    @property
    def resolution(self):
        return self._resolution

    @property
    def sensor(self):
        return self._sensor


    @property
    def all_queues_have_been_emptied(self):
        return self._data_queue.qsize() == self._stop_queue.qsize() == 0

    @property
    def framerate(self):
        return self._framerate

    @property
    def imgshape(self):
        return self.resolution[::-1]


    @property
    def name(self):
        return "Recorder"


    @property
    def max_frames_reached(self):
        return self.n_saved_frames >= self._maxframes


    @property
    def duration_reached(self):
        if self._duration is None:
            duration_reached = False
        else:
            duration_reached = self.running_for_seconds >= self._duration
        
        return duration_reached

    def should_stop(self):

        try:
            msg = self._stop_queue.get(False)
        except queue.Empty:
            msg = None

        result = (
            self.duration_reached
            or self.max_frames_reached
            or msg == "STOP"
        )

        return result

class BaseRecorder(TimeUtils, AbstractRecorder):
    def __init__(self, *args, **kwargs):
        super(BaseRecorder, self).__init__(*args, **kwargs)
        self._last_ticks = {}
        self._read_latency = collections.deque([0], int(self._framerate*10))
        self._write_latency = collections.deque([0], int(self._framerate*10))
        self._loop_latency = collections.deque([0], int(self._framerate*10))
        self._file_size = collections.deque([0], int(self._framerate*10))


    @timeit
    def _read_data_queue(self):
        try:
            (timestamp, frame_idx, info), img = self._data_queue.get(block=True, timeout=1)
        except queue.Empty:
            logger.warning("Empty data_queue")
            img = None

        if img is None:
            data = None
        else:
            data = (timestamp, frame_idx, img, info)
        
        return data

    @timeit
    def _handle_data_queue(self):
        try:
            data, read_msec = self._read_data_queue()
            self._read_latency.append(read_msec)
        except ServiceExit:
            logger.info("Service Exit")
            return 1, None
        except Exception as error:
            logger.error(error)
            logger.error(traceback.print_exc())
            return 1, None
        else:
            if data is None:
                logger.warning("None received")
                return 0, None
            else:
                self._process_data(data)
                return 0, data

    def _handle_stop_queue(self):
        if self._stop_queue.empty():
            msg = None
        else:
            msg = self._stop_queue.get()
        if msg == "STOP":
            self.close()

    @timeit
    def _run_data(self):
        # runs until a STOP message is detected in the stop_queue
        run_logger.debug("_handle_data_queue")
        (code, data), loop_msec = self._handle_data_queue()
        self._loop_latency.append(loop_msec)
        if code != 0:
            return code

        run_logger.debug("_handle_stop_queue")
        self._handle_stop_queue()
        return code