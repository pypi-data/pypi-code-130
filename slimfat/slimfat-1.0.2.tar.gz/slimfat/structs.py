from struct import pack

class CStruct():
    fmt: str

    def __init__(self, fmt: str, endian: str) -> None:
        self.fmt = f"{endian}{fmt}"

    def _pack(self, *args) -> bytes:
        return pack(self.fmt, *args)
