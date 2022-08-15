from ..api import request
from ..context import ctx
from ..objects.tg_methods import DeleteMessage


def delete_message(
        message_id: int = None,
        chat_id: int | str = None,
) -> bool:
    return request(
        DeleteMessage,
        locals(),
        message_id=ctx.message_id,
        chat_id=ctx.chat_id,
    )
