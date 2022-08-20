import traceback
import logging
import sys
import time
import multiprocessing
import os.path

import tqdm
import cv2
import imgstore
import numpy as np

from scicam.utils import document_for_reproducibility
from scicam.exceptions import ServiceExit
from scicam.decorators import timeit
from scicam.io.recorders.core import BaseRecorder
from imgstore.stores.utils.formats import get_formats
FMT_TO_CODEC=get_formats(video=True)

ENCODER_FORMAT_CPU="divx/avi"
ENCODER_FORMAT_GPU="h264_nvenc/mp4"

logger = logging.getLogger(__name__)
run_logger = logging.getLogger(f"{__name__}.run")

class ImgStoreRecorder(BaseRecorder):
        
    # look here for possible formats:
    # Video -> https://github.com/loopbio/imgstore/blob/d69035306d816809aaa3028b919f0f48455edb70/imgstore/stores.py#L932
    # Images -> https://github.com/loopbio/imgstore/blob/d69035306d816809aaa3028b919f0f48455edb70/imgstore/stores.py#L805
    # if you dont have enough RAM, you dont want to make this number huge
    # otherwise you will run out of RAM

    def __init__(
        self, *args, format=None,
        chunk_duration = 300, info_frequency=60, extra_data_frequency=10,
        **kwargs
    ):

        super(ImgStoreRecorder, self).__init__(*args, **kwargs)
        self.n_lost_frames = 0
        self._n_saved_frames = 0
        self._time_s = 0


        if format is None:
            logger.warning(
                f"scicam using {ENCODER_FORMAT_CPU} to encode video data"
                f" you may want to use {ENCODER_FORMAT_GPU} if CUDA is enabled"
            )
            format = ENCODER_FORMAT_CPU

        self._current_chunk = -1
        self.chunk_duration = chunk_duration
        logger.debug(f"{self} chunk_duration: {chunk_duration}")
        self._chunksize = self.chunk_duration * self._framerate
        self._buffer_usage = 0
        self._format = format
        self._start_event = multiprocessing.Event()
        self._stop_event = multiprocessing.Event()
        self._show_initialization_info()

        self._write_msec = 0
        self._fps = 0

        self._info_freq = info_frequency
        self._extra_data_freq = extra_data_frequency


        imgshape = self._resolution[:2][::-1]
        metadata = {}

        versions = document_for_reproducibility()
        metadata.update(versions)

        self._video_writer = imgstore.new_for_format(
            mode="w",
            fmt=format,
            fps=self._framerate,
            basedir=self._path,
            imgshape=imgshape,
            chunksize=self._chunksize,
            imgdtype=np.uint8,
            **metadata
        )

        self._make_tqdm = True

        if self._make_tqdm:
            self._tqdm = tqdm.tqdm(
                position=self.idx,
                total=100,
                unit="",
                desc=f"{self.name} - {self.idx}" + r" % Buffer usage",
            )

    @property
    def n_saved_frames(self):
        return self._n_saved_frames

    @property
    def buffer_usage(self):
        return self._buffer_usage
    
    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"ImgStore - {self._path}"

    def report_time(self):
        logger.debug(f"{self._path} - Timestamp {time.time()} @ {self._video_writer._basedir}: {self._video_writer._tN}")
        logger.debug(f"{self._path} - Timestamp {time.time()} @ {self._video_writer._basedir}: {self._time_s}")
                
    def _process_data(self, data):
        timestamp, i, frame, camera_info = data
        if camera_info is not None:
            self._camera_info = camera_info

        self._time_s = timestamp / 1000
        run_logger.debug("_write")
        _, write_msec = self._write(timestamp, i, frame)
        bytes = sys.getsizeof(frame)
        MB = round(bytes / 1024, ndigits=2)
        self._file_size.append(MB)
        self._write_latency.append(write_msec)
        self._write_msec = write_msec

        if self._has_new_chunk():
            self._save_first_frame_of_chunk(frame)


    def _save_extra_data(self, **kwargs):

        try:
            self._video_writer.add_extra_data(**kwargs)
            return 0
        except Exception as error:
            logger.error(
                "Unknown error. See more details following this message"
            )
            logger.error(error)
            logger.error(traceback.print_exc())
            return 1


    def _get_environmental_data(self):
        logger.debug("flyhostel.sensor.query")
        return self._sensor.query(timeout=1)


    def save_extra_data(self):

        code = 1
        if self.sensor is None:
            return code

        logger.debug("_get_environmental_data")
        environmental_data = self._get_environmental_data()


        if environmental_data is None:
            logger.warning("Could not fetch environmental data")
        else:
            logger.debug("_save_extra_data")
            code = self._save_extra_data(
                camera_temperature=self._camera_info.get("temperature", None),
                temperature=environmental_data["temperature"],
                humidity=environmental_data["humidity"],
                light=environmental_data["light"],
                time=self._time_s,
            )

        return code


    def open(self, path=None):

        if path is not None:
            logger.warning("Ignoring path")

    def _show_initialization_info(self):
        logger.info("Initializing Imgstore video with following properties:")
        logger.info("  Resolution: %dx%d", *self.resolution)
        logger.info("  Path: %s", self._path)
        logger.info("  Format (codec): %s", self._format)
        logger.info("  Chunksize: %s", self._chunksize)
        logger.info("  Framerate: %s", self._framerate)


    def terminate(self):
        time.sleep(1)
        super(ImgStoreRecorder, self).terminate()
        time.sleep(1)


    def close(self):
        # to tell the async writer the recorder is finished
        self._stop_queue.put("STOP")
        self._stop_event.wait(.1)

    def run(self):
        """
        Collect frames from the source and write them to the video
        Periodically log #frames saved
        """
        logger.debug("first line of imgstore.run")
        self.start_time = time.time()
        self._start_event.set()

        try:
            logger.debug("before call to imgstore._run")
            self._run()
            logger.debug("after call to imgstore._run")
    
        except ServiceExit:
            print(f"ServiceExit detected by {self}. Please wait")
        except Exception as error:
            logger.error(error)
            logger.error(traceback.print_exc())

        finally:
            self._video_writer.close()
            # to avoid hanging
            self._exit_gracefully()

            logger.debug("imgstore finishing")
            logger.debug(
                "Queues: "\
                f" data_queue: {self._data_queue.qsize()}"\
                f" stop_queue: {self._stop_queue.qsize()}"\
            )
            
            return 


    def _exit_gracefully(self):
        if not self.check_data_queue(target=0):
            logger.warning(f"{self} - Buffer usage on exit {self._buffer_usage} != 0")
        assert self._stop_queue.empty()
        return 0



    def _run(self):
        while not self._stop_event.is_set():
            
            if self.tick(1):
                self._fps = 0

            if self.tick(self._info_freq):
                self._report(self._buffer_usage)
            if self.tick(self._extra_data_freq):
                self.save_extra_data()
            
            if self.should_stop():
                break

            code, msec = self._run_data()
            if code != 0:
                break

        while not self.check_data_queue(target=0):
            if self.tick(self._info_freq):
                self._report(self._buffer_usage)
            if self.tick(self._extra_data_freq):
                self.save_extra_data()
                
            code, msec = self._run_data()
            if code != 0:
                break

        logger.debug(f"should stop: {self.should_stop()}")
 

    def safe_join(self, timeout):
        self.join(timeout=timeout)
        if self.exitcode is None:
            return 1
        else:
            return self.exitcode

    def should_stop(self):

        result = (
            self.duration_reached
            or self.max_frames_reached
        )

        return result


    def _report(self, target):
        self._report_fps()
        self._check_io_benchmark()
        self.check_data_queue(target=target)
        self.report_time()
    
    def _report_fps(self):
        logger.debug(f"{self._path} - Saved frames {self._n_saved_frames}")
        logger.debug(f"{self._path} - {self._fps} FPS")

    def _check_io_benchmark(self):
        loop_ms_latency_mean = np.array(self._loop_latency).mean()
        logger.debug(f"{self._path} - Average loop time: {loop_ms_latency_mean:.2f} ms")
        
        read_ms_latency_mean = np.array(self._read_latency).mean()
        logger.debug(f"{self._path}- Average read time: {read_ms_latency_mean:.2f} ms")
        
        write_latency_mean = np.array(self._write_latency).mean()
        logger.debug(f"{self._path} - Average write time: {write_latency_mean:.2f} ms")
        logger.debug(f"{self._path} - Last write time: {self._write_msec:.2f} ms")

        file_size_mean = np.array(self._file_size).mean()
        logger.debug(f"{self._path} - Average file size: {file_size_mean:.2f} MB")
    

    def check_data_queue(self, target=0):

        q = self._data_queue
        buffer_usage = q.view.nbytes_el * q.qsize() / q.maxbytes

        if buffer_usage != target:

            if self._make_tqdm:
                self._tqdm.n = int(self._buffer_usage)
                self._tqdm.refresh()
            else:

                logger.info(
                    f"Buffer: {buffer_usage} / {q.maxbytes} MB"
                )

        self._buffer_usage = buffer_usage
        return self._buffer_usage == target


    @timeit
    def _write(self, timestamp, i, frame):
        """
        Arguments:
            * timestamp (int): time in ms
            * i (int): frame number
            * frame (np.ndarray): frame
        """
        if not self._stop_event.is_set():
            self._timestamp = timestamp

        if frame is None:
            return None

        self._video_writer.add_image(frame, i, timestamp)
        self._n_saved_frames += 1
        self._fps += 1
        return None
    

    def _has_new_chunk(self):
        current_chunk = self._video_writer._chunk_n
        if current_chunk > self._current_chunk:
            self._current_chunk = current_chunk
            return True
        else:
            return False

    def _save_first_frame_of_chunk(self, frame=None):

        last_shot_path = os.path.join(
            self._path, str(self._current_chunk).zfill(6) + ".png"
        )
        cv2.imwrite(last_shot_path, frame)