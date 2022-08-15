from ..api import request
from ..objects import BotCommand, BotCommandScope
from ..objects.tg_methods import AnswerCallbackQuery
from ..context import ctx


def answer_callback_query(
        text: str = None,
        show_alert: bool = None,

        callback_query_id: str = None,

        url: str = None,
        cache_time: int = None,
) -> bool:
    return request(
        AnswerCallbackQuery,
        locals(),
        callback_query_id=ctx.callback_query_id,
    )
