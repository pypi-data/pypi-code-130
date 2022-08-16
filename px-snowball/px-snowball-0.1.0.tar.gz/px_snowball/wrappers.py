from .storages import Storage
from .runners import Runner


__all__ = 'Wrapper', 'Throttle', 'Debounce',


class Wrapper:
    storage: Storage
    runner: Runner

    def __init__(self, storage: Storage, runner: Runner):
        self.storage = storage
        self.runner = runner

    def wrapper(self, *args, **kwargs):
        self.storage.add((args, kwargs))
        result = self.runner.run(self.callback)

        return self, result

    def __call__(self, fn):
        self.callback = fn

        return self.wrapper


class Throttle(Wrapper):
    def wrapper(self, *args, **kwargs):
        self.storage.add((args, kwargs))

        if not self.runner.is_running:
            self.runner.run(self.callback)

        return self


class Debounce(Wrapper):
    def wrapper(self, *args, **kwargs):
        self.runner.cancel()

        self.storage.add((args, kwargs))
        self.runner.run(self.callback)

        return self
