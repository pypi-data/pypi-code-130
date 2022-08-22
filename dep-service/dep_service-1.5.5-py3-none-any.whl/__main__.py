"""Service commands."""

import fire

from spec.service.command import CommandsMixin


class Command(CommandsMixin):
    """Service commands."""

    pass


fire.Fire(Command)
