import itertools
import sys
from uuid import UUID


def is_uuid(value: str) -> bool:
    if value is None:
        return False
    try:
        UUID(value)
        return True
    except ValueError:
        return False


class Spinner:
    def __init__(self):
        self._chars = itertools.cycle(("|", "/", "-", "\\"))
        self._stream = sys.stdout

    def __enter__(self):
        return self

    def update(self):
        self._stream.write("\b")
        self._stream.write(next(self._chars))
        self._stream.flush()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.write("\b")
        self._stream.flush()
