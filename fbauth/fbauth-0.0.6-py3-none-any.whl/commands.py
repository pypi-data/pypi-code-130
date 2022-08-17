# -*- coding: utf-8 -*-
"""
    Custom - Command-Line-Group
"""
# Settings

import os
import pathlib
import shutil

import click
from alembic import command
from alembic.config import Config
from fastberry import Fastberry, coro

from .actions.users import User

SETTINGS = Fastberry()

CURRENT_DIR = pathlib.Path(__file__).parents[0]
CONFIG_PATH = CURRENT_DIR / "alembic.ini"
SCRIPT_PATH = CURRENT_DIR / "migrations"


def init_alembic():
    """Init Alembic Config"""
    alembic_cfg = Config(CONFIG_PATH)
    alembic_cfg.set_main_option("script_location", str(SCRIPT_PATH))
    return alembic_cfg


# Init Group
@click.group()
def cli():
    """Click (CLI) Group"""


@click.group()
def users():
    """Users' Database Migrations Commands"""


ALEMBIC_CONFIG = init_alembic()


@users.command()
@click.option("-m", "--message", help="Migration message.", type=str, default=None)
def make_migrations(message):
    """Database Make-Migrations."""
    command.revision(ALEMBIC_CONFIG, message=message, autogenerate=True)


@users.command()
def migrate():
    """Database Migrate."""
    command.upgrade(ALEMBIC_CONFIG, "head")


@users.command()
@click.option("-m", "--message", help="Migration message.", type=str, default=None)
def auto_migrate(message):
    """Database Make-Migrations & Migrate."""
    # Make-Migrations
    command.revision(ALEMBIC_CONFIG, message=message, autogenerate=True)
    # Migrate
    command.upgrade(ALEMBIC_CONFIG, "head")


@users.command()
@click.argument("revision", type=str)
def upgrade(revision):
    """Database Migrate (Upgrade)."""
    command.upgrade(ALEMBIC_CONFIG, revision)


@users.command()
@click.argument("revision", type=str)
def downgrade(revision):
    """Database Migrate (Downgrade)."""
    command.downgrade(ALEMBIC_CONFIG, revision)


@users.command()
def history():
    """Database Migrations History."""
    command.history(ALEMBIC_CONFIG)


@users.command()
def reset():
    """Database Delete Migrations (All-Versions)."""
    dir_path = CURRENT_DIR / "migrations" / "versions"
    # Delete
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print(f"Error: {dir_path} : {e.strerror}")
    # Recreate
    os.makedirs(dir_path)
    with open(dir_path / "README", "w") as f:
        f.write("Database Migrations Versions")
    click.secho(
        f"Successfully Delete All-Migrations", fg="bright_green"
    )


# Register User's Commands
cli.add_command(users)


@cli.command()
@click.option(
    "-u",
    "--username",
    help="Account's Username.",
    type=str,
    default=None,
    required=True,
)
@click.option(
    "-p",
    "--password",
    help="Account's Password.",
    type=str,
    default=None,
    required=True,
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
)
@click.option(
    "-e", "--email", help="Account's Email.", type=str, default=None, required=True
)
@coro
async def create_super_user(username, password, email):
    """Create a Super-User Account."""
    results = await User.create(
        username=username, password=password, email=email, is_super_user=True, role_id=0
    )
    if not results.error:
        click.secho(
            f"<{results.data.username}> Created Successfully", fg="bright_green"
        )
    else:
        click.secho(f"ERROR:\n\t{results.error_message}", fg="bright_red")
