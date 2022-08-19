from re import X
from slimfat.structs import CStruct


# Definitions in mach-o/fat.h
class FatHeaderStruct(CStruct):
    magic: bytes
    nfat_arch: int

    @staticmethod
    def packsize() -> int:
        return 4 + 4

    def _struct_vals(self) -> tuple:
        return ("magic", "nfat_arch")

    def _struct_fmt(self) -> str:
        return "II"

class FatArchStructBase(CStruct):
    cputype: int
    cpusubtype: int
    offset: int
    size: int
    align: int

    @staticmethod
    def packsize() -> int:
        return 4 + 4

    def _struct_vals(self) -> tuple:
        return ("cputype", "cpusubtype", "offset", "size", "align")

    def _struct_fmt(self) -> str:
        return "ii"

class FatArchStruct(FatArchStructBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(fmt="III", **kwargs)

    @staticmethod
    def packsize() -> int:
        return FatArchStructBase.packsize() + 4 + 4 + 4

    @staticmethod
    def magic() -> int:
        return 0xcafebabe

    def _struct_fmt(self) -> str:
        return f"{super()._struct_fmt()}III"


# This class does not seem to work, but it is exactly as defined to my knowledge...
# objdump, however, recognizes it, so I assume it just isn't implemented just yet
class FatArch64Struct(FatArchStructBase):
    reserved: int = 0

    @staticmethod
    def packsize() -> int:
        return FatArchStructBase.packsize() + 8 + 8 + 4 + 4

    @staticmethod
    def magic() -> int:
        return 0xcafebabf

    def _struct_fmt(self) -> str:
        return f"{super()._struct_fmt()}QQII"

    def _struct_vals(self) -> tuple:
        return (*super()._struct_vals(), "reserved")
