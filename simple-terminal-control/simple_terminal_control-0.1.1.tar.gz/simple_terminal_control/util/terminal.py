from codecs import getincrementaldecoder
from contextlib import contextmanager
from select import select
from typing import IO, AnyStr
import os
import sys
import termios
import tty

_DECODER_TYPE = getincrementaldecoder("utf-8")


def _is_ready(file: IO[AnyStr]) -> bool:
    result = select([file], [], [], 0.0)
    return len(result[0]) > 0


def _read(limit: int):
    decoder = _DECODER_TYPE()
    buff = ""
    while len(buff) < limit:
        char = os.read(sys.stdin.fileno(), limit - len(buff))
        buff += decoder.decode(char)
    return buff


def read_chars(n: int | None = None):
    s = _read(1 if n is None else n)
    while (n is None or len(s) < n) and _is_ready(sys.stdin):
        s += _read(1 if n is None else n - len(s))
    return s


def read_chars_until(char: str):
    s = ""
    while True:
        c = read_chars(1)
        s += c
        if c == char:
            return s


def write_csi(s: str, flush: bool = False):
    sys.stdout.write(f"\x1b[{s}")
    if flush:
        sys.stdout.flush()


def assert_empty_read():
    assert not _is_ready(sys.stdin)


def _mouse_reporting(disable: bool):
    code = "l" if disable else "h"
    write_csi(f"?1000{code}", flush=True)
    write_csi(f"?1006{code}", flush=True)


@contextmanager
def setup(report_mouse: bool):
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())
    os.system("stty -echo")
    if report_mouse:
        _mouse_reporting(disable=False)
    try:
        yield
    except KeyboardInterrupt:
        pass
    finally:
        if report_mouse:
            _mouse_reporting(disable=True)
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
