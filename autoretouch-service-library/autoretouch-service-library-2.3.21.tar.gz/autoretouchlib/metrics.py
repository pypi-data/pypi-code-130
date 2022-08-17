import json
import logging


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
        service_name = os.getenv("K_SERVICE") if os.getenv("K_SERVICE") else os.getenv("SERVICE_NAME",
                                                                                       "test-service")

        self.storage_access_sink = lambda payload: print(
            json.dumps(dict(
                severity="DEBUG",
                message="storage_access",
                name="storage_access",
                serviceName=service_name,
                **payload))
        )

        logging.info(f"Metrics initialized for {service_name} in {project}")

    def count_storage_access(self, storage_class: str, operation: str, file_type: str, **kwargs):
        if self.disabled:
            return
        try:
            self.storage_access_sink(dict(
                storageClass="STANDARD" if storage_class is None else storage_class,
                operation=operation,
                fileType="application/octet-stream" if file_type is None else file_type,
                **kwargs
            ))
        except Exception as e:
            logging.info("Error while writing metric logs!", e)
