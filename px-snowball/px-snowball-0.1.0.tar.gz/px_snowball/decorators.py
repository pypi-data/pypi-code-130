from .storages import InMemStorage
from .runners import ThreadingDaemonRunner
from .wrappers import Throttle, Debounce


__all__ = 'thread_throttle', 'thread_debounce', 'throttle', 'debounce',


def thread_throttle(delay: float):
    storage = InMemStorage()
    runner = ThreadingDaemonRunner(storage, delay=delay, clear_on_execute=True)

    return Throttle(storage, runner)


def thread_debounce(delay: float):
    storage = InMemStorage()
    runner = ThreadingDaemonRunner(storage, delay=delay, clear_on_execute=True)

    return Debounce(storage, runner)


throttle = thread_throttle
debounce = thread_debounce
