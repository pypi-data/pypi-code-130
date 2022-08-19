from slimfat.structs import CStruct


# Definitions in mach-o/fat.h
class FatHeaderStruct(CStruct):
    magic: bytes
    nfat_arch: int

    def __init__(self, endian: str, magic: int, nfat_arch: int) -> None:
        super().__init__(fmt="II", endian=endian)
        self.magic = magic
        self.nfat_arch = nfat_arch

    def pack(self) -> bytes:
        return self._pack(self.magic, self.nfat_arch)


class FatArchStructBase(CStruct):
    cputype: int
    cpusubtype: int
    offset: int
    size: int
    align: int

    def __init__(self, fmt: str, endian: str, cputype: int, cpusubtype: int, offset: int, size: int, align: int) -> None:
        super().__init__(fmt=f"ii{fmt}", endian=endian)
        self.cputype = cputype
        self.cpusubtype = cpusubtype
        self.offset = offset
        self.size = size
        self.align = align

    @staticmethod
    def packsize() -> int:
        return 4 + 4

    def _pack(self, *args) -> bytes:
        return super()._pack(self.cputype, self.cpusubtype, self.offset, self.size, self.align, *args)


class FatArchStruct(FatArchStructBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(fmt="III", **kwargs)

    @staticmethod
    def packsize() -> int:
        return FatArchStructBase.packsize() + 4 + 4 + 4

    @staticmethod
    def magic() -> int:
        return 0xcafebabe

    def pack(self) -> bytes:
        return self._pack()


# This class does not seem to work, but it is exactly as defined to my knowledge...
# objdump, however, recognizes it, so I assume it just isn't implemented just yet
class FatArch64Struct(FatArchStructBase):
    reserved: int

    def __init__(self, **kwargs) -> None:
        super().__init__(fmt="QQII", **kwargs)
        self.reserved = 0

    @staticmethod
    def packsize() -> int:
        return FatArchStructBase.packsize() + 8 + 8 + 4 + 4

    @staticmethod
    def magic() -> int:
        return 0xcafebabf

    def pack(self) -> bytes:
        return self._pack(self.reserved)
