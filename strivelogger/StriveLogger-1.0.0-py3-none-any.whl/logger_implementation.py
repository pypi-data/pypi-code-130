from abc import ABC, abstractmethod
from typing import Dict, Optional, Union


class LoggerImplementation(ABC):
    @abstractmethod
    def debug(
        self,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def info(
        self,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def warn(
        self,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def error(
        self,
        message: str,
        trace_id: Optional[str],
        exc_info: Optional[Union[BaseException, str]],
        extra: Optional[Dict],
    ) -> None:
        raise NotImplementedError()
