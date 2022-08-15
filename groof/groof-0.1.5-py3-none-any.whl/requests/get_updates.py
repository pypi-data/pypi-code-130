from ..api import request
from ..objects import Update
from ..objects.tg_methods import GetUpdates


def get_updates(
        offset: int = None,
        limit: int = None,
        timeout: int = None,
        allowed_updates: list[str] = None,
) -> list[Update]:
    return request(
        GetUpdates,
        locals(),
    )
