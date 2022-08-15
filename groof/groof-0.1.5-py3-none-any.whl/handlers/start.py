from .command import command


def start(
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    return command('start', user_id, chat_type, state)
