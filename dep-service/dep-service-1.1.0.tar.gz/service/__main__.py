"""Service commands."""

import fire

from spec.fn import execute

from .command.extra import ExtraCommands
from .command import uvicorn_run_service


class Command(ExtraCommands):
    """Service commands."""

    @staticmethod
    def run() -> None:
        """Run service."""
        uvicorn_run_service()

    @staticmethod
    def test() -> None:
        """Pytest runner."""
        execute(['poetry', 'run', 'pytest', '-v', '-vv', '-s'])


fire.Fire(Command)
