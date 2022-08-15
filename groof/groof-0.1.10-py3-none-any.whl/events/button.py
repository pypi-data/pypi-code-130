from .base import HandlerOld
from .. import filters
from ..objects import CallbackButton


def button(
        value: CallbackButton | str | list[str],
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    _filters = [
        filters.Button(value),
        filters.State(state),
    ]

    if user_id:
        _filters.append(filters.UserId(user_id))

    if chat_type:
        _filters.append(filters.ChatType(chat_type))

    def _(func):
        if isinstance(func, HandlerOld):
            func = func.func

        handler = HandlerOld(func, _filters)
        return handler

    return _
