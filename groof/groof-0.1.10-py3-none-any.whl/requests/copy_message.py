from .base import ReplyMarkupT
from ..api import request
from ..context import ctx
from ..objects import MessageEntity, MessageId
from ..objects.tg_methods import CopyMessage


def copy_message(
        reply_markup: ReplyMarkupT = None,
        caption: str = None,

        chat_id: int | str = None,
        from_chat_id: int | str = None,
        message_id: int = None,
        parse_mode: str = None,
        disable_notification: bool = None,
        protect_content: bool = None,

        reply_to_message_id: int = None,
        caption_entities: list[MessageEntity] = None,
        allow_sending_without_reply: bool = None,
) -> MessageId:
    return request(
        CopyMessage,
        locals(),
        chat_id=ctx.chat_id,
        from_chat_id=ctx.chat_id,
        message_id=ctx.message_id,
        parse_mode=ctx.parse_mode,
        disable_notification=ctx.disable_notification,
        protect_content=ctx.protect_content,
    )
