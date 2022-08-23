import typing


class Timeout:
    def __init__(self, connect: float = None, read: float = None):
        self.connect_timeout = connect
        self.read_timeout = read

    @property
    def total(self) -> typing.Optional[float]:
        if self.connect_timeout is None and self.read_timeout is None:
            return None
        timeout = 0
        if self.connect_timeout is not None:
            timeout += self.connect_timeout
        if self.read_timeout is not None:
            timeout += self.read_timeout
        return timeout


DEFAULT_TIMEOUT = Timeout()
