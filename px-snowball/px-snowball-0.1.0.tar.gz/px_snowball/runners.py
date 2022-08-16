from threading import Timer
from typing import Callable, Optional

from .storages import Storage


__all__ = 'Runner', 'ThreadingDaemonRunner',


class Runner:
    delay: float = None
    clear_on_execute: bool = True
    is_running: bool = False

    def __init__(
        self,
        storage: Storage,
        delay: Optional[float] = None,
        clear_on_execute: Optional[bool] = None,
    ):
        self.storage = storage
        self.delay = (
            delay if delay is not None
            else self.delay
        )
        self.clear_on_execute = (
            clear_on_execute if clear_on_execute is not None
            else self.clear_on_execute
        )

        assert self.delay is not None, 'Delay must not be empty.'

    def execute(self, callback: Callable, kwargs: dict):
        values = self.storage.get()

        if kwargs.get('clear_on_execute', False) or self.clear_on_execute:
            self.storage.clear()

        self.is_running = False

        return callback(values)

    def cancel(self):
        raise NotImplementedError()

    def run(self, callback: Callable, **kwargs):
        raise NotImplementedError()


class ThreadingDaemonRunner(Runner):
    timer: Timer

    def run(self, callback: Callable, **kwargs):
        self.timer = Timer(
            self.delay,
            self.execute,
            args=(callback, kwargs),
        )
        self.timer.setDaemon(True)
        self.timer.start()
        # TODO: Manually setting state here could be dangerous.
        # Should be checked.
        self.is_running = True

    def cancel(self):
        self.is_running = False

        if hasattr(self, 'timer'):
            self.timer.cancel()
