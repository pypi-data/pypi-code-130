from ..api import request
from ..objects import BotCommandScope
from ..objects.tg_methods import DeleteMyCommands


def delete_my_commands(
        scope: BotCommandScope = None,
        language_code: str = None,
) -> bool:
    return request(
        DeleteMyCommands,
        locals(),
    )
