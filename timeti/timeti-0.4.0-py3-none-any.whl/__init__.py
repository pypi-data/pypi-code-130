"""
serializer elapsed time of functions, loops and code blocks.

Copyright 2022 Ilia Lazarev
"""

__all__ = ["Stopwatch", "Clockface", "timing", "totime", "timer"]

from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional

from timeti.clockface import Clockface
from timeti.stopwatch import Stopwatch


class profiler:
    def __init__(
        self,
        something: Any = None,
        /,
        name: str = None,
        *,
        verbose: bool = True,
        serializer: Callable = None,
        ret_sw: bool = False,
    ):
        self._something: Any = something
        self._name: Optional[str] = name
        self._verbose: bool = verbose
        self._serializer = serializer
        self._iter: Optional[int] = None
        self._ret_sw: bool = ret_sw
        self._sw: Stopwatch = Stopwatch()

    @property
    def stopwatch(self):
        return self._sw

    @property
    def sw(self):
        return self._sw

    def __enter__(self):
        if self._name is None and isinstance(self._something, str):
            self._name = self._something
            self._something = None
        self._sw.reset()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._sw.pause()
        self._ctxm_serializer()

    def __iter__(self):
        if self._something is None:
            raise ValueError("something is not provided")
        self._sw.reset()
        for self._iter, item in enumerate(self._something):
            yield (self._sw, item) if self._ret_sw else item
            self._sw.lap()
            with self._sw.paused():
                self._loop_serializer()

        self._sw.pause()
        self._iter = None
        self._loop_serializer()

    def __call__(self, *args, **kwargs):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self._sw.reset()
                out = func(*args, **kwargs)
                self._sw.pause()
                self._func_serializer()
                return out

            return wrapper

        if self._something is not None:
            if not isinstance(self._something, str):
                func = self._something
                self._name = func.__name__
                return decorator(func)(*args, **kwargs)
            else:
                self._name = self._something
                self._something = None

        func = args[0]
        self._name = self._name or func.__name__
        return decorator(func)

    @property
    def _mention(self):
        return "" if self._name is None else f" '{self._name}'"

    def _func_serializer(self):
        if self._verbose:
            if self._serializer is None:
                print(f"Elapsed time of{self._mention} function: {self._sw.clockface}")
            else:
                self._serializer(self._sw, name=self._name, verbose=self._verbose)

    def _ctxm_serializer(self):
        if self._verbose:
            if self._serializer is None:
                print(f"Elapsed time of{self._mention} block: {self._sw.clockface}")
            else:
                self._serializer(self._sw, name=self._name, verbose=self._verbose)

    def _loop_serializer(self):
        if self._verbose:
            if self._serializer is None:
                if self._iter is not None:
                    lap = self._sw.laps[-1]
                    print(f"Elapsed time of{self._mention} loop iteration {self._iter}: {lap}")
                else:
                    print(f"Elapsed time of{self._mention} loop: {self._sw.clockface}")
            else:
                self._serializer(self._sw, name=self._name, i=self._iter, verbose=self._verbose)
