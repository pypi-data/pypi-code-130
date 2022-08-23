import traceback
from typing import Dict, Optional, Union

from ..logger_implementation import LoggerImplementation


class ConsoleLogger(LoggerImplementation):
    def __log(
        self, level: str, message: str, trace_id: Optional[str], extra: Dict = None
    ) -> None:
        if trace_id:
            message = f"[{trace_id}] {message}"

        level = f"{level}:".ljust(10)
        print(f"{level}{message}")
        if extra:
            print(f"{'EXTRA:'.ljust(10)} {extra}")

    def debug(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        self.__log("DEBUG", message, trace_id, extra)

    def info(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        self.__log("INFO", message, trace_id, extra)

    def warn(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        self.__log("WARN", message, trace_id, extra)

    def error(
        self,
        message: str,
        trace_id: Optional[str],
        exc_info: Optional[Union[BaseException, str]],
        extra: Optional[Dict],
    ) -> None:
        self.__log("ERROR", message, trace_id, extra)
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = "\n".join(
                    traceback.format_exception(
                        type(exc_info), exc_info, exc_info.__traceback__
                    )
                )
            print(f"{'EXC_INFO:'.ljust(10)} {exc_info}")
