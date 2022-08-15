from ..api import request
from ..context import ctx
from ..objects import Message, InlineKeyboardMarkup, InlineKeyboard
from ..objects.tg_methods import EditMessageReplyMarkup


def edit_message_reply_markup(
        reply_markup: InlineKeyboardMarkup | InlineKeyboard = None,
        chat_id: int | str = None,
        message_id: int = None,
        inline_message_id: str = None,
) -> Message | bool:
    return request(
        EditMessageReplyMarkup,
        locals(),
        chat_id=ctx.chat_id,
        message_id=ctx.message_id,
    )
