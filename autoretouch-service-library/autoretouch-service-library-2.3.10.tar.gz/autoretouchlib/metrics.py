import logging
import threading
import time
import uuid

from google.api import metric_pb2 as ga_metric
from google.cloud import monitoring_v3


class Metrics:
    disabled = True

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, project: str):
        import os
        self.disabled = not os.getenv("METRICS_ENABLED", 'False').lower() in ('true', '1', 't')
        if self.disabled:
            return
        self.service_name = os.getenv("K_SERVICE") if os.getenv("K_SERVICE") else os.getenv("SERVICE_NAME",
                                                                                            "testService")
        self.project = project
        self.client = monitoring_v3.MetricServiceClient()
        self.storage_sink = self.__init_storage_access_count()
        logging.info(f"Metrics initialized with for {self.service_name} in {project}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(x={self.project}, y={self.service_name})"

    def __init_storage_access_count(self) -> ga_metric.MetricDescriptor:
        name = f"custom.googleapis.com/storage/access_count"
        try:
            storage_descriptor = self.client.get_metric_descriptor(
                name=f"projects/{self.project}/metricDescriptors/{name}"
            )
        except Exception as e:
            logging.warning("Metric not found! Disabling metric collection!", e)
            self.disabled = True
            return None
        return storage_descriptor

    def _count_storage_access(self, storage_class: str, operation: str, file_type: str):
        try:
            series = monitoring_v3.TimeSeries()
            series.metric.type = self.storage_sink.type
            series.resource.type = "global"
            series.resource.labels["project_id"] = self.project
            series.metric.labels["service_name"] = self.service_name
            series.metric.labels["storage_class"] = "STANDARD" if storage_class is None else storage_class
            series.metric.labels["operation"] = operation
            series.metric.labels["file_type"] = "UNKNOWN" if file_type is None else file_type
            series.metric.labels["uuid"] = uuid.uuid4().__str__()
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {
                    "end_time": {"seconds": seconds, "nanos": nanos}
                }
            )
            point = monitoring_v3.Point({"interval": interval, "value": {"int64_value": 1}})
            series.points = [point]
            self.client.create_time_series(name=f"projects/{self.project}", time_series=[series])
        except Exception as e:
            logging.warning(f"Exception during while counting metrics", e)

    def count_storage_access(self, storage_class: str, operation: str, file_type: str):
        if self.disabled:
            return
        thread = threading.Thread(target=self._count_storage_access(storage_class, operation, file_type))
        thread.start()
