import json
import logging
from typing import Any, Dict, Optional, Tuple

from .python_logger import LEVELS, PythonLogger


class UvicornLogger(PythonLogger):
    """
    Use the uvicorn logger instance.

    Equivalent to creating a PythonLogger with logger_name 'uvicorn'.
    """

    def __init__(self, level: LEVELS = "INFO", enable_json: bool = False) -> None:
        super().__init__("uvicorn", level, enable_json)

        if enable_json and "uvicorn.access" in logging.Logger.manager.loggerDict:
            access_logger = logging.getLogger("uvicorn.access")
            if len(access_logger.handlers) > 0:
                access_logger.handlers[0].formatter = UvicornAccessFormatter()


class UvicornAccessFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: Dict[str, Any] = {
            "message": record.getMessage(),
        }
        if "HTTP/" in record.msg:
            UvicornAccessFormatter.add_request_info(log, record.args)  # type: ignore

        return json.dumps(log)

    @staticmethod
    def add_request_info(log: Dict[str, Any], args: Optional[Tuple]) -> None:
        if args and len(args) >= 5:
            host = args[0]
            method = args[1]
            path = args[2]
            status_code = args[4]
            is_error_code = status_code >= 400

            log["host"] = host
            log["method"] = method
            log["path"] = path
            log["status_code"] = status_code
            log["success"] = not is_error_code
