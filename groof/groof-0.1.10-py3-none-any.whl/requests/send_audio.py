from .base import ReplyMarkupT
from ..api import request
from ..context import ctx
from ..objects import MessageEntity, Message, InputFile
from ..objects.tg_methods import SendAudio


def send_audio(
        audio: InputFile | str,
        reply_markup: ReplyMarkupT = None,

        chat_id: int | str = None,
        parse_mode: str = None,
        disable_notification: bool = None,
        protect_content: bool = None,

        caption: str = None,
        caption_entities: list[MessageEntity] = None,
        duration: int = None,
        performer: str = None,
        title: str = None,
        thumb: InputFile | str = None,
        reply_to_message_id: int = None,
        allow_sending_without_reply: bool = None,
) -> Message:
    return request(
        SendAudio,
        locals(),
        chat_id=ctx.chat_id,
        parse_mode=ctx.parse_mode,
        disable_notification=ctx.disable_notification,
        protect_content=ctx.protect_content,
    )
