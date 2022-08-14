#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""CLI command processing for ``build-harness`` command."""

import pathlib
import sys

import click

from build_harness._version import acquire_version

from ._declarations import (
    DEFAULT_CONSOLE_LOGGING_ENABLED,
    DEFAULT_FILE_LOGGING_DISABLED,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PROJECT_PATH,
    VALID_LOG_LEVELS,
)
from ._logging import LoggingState
from .analysis import static_analysis
from .bdd import bdd_acceptance_command
from .bootstrap import bootstrap
from .code_style import formatting
from .dependencies import install
from .publishing import publish
from .state import CommandState
from .unit_tests import unit_test
from .wheel import package


@click.group()
@click.pass_context
@click.version_option(version=acquire_version())
@click.option(
    "--log-enable-console",
    "enable_console_log",
    default=DEFAULT_CONSOLE_LOGGING_ENABLED,
    help="Log to console.",
    is_flag=True,
)
@click.option(
    "--log-disable-file",
    "disable_file_log",
    default=DEFAULT_FILE_LOGGING_DISABLED,
    help="Disable file logging.",
    is_flag=True,
)
@click.option(
    "--log-level",
    "log_level",
    default=DEFAULT_LOG_LEVEL,
    help="Select logging level to apply to all enabled log sinks.",
    type=click.Choice(VALID_LOG_LEVELS, case_sensitive=False),
)
def main(
    ctx: click.Context,
    disable_file_log: bool,
    enable_console_log: bool,
    log_level: str,
) -> None:
    """Build harness group."""
    logging_state = LoggingState(
        disable_file_logging=disable_file_log,
        enable_console_logging=enable_console_log,
        log_level_text=log_level,
    )
    ctx.obj = CommandState(
        logging_state=logging_state,
        project_path=pathlib.Path(DEFAULT_PROJECT_PATH),
        venv_path=pathlib.Path(sys.argv[0]).parent.absolute(),
    )


main.add_command(bdd_acceptance_command, name="acceptance")
main.add_command(bootstrap, name="bootstrap")
main.add_command(formatting, name="formatting")
main.add_command(install, name="install")
main.add_command(package, name="package")
main.add_command(publish, name="publish")
main.add_command(static_analysis, name="static-analysis")
main.add_command(unit_test, name="unit-test")
