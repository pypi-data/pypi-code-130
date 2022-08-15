from ..context import ctx
from ..api import request
from ..objects import ChatMemberT
from ..objects.tg_methods import GetChatMember


def get_chat_member(
        chat_id: int | str = None,
        user_id: int = None,
) -> ChatMemberT:
    return request(
        GetChatMember,
        locals(),
        chat_id=ctx.chat_id,
        user_id=ctx.user_id,
    )
