def a(text, url) -> str:
    return f'<a href="{url}">{text}</a>'


def b(text) -> str:
    return f'<b>{text}</b>'


def spoiler(text) -> str:
    return f'<tg-spoiler>{text}</tg-spoiler>'


def code(text) -> str:
    return f'<code>{text}</code>'
