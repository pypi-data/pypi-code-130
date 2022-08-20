import logging
import multiprocessing
import threading
import traceback
import queue

import pandas as pd
import yaml

from scicam.io.cameras import CAMERAS
from scicam.constants import CAMERA_INDEX
from scicam.core.monitor import run as run_monitor
from scicam.core.monitor import Monitor

logger = logging.getLogger(__name__)

try:
    with open(CAMERA_INDEX, "r") as filehandle:
        camera_index = yaml.load(filehandle, yaml.SafeLoader)
except Exception as error:
    logger.warning(error)
    
class Manager:

    def __init__(self, idx, camera_name, format, output, sensor=None, rois=None, roi_helper=None, select_rois=False, resolution_decrease=1.0, chunk_duration=300):

        self.idx = idx
        self.camera_name = camera_name
        self.sensor = sensor
        self.roi_helper = roi_helper
        self.select_rois = select_rois
        self.rois=rois
        self.root_output = output
        self.chunk_duration=chunk_duration
        self.format = format
        self.process = None
        self.stop_queue = None
        self.resolution_decrease=resolution_decrease


    @staticmethod
    def separate_process(
        camera_name,
        output,
        format,
        sensor=None,
        stop_queue=None,
        process_id=0,
        rois=None,
        camera_idx=0,
        start_time=None,
        chunk_duration=300,
    ):
        logger.info("multiprocess.Process - scicam.bin.__main__.separate _process")

        logger.debug(f"Monitor running {camera_name} chunk_duration: {chunk_duration}")
        monitor = Monitor(
            camera_name=camera_name,
            camera_idx=camera_idx,
            path=output,
            format=format,
            start_time=start_time,
            stop_queue=stop_queue,
            sensor=sensor,
            rois=rois,
            select_rois=False,
            chunk_duration=chunk_duration,
        )


        logger.info(f"Monitor start time: {start_time}")

        monitor.process_id = process_id
        return monitor


    def init(
        self, start_time,
    ):
        camera_idx = camera_index[self.camera_name]

        if self.select_rois:

            camera = CAMERAS[self.camera_name](
                start_time=start_time,
                roi_helper=self.roi_helper,
                resolution_decrease=self.resolution_decrease,
                idx=camera_idx,
            )

            logger.info(f"Selecting rois for {camera}")
            if self.select_rois:
                rois = camera.select_ROIs()
            # save the roi and somehow give it to the next instance
            camera.close()

        elif self.rois is not None:
            # TODO Make a function out of this
            roi_data = pd.read_csv(self.rois)
            assert all([col in roi_data.columns for col in ["x", "y", "w", "h", "camera_name"]])
            roi_data = roi_data.loc[roi_data["camera_name"] == self.camera_name]
            rois = [(row.x, row.y, row.w, row.h) for i, row in roi_data.iterrows()]

        else:
            camera = CAMERAS[self.camera_name](
                            start_time=start_time,
                            resolution_decrease=self.resolution_decrease,
                            idx=camera_idx,
            )
            width=max(camera.width, camera.height)
            height=width
            camera.close()
            rois = [(0, 0, width, height)]
            
        self.stop_queue = queue.Queue(maxsize=1)       
        
        kwargs = {
            "sensor": self.sensor,
            "stop_queue": self.stop_queue,
            "process_id": self.idx,
            "rois": rois,
            "camera_idx": camera_idx,
            "start_time": start_time,
            "chunk_duration": self.chunk_duration
        }


        monitor=self.separate_process(
            camera_name=self.camera_name, output=self.root_output, format=self.format, **kwargs
        )
        return monitor


    def start(self):
        return self.process.start()

    def join(self, *args, **kwargs):
        return self.process.join(*args, **kwargs)
    
    def is_alive(self, *args, **kwargs):
        return self.process.is_alive(*args, **kwargs)
