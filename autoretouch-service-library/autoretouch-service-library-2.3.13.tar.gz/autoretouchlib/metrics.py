import logging
import threading

from google.cloud import logging as gc_logging


class Metrics:
    disabled = True

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, project: str):
        import os
        self.disabled = not os.getenv("METRICS_ENABLED", 'False').lower() in ('true', '1', 't')
        if self.disabled:
            return

        self.project = project
        self.service_name = os.getenv("K_SERVICE") if os.getenv("K_SERVICE") else os.getenv("SERVICE_NAME",
                                                                                            "test-service")
        client = gc_logging.Client()
        client.setup_logging()

        self.storage_access_sink = lambda payload: logging.info("storage_access", extra=payload)

        logging.info(f"Metrics initialized for {self.service_name} in {project}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(x={self.project}, y={self.service_name})"

    def _count_storage_access(self, storage_class: str, operation: str, file_type: str):
        try:
            self.storage_access_sink({"message": "storage_access",
                                      "serviceName": self.service_name,
                                      "storageClass": "STANDARD" if storage_class is None else storage_class,
                                      "operation": operation,
                                      "fileType": "UNKNOWN" if file_type is None else file_type
                                      })
        except Exception as e:
            logging.warning(f"Exception during while writing log metrics", e)

    def count_storage_access(self, storage_class: str, operation: str, file_type: str):
        if self.disabled:
            return
        thread = threading.Thread(target=self._count_storage_access(storage_class, operation, file_type))
        thread.start()
