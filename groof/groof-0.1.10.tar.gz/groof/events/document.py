from .base import HandlerOld
from .. import filters


def document(
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    _filters = [
        filters.Document(),
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
