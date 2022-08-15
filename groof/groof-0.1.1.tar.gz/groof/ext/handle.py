from typing import Callable

Handler = Callable[[], ...]
Decorator = Callable[[Handler], ...]


def handle(event: Decorator, callback: Handler):
    event(callback)
