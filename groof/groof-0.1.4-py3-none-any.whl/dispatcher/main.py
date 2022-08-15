from typing import Callable, Any

import groof

Handler = Callable[[], Any]
Decorator = Callable[[Handler], Any]


class Dispatcher:

    @staticmethod
    def handle(event: Decorator, callback: Handler):
        event(callback)

    @staticmethod
    def run(
            skip_updates: bool = False,
            parse_mode: str = None,
            disable_web_page_preview: bool = None,
            disable_notification: bool = None,
            protect_content: bool = None,
    ):
        groof.run(skip_updates, parse_mode, disable_web_page_preview, disable_notification, protect_content)
