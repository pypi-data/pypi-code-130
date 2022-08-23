from typing import Dict, Optional, Union

from .logger_implementation import LoggerImplementation
from .logger_implementations.null_logger import NullLogger
from .tracer_implementation import TracerImplementation


class StriveLogger:
    _logger: LoggerImplementation = NullLogger()
    _tracer: Optional[TracerImplementation] = None

    @classmethod
    def initialize(
        cls,
        logger: LoggerImplementation,
        tracer: Optional[TracerImplementation] = None,
    ) -> None:
        if logger is not None and isinstance(logger, LoggerImplementation):
            cls._logger = logger

        cls._tracer = tracer

    @classmethod
    def logger_type(cls) -> str:
        return type(cls._logger).__name__

    @classmethod
    def get_trace_id(cls) -> Optional[str]:
        return cls._tracer.get_trace_id() if cls._tracer else None

    @classmethod
    def debug(cls, message: str, extra: Dict = None) -> None:
        cls._logger.debug(message, cls.get_trace_id(), extra)

    @classmethod
    def info(cls, message: str, extra: Dict = None) -> None:
        cls._logger.info(message, cls.get_trace_id(), extra)

    @classmethod
    def warn(cls, message: str, extra: Dict = None) -> None:
        cls._logger.warn(message, cls.get_trace_id(), extra)

    @classmethod
    def error(
        cls,
        message: str,
        exc_info: Optional[Union[BaseException, str]] = None,
        extra: Optional[Dict] = None,
    ) -> None:
        cls._logger.error(message, cls.get_trace_id(), exc_info, extra)
