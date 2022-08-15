from typing import Callable, Any

Handler = Callable[[], Any]
Decorator = Callable[[Handler], Any]


class Dispatcher:

    @staticmethod
    def handle(event: Decorator, callback: Handler):
        event(callback)
