from ..api import request
from ..objects import User
from ..objects.tg_methods import GetMe


def get_me() -> User:
    return request(
        GetMe,
        locals(),
    )
