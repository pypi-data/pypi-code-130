from ..api import request
from ..context import ctx
from ..objects import Chat
from ..objects.tg_methods import GetChat


def get_chat(
        chat_id: int | str = None,
) -> Chat:
    return request(
        GetChat,
        locals(),
        chat_id=ctx.chat_id,
    )
