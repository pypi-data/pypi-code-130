from ..api import request
from ..context import ctx
from ..objects import InlineKeyboard, InlineKeyboardMarkup, MessageEntity, Message
from ..objects.tg_methods import EditMessageCaption


def edit_message_caption(
        caption: str = None,
        reply_markup: InlineKeyboard | InlineKeyboardMarkup = None,

        chat_id: int | str = None,
        message_id: int = None,
        inline_message_id: str = None,
        parse_mode: str = None,

        caption_entities: list[MessageEntity] = None,
) -> Message | bool:
    return request(
        EditMessageCaption,
        locals(),
        chat_id=ctx.chat_id,
        message_id=ctx.message_id,
        parse_mode=ctx.parse_mode,
    )
