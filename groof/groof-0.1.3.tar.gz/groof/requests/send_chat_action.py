from ..api import request
from ..context import ctx
from ..objects.tg_methods import SendChatAction


def send_chat_action(
        action: str,
        chat_id: int | str = None,
) -> bool:
    return request(
        SendChatAction,
        locals(),
        chat_id=ctx.chat_id,
    )
