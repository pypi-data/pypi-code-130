import abc
import sys
import time
import datetime
import threading
import urllib.parse

from .constants import *


class Serializable(abc.ABC):
    @abc.abstractmethod
    def to_json(self) -> str:
        """Convert instance to a JSON string"""
        raise NotImplementedError


class AsyncSpinner(threading.Thread):
    """
    Used to display a spinner while some other
    job is being processed in the background.
    """

    def __init__(self):
        super().__init__(target=self._spin)
        self._stopevent = threading.Event()

    def stop(self):
        self._stopevent.set()

    def _spin(self):
        while not self._stopevent.is_set():
            for char in "|/-\\":
                sys.stdout.write(f"[{char}]")
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write("\b" * 3)


def valid_url(url: str = DEFAULT_URL) -> str:
    result = urllib.parse.urlparse(url)
    if all([result.scheme, result.netloc]):
        return url
    else:
        sys.stderr.write(f"invalid URL: {url}")
        sys.exit(1)


def valid_date(date: str) -> str:
    try:
        return datetime.datetime.strptime(date, DATE_FORMAT).strftime(DATE_FORMAT)
    except ValueError:
        raise ValueError(f"invalid date format: expected {DATE_FORMAT}")


__all__ = ("valid_url", "AsyncSpinner", "Serializable", "valid_date")
