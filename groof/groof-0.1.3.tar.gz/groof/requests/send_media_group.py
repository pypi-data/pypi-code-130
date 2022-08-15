from ..api import request
from ..context import ctx
from ..objects import Message, InputMediaDocument, InputMediaPhoto, InputMediaVideo, InputMediaAudio
from ..objects.tg_methods import SendMediaGroup


def send_media_group(
        media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo],

        chat_id: int | str = None,
        disable_notification: bool = None,
        protect_content: bool = None,

        reply_to_message_id: int = None,
        allow_sending_without_reply: bool = None,
) -> list[Message]:
    _locals = locals()

    for m in media:
        if m.caption_entities:
            m.parse_mode = None
        else:
            m.parse_mode = m.parse_mode or ctx.parse_mode

    return request(
        SendMediaGroup,
        _locals,
        chat_id=ctx.chat_id,
        disable_notification=ctx.disable_notification,
        protect_content=ctx.protect_content,
    )
