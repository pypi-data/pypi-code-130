from ..api import request
from ..objects import BotCommand, BotCommandScope
from ..objects.tg_methods import SetMyCommands


def set_my_commands(
        commands: list[BotCommand],
        scope: BotCommandScope = None,
        language_code: str = None,
) -> bool:
    return request(
        SetMyCommands,
        locals(),
    )
