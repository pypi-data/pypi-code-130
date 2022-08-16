from .commands import AppendCommand as append
from .commands import Command, Context
from .commands import DeleteCommand as delete
from .commands import GoToCommand as go_to
from .commands import GoToFirstLineCommand as go_to_first_line
from .commands import GoToLastLineCommand as go_to_last_line
from .commands import InsertCommand as insert
from .commands import InvalidOperation
from .commands import MoveCommand as move
from .commands import SearchCommand as search
from .commands import SubstituteCommand as substitute


def yaex(*commands: Command) -> str:
    context = Context(cursor=0, lines=[])
    for command in commands:
        context = command(context)
    return "".join(context.lines)


__all__ = [
    "Command",
    "Context",
    "InvalidOperation",
    "append",
    "delete",
    "go_to",
    "go_to_first_line",
    "go_to_last_line",
    "insert",
    "move",
    "search",
    "substitute",
    "yaex",
]
