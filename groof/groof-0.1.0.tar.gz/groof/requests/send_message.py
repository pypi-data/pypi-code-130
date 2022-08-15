from .base import ReplyMarkupT
from ..api import request
from ..context import ctx
from ..objects import Translations, MessageEntity, Message
from ..objects.tg_methods import SendMessage


def send_message(
        text: str | Translations,
        reply_markup: ReplyMarkupT = None,

        chat_id: int | str = None,
        parse_mode: str = None,
        disable_web_page_preview: bool = None,
        disable_notification: bool = None,
        protect_content: bool = None,

        reply_to_message_id: int = None,
        entities: list[MessageEntity] = None,
        allow_sending_without_reply: bool = None,
) -> Message:
    return request(
        SendMessage,
        locals(),
        chat_id=ctx.chat_id,
        parse_mode=ctx.parse_mode,
        disable_web_page_preview=ctx.disable_web_page_preview,
        disable_notification=ctx.disable_notification,
        protect_content=ctx.protect_content,
    )
