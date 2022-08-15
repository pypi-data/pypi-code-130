from ..api import request
from ..context import ctx
from ..objects import Translations, MessageEntity, Message, InlineKeyboardMarkup, InlineKeyboard
from ..objects.tg_methods import EditMessageText


def edit_message_text(
        text: str | Translations,
        reply_markup: InlineKeyboardMarkup | InlineKeyboard = None,

        chat_id: int | str = None,
        message_id: int = None,
        inline_message_id: str = None,
        parse_mode: str = None,
        disable_web_page_preview: bool = None,

        entities: list[MessageEntity] = None,
) -> Message | bool:
    return request(
        EditMessageText,
        locals(),
        chat_id=ctx.chat_id,
        message_id=ctx.message_id,
        parse_mode=ctx.parse_mode,
        disable_web_page_preview=ctx.disable_web_page_preview,
    )
