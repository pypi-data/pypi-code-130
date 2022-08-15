import inspect
from threading import Thread
from typing import Callable, Any

import yaml

from ..base.exceptions import StopProcessing, ExitHandler
from ..base.user_model import UserModel
from ..base.user_proxy_model import UserProxyModel
from ..context import ctx
from ..events.base import Handler
from ..objects.tg_objects import Update
from ..requests.get_updates import get_updates
from ..utils import cast

Callback = Callable[..., Any]
Event = Callable[[Callback], Handler]


class Dispatcher:

    def __init__(self):
        from ..loader import logger

        self.handlers = []
        self.logger = logger

    def handle(self, event: Event, callback: Callback):
        handler = event(callback)
        self.handlers.append(handler)

    # ===

    def _notify_first_handlers(self):
        for handler in self.handlers:
            if not handler.check_first:
                continue

            for _filter in handler.filters:
                if not _filter():
                    break
            else:
                execute_handler(handler)

    def _notify_default_handlers(self):
        for handler in self.handlers:
            if handler.check_first or handler.check_last or handler.check_after_any:
                continue

            for _filter in handler.filters:
                if not _filter():
                    break
            else:
                execute_handler(handler)

    def _notify_last_handlers(self):
        for handler in self.handlers:
            if not handler.check_last:
                continue

            for _filter in handler.filters:
                if not _filter():
                    break
            else:
                execute_handler(handler)

    def _notify_after_any_handlers(self):
        for handler in self.handlers:
            if not handler.check_after_any:
                continue

            for _filter in handler.filters:
                if not _filter():
                    break
            else:
                execute_handler(handler)

    def _notify_handlers(self):
        try:
            self._notify_first_handlers()
            self._notify_default_handlers()
            self._notify_last_handlers()
        except StopProcessing:
            pass

        try:
            self._notify_after_any_handlers()
        except StopProcessing:
            pass

    def _process_update(self, update: Update) -> None:
        ctx.update = update
        self._notify_handlers()
        ctx.update = None

    def _process_updates(self, updates: list[Update]):
        for update in updates:
            Thread(target=lambda: self._process_update(update)).start()

            as_dict = cast(update, dict)
            as_string = yaml.dump(as_dict, allow_unicode=True, sort_keys=False)
            as_string = f'Update ->\n{as_string}'
            self.logger.info(as_string)

    def _start_polling(self, skip_updates: bool):
        offset = None

        if skip_updates:
            updates = get_updates(offset=offset)
            if updates:
                offset = updates[-1].update_id + 1

        while True:
            try:
                updates = get_updates(offset=offset)

                if updates:
                    offset = updates[-1].update_id + 1
                    self._process_updates(updates)
            except Exception as exc:
                self.logger.exception(exc)

    def run(
            self,
            skip_updates: bool = False,
            parse_mode: str = None,
            disable_web_page_preview: bool = None,
            disable_notification: bool = None,
            protect_content: bool = None,
    ):
        self.logger.info('Starting up...')

        ctx.parse_mode = parse_mode
        ctx.disable_web_page_preview = disable_web_page_preview
        ctx.disable_notification = disable_notification
        ctx.protect_content = protect_content

        try:
            self._start_polling(skip_updates)
        except KeyboardInterrupt:
            self.logger.info('Shutting down...')


# ===


def execute_handler(handler: Handler):
    func = handler.func
    kwargs: dict[str, UserProxyModel | UserModel] = {}

    for key, value in inspect.getfullargspec(func).annotations.items():
        if issubclass(value, UserProxyModel):
            kwargs[key] = value.get() or value()
        elif issubclass(value, UserModel):
            kwargs[key] = value.current() or value()

    try:
        func(**kwargs)
    except ExitHandler:
        pass

    for model in kwargs.values():
        if isinstance(model, UserProxyModel):
            model.save()
        elif isinstance(model, UserModel):
            model.save(as_current=True)

    if handler.exclusive:
        raise StopProcessing()
