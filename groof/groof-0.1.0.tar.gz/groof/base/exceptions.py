from dataclasses import dataclass


@dataclass
class Error(Exception):
    def __str__(self):
        return repr(self)


@dataclass
class RequestError(Error):
    error_code: int
    description: str
    params: dict
    files: dict | None


class ExitHandler(Exception):
    pass


class StopProcessing(Exception):
    pass
