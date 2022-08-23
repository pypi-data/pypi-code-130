import json
import logging
import traceback
from typing import Any, Dict, Literal, Optional, Union

from ..logger_implementation import LoggerImplementation

LEVELS = Literal["ERROR", "WARN", "INFO", "DEBUG"]


class PythonLogger(LoggerImplementation):
    """
    Use a python logger instance with the specified name, creating it if necessary.

    If no name is specified the root logger will be used.
    """

    def __init__(
        self,
        logger_name: Optional[str] = None,
        level: LEVELS = "INFO",
        enable_json: bool = False,
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        self.enable_json = enable_json

    def __create_json_record(
        self,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
        exc_info: Optional[Union[BaseException, str]] = None,
    ) -> str:
        record: Dict[str, Any] = {
            "message": message,
        }

        if trace_id:
            record["trace_id"] = trace_id
        if extra:
            record["extra"] = extra
        if exc_info:
            if isinstance(exc_info, BaseException):
                record["exc_info"] = traceback.format_exception(exc_info)
            else:
                record["exc_info"] = str(exc_info)

        return json.dumps(record)

    def __log_json(
        self,
        level: int,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
        exc_info: Optional[Union[BaseException, str]] = None,
    ) -> None:
        record = self.__create_json_record(message, trace_id, extra, exc_info)
        self.logger.log(level, record)

    def __log_string(
        self,
        level: int,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
        exc_info: Optional[Union[BaseException, str]] = None,
    ) -> None:
        if trace_id:
            message = f"[{trace_id}] {message}"

        if extra:
            message = f"{message}\n\t\t{extra}"

        self.logger.log(level, message, exc_info=exc_info)  # type: ignore

    def __log(
        self,
        level: int,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
        exc_info: Optional[Union[BaseException, str]] = None,
    ) -> None:
        log = self.__log_json if self.enable_json else self.__log_string
        log(
            level,
            message,
            trace_id,
            extra,
            exc_info,
        )

    def debug(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        self.__log(logging.DEBUG, message, trace_id, extra)

    def info(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        self.__log(logging.INFO, message, trace_id, extra)

    def warn(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        self.__log(logging.WARN, message, trace_id, extra)

    def error(
        self,
        message: str,
        trace_id: Optional[str],
        exc_info: Optional[Union[BaseException, str]],
        extra: Optional[Dict],
    ) -> None:
        self.__log(logging.ERROR, message, trace_id, extra, exc_info)
        # if trace_id:
        #     message = f"[{trace_id}] {message}"

        # if extra:
        #     message = f"{message}\n\t\t{extra}"

        # self.logger.error(message, exc_info=exc_info)  # type: ignore
