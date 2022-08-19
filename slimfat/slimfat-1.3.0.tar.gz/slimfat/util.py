from os import open as os_open
from stat import S_IRWXG, S_IRWXO, S_IRWXU


def align_int(num: str, align_bytes: int) -> int:
    align_off = num % align_bytes
    if align_off == 0:
        return num
    return num + (align_bytes - align_off)


def executable_opener(path: str, flags: int) -> int:
    return os_open(path, flags, S_IRWXU | S_IRWXG | S_IRWXO)
