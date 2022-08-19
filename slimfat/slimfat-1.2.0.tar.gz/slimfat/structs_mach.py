from slimfat.structs import CStruct


# Defined in mach-o/loader.h
class MachHeaderBegin(CStruct):
    magic: int
    cputype: int
    cpusubtype: int

    VALID_MAGICS: list = [
        0xfeedface,
        0xfeedfacf,
    ]

    def _struct_fmt(self) -> str:
        return "III"

    def _struct_vals(self) -> tuple:
        return ("magic", "cputype", "cpusubtype")

    def unpack(self, buf: bytes) -> None:
        if buf[0] == 0xfe:
            self.endian = ">"
        elif buf[3] == 0xfe:
            self.endian = "<"

        super().unpack(buf)

        if self.magic not in self.VALID_MAGICS:
            raise ValueError("Invalid magic")

    @staticmethod
    def packsize():
        return 4 + 4 + 4
