
from struct import unpack


# Defined in mach-o/loader.h
class MachHeaderBegin():
    magic: int
    cputype: int
    cpusubtype: int

    VALID_MAGICS: list[bytes] = [
        0xfeedface,
        0xfeedfacf,
    ]

    def __init__(self, buf: bytes) -> None:
        endian = "<"
        if buf[0] == 0xfe:
            endian = ">"
        self.magic, self.cputype, self.cpusubtype = unpack(f"{endian}III", buf)
        if self.magic not in self.VALID_MAGICS:
            raise ValueError("Invalid magic")

    @staticmethod
    def packsize():
        return 4 + 4 + 4
