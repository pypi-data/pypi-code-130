"""Extra service commands."""

from spec.fn import create_locale_dot_gen, execute


class ExtraCommands(object):
    """Extra commands mixin."""

    @staticmethod
    def locale_gen() -> None:
        """Export locale.gen locales file from spec."""
        create_locale_dot_gen()

    @staticmethod
    def migrate():
        """Alembic migrate."""
        execute(['python', '-m', 'alembic', 'upgrade', 'head'])

    @staticmethod
    def make_migration(name: str):
        """Alembic make migration."""
        execute(['python', '-m', 'alembic', 'revision', '-m', name])

    @staticmethod
    def rollback(name: str):
        """Alembic rollback to exact revision."""
        execute(['python', '-m', 'alembic', 'downgrade', name])
