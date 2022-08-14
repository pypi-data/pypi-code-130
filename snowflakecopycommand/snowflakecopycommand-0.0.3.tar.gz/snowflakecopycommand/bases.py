from abc import ABC
from .enums import FileFormat
from typing import Dict

class Namespaced(ABC):
    @property
    def fullname(self) -> str:
        pass

class SQL(ABC):
    @property
    def sql(self) -> str:
        pass

    def to_dict(self) -> Dict[str, str]:
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        }

class FileFormatType(ABC):
    @property
    def ff_type(self) -> FileFormat:
        pass