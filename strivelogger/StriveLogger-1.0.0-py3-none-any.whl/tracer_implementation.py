from abc import ABC, abstractmethod
from typing import Optional


class TracerImplementation(ABC):
    @abstractmethod
    def get_trace_id(self) -> Optional[str]:
        raise NotImplementedError()
