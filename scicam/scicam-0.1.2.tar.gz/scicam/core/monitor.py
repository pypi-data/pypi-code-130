import logging
import os.path
import time
import math

logger = logging.getLogger(__name__)
write_logger = logging.getLogger("scicam.write_logger")

import multiprocessing
import threading
import queue
import pandas as pd
import arrayqueues
from scicam.io.recorders import ImgStoreRecorder
from scicam.web_utils.sensor import setup as setup_sensor
from scicam.exceptions import ServiceExit
from scicam.io.cameras import CAMERAS
from scicam.utils import load_config

class Monitor(threading.Thread):
    _RecorderClass = ImgStoreRecorder

    def __init__(
        self,
        camera_name,
        camera_idx,
        path,
        format,
        start_time,
        *args,
        stop_queue=None,
        sensor=None,
        rois=None,
        select_rois=False,
        chunk_duration=300,
    ):

        self._camera_name = camera_name
        self._camera_idx = camera_idx
        self._root_path = path
        self._select_rois = select_rois
        os.makedirs(self._root_path, exist_ok=True)
        logger.debug(f"{self} chunk_duration: {chunk_duration}")

        self.setup_camera(
            camera_name=camera_name,
            idx=camera_idx,
            rois=rois,
            start_time=start_time,
        )

        self._stop_queue = stop_queue
        self._setup_queues()
        self._stop_event = multiprocessing.Event()

        self._recorders = []

        for i in range(len(self.camera.rois)):
            
            metadata = {
                "camera-framerate": self.camera.framerate,
                "camera-exposure": self.camera.exposure,
                "camera-model": self.camera.model_name,
            }
            
            recorder = self._RecorderClass(
                framerate=float(int(self.camera.framerate)),
                duration=self.camera.duration,
                resolution = self.camera.rois[i][2:4],
                path=self._root_path,
                data_queue = self._data_queues[i],
                stop_queue = self._stop_queues[i],
                sensor=sensor,
                idx=i,
                roi=self.camera.rois[i],
                metadata=metadata,
                format=format,
                chunk_duration=chunk_duration,
            )
            self._recorders.append(recorder)

        super(Monitor, self).__init__()


    def __str__(self):
        return f"Monitor driving camera {self._camera_name}"


    def _setup_queues(self):

        self._data_queues = [
            arrayqueues.TimestampedArrayQueue(100) for _ in self.camera.rois
        ]
        
        self._stop_queues = [
            multiprocessing.Queue(maxsize=1) for _ in self.camera.rois
        ]

    def setup_camera(self, camera_name, **kwargs):
        config = load_config()

        duration = config["cameras"][camera_name]["duration"]
        framerate = config["cameras"][camera_name]["framerate"]
        exposure = config["cameras"][camera_name]["exposure"]

        print(camera_name, end=":")
        print(f"    Framerate {framerate}")
        print(f"    Exposure {exposure}")
        

        self.camera = CAMERAS[camera_name](
            document_path=self._root_path,
            framerate=framerate,
            exposure=exposure,
            duration=duration,
            **kwargs
        )

        if self._select_rois:
            self.camera.select_ROIs()

    def open(self):
        for idx in range(len(self.camera.rois)):

            recorder_path = f"{self._root_path.rstrip('/')}_ROI_{idx}"
            self._recorders[idx].open(
                path=recorder_path
            )
            logger.info(
                f"{self._recorders[idx]} for {self.camera} has recorder_path = {recorder_path}"
            )

    def put(self, recorder, data_queue, data):

        timestamp, i, arr, info = data
        try:
            data_queue.put(arr, timestamp=(timestamp, i, info))
            recorder._n_saved_frames += 1
        except queue.Full:
            # data_queue.get()
            recorder.n_lost_frames += 1
            if recorder.n_lost_frames % 100 == 0 or recorder.n_saved_frames % 100 == 0:
                logger.warning(
                    f"{self} Data queue is full!"\
                    f" Wrote {recorder.n_saved_frames} frames."\
                    f" Lost {recorder.n_lost_frames} frames"\
                    f" That means ({100 * recorder.n_lost_frames / recorder.n_saved_frames}) % of all frames are dropped"
                )


    def run(self):

        logger.info("Monitor starting")
        self._start_time = self.camera.start_time
        for i, recorder in enumerate(self._recorders):
            recorder.start_time = self._start_time
            recorder.start()
            logger.debug("Recorder starting")
            roi = self.camera._rois[i]
            roi_df = pd.DataFrame({
                "x": [roi[0]], "y": [roi[1]],
                "w": [roi[2]], "h": [roi[3]],
                "camera_name": [self.camera.__class__.__name__.replace("Camera", "")]
            })

            if self._select_rois:
                roi_df.to_csv("rois.csv", mode='a', index=False, header=False)

        last_timestamp = 0
        for frame_idx, (timestamp, frame, info) in enumerate(self.camera):
            # proc_time = timestamp - last_timestamp
            # logger.debug(
            #     f"Frame processing time: {proc_time}"
            #     f"FPS approx {round(1000/proc_time, 2)}"
            # )

            if self._stop_event.is_set():
                logger.info("Monitor exiting")

                for i in range(len(self._recorders)):
                    logger.debug(
                        f"Recorder {i} output queue has {self._recorders[i].buffer_usage} frames"
                    )
                break

            if self._stop_queue is not None:
                try:
                    msg = self._stop_queue.get(False)
                except queue.Empty:
                    msg = None
                if msg == "STOP":
                    logger.debug(f"Setting {self} stop event")
                    self._stop_event.set()

            for i in range(len(self.camera.rois)):
                recorder = self._recorders[i]
                self.put(
                    recorder=recorder,
                    data_queue=self._data_queues[i],
                    data=(timestamp, frame_idx, frame[i], info)
                )
                # _, write_msec = recorder.write(timestamp, frame_idx, frame[i])
                # write_logger.debug(f"Recorder took {write_msec} ms to write")
            last_timestamp = timestamp

        logger.debug("Joining recorders")
        for recorder in self._recorders:
            if recorder.is_alive():
                while not recorder.all_queues_have_been_emptied:
                    time.sleep(1)
                    logger.debug("Waiting for", recorder)

                logger.debug("Report one last time ", recorder)
                recorder.check_data_queue()
                logger.debug("Close tqdm for ", recorder)
                logger.debug("Joining", recorder)
                # recorder._data_queue.put(None)
            recorder.join()
            logger.debug("JOOOOIIIIIINEEEEDD")

        logger.debug("Joined all recorders")

    def close(self):

        # this makes the run method exit
        # because it checks if the stop_event is set
        self._stop_event.set()
        logger.info("Monitor closing")

        for recorder in self._recorders:
            recorder.close()


def run(monitor):

    monitor.open()
    try:
        monitor.start()
        time.sleep(5)
        monitor.join()
        # while monitor.is_alive():
        #    print("Running time sleep forever")
        #    time.sleep(0.5)

    except ServiceExit:
        print("ServiceExit captured at Monitor level")
        monitor.close()
    except Exception as error:
        print(error)
    finally:
        print(f"Joining monitor {monitor}")
        monitor.join()
        print(f"Joined monitor {monitor}")
        if monitor._stop_queue is not None:
            print(f"stop_queue size: {monitor._stop_queue.qsize()}")

        for some_queue in monitor._stop_queues:
            print(f"{some_queue} size: {some_queue.qsize()}")


