"""Primitive stopwatch."""
import time
import warnings
from contextlib import contextmanager
from typing import List

from .clockface import Clockface


class Stopwatch:
    """Primitive stopwatch."""

    def __init__(self):
        self._start_time: float = time.time()
        self._onpause = False
        self._laps: List[Clockface] = []
        self._pause_time: float = None

    def pause(self) -> Clockface:
        """Pause stopwatch."""
        if not self._onpause:
            self._onpause = True
            self._pause_time = time.time()
        else:
            warnings.warn("Stopwatch already paused")
        return Clockface(self._pause_time)

    @contextmanager
    def paused(self):
        """Pause stopwatch."""
        self.pause()
        yield self
        self.play()

    def play(self):
        """Continue stopwatch after a pause."""
        if self._onpause:
            self._start_time += time.time() - self._pause_time
            self._onpause = False

    def lap(self) -> Clockface:
        """Save time of lap."""
        self._laps.append(Clockface(self.timestamp - sum(self._laps, Clockface(0)).timestamp))
        if self._onpause:
            warnings.warn("Stopwatch paused")
        return self._laps[-1]

    @property
    def laps(self) -> List[Clockface]:
        """List of lap time span."""
        return self._laps

    def reset(self):
        """Reset stopwatch."""
        self.__init__()

    @property
    def timestamp(self) -> float:
        """Timestamp of stopwatch."""
        if self._onpause:
            return self._pause_time - self._start_time
        return time.time() - self._start_time

    @property
    def clockface(self) -> Clockface:
        """Clock face of stopwatch."""
        return Clockface(self.timestamp)

    def __str__(self):
        """Clock face as a string."""
        return str(self.clockface)

    def __repr__(self):
        """Summary of stopwatch."""
        return f"Stopwatch on {self.timestamp}"
