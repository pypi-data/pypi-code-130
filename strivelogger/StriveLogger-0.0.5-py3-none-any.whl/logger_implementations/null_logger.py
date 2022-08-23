from typing import Dict, Optional, Union

from ..logger_implementation import LoggerImplementation


class NullLogger(LoggerImplementation):
    """
    This logger is used as the default logger implementation if no other logger is initialized.

    Log messages are discarded.

    There may be valid use-cases for this logger in production, but it's primary purpose to
    avoid null pointer exceptions in the StriveLogger.
    """

    def debug(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        pass

    def info(cls, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        pass

    def warn(cls, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        pass

    def error(
        cls,
        message: str,
        trace_id: Optional[str],
        exc_info: Optional[Union[BaseException, str]],
        extra: Optional[Dict],
    ) -> None:
        pass
