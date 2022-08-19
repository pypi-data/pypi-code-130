from abc import abstractmethod
from struct import pack, unpack

class CStruct():
    endian: str

    VALID_ENDIAN = ["<", ">"]

    def __init__(self, endian: str = ">", **kwargs) -> None:
        if endian not in self.VALID_ENDIAN:
            raise ValueError("Invalid endianness")
        self.endian = endian

        for k, v in kwargs.items():
            self.__setattr__(k, v)

    @abstractmethod
    def _struct_vals(self) -> tuple:
        pass

    @abstractmethod
    def _struct_fmt(self) -> str:
        pass

    def _struct_fmt_full(self) -> str:
        return f"{self.endian}{self._struct_fmt()}"

    def pack(self) -> bytes:
        return pack(self._struct_fmt_full(), *map(lambda k : getattr(self, k), self._struct_vals()))

    def unpack(self, buf: bytes) -> None:
        vals = self._struct_vals()
        for i, val in enumerate(unpack(self._struct_fmt_full(), buf)):
            setattr(self, vals[i], val)
