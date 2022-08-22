from typing import TypeAlias
from .exceptions import *


HexCode: TypeAlias = list[str]
IntCode: TypeAlias = list[int]


def intc_to_hexc(ic: IntCode | list[int]) -> HexCode:
    hc = []
    for ii in ic:
        hc.append(hex(ii))
    return hc


def hexc_to_intc(hc: HexCode | list[str]) -> IntCode:
    ic = []
    for ii in hc:
        ic.append(int(ii, 16))
    return ic


def str_to_hexc(s: str) -> HexCode:
    h: HexCode = []
    for ii in s:
        h.append(hex(ord(ii)))

    return h


def hexc_to_str(h: HexCode) -> str:
    s = []
    for ii in h:
        s.append(chr(int(ii, 16)))

    return "".join(s)


def read_hc_file(path: str) -> HexCode:
    rb: bytes = None
    with open(path, "rb") as f:
        rb = f.read()

    rb = list(rb)
    hexcode: HexCode = []
    for dec in rb:
        hexcode.append(hex(dec))

    return hexcode


def write_hc_file(path: str, hexcode: HexCode) -> None:
    try:
        intcode = hexc_to_intc(hexcode)
        bytecode = bytes(intcode)  # to bytes

        with open(path, "wb") as f:  # save
            f.write(bytecode)

    except ValueError:
        raise TASM_IntSizeToBigError()


__all__ = [
    "write_hc_file",
    "read_hc_file",
    "intc_to_hexc",
    "hexc_to_intc",
    "str_to_hexc",
    "hexc_to_str",
    "HexCode",
    "IntCode",
]
