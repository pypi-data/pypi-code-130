#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import logging
import subprocess
import typing

log = logging.getLogger(__name__)

CommandArgs = typing.List[str]


def run_command(
    command: CommandArgs, **kwargs: typing.Any
) -> subprocess.CompletedProcess:
    """
    Run a system command using ``subprocess.run``.

    Args:
        command: List of command and arguments.
        **kwargs: Optional arguments passed through to ``subprocess.run``.

    Returns:
        Subprocess results.
    """
    log.debug("command to run, {0}".format(str(command)))
    log.debug("command arguments, {0}".format(str(kwargs)))
    result = subprocess.run(command, **kwargs)

    return result


def run_command_sequence(sequence: typing.List[str]) -> None:
    """
    Run through a shell command sequence.

    Args:
        sequence: List of commands to be executed.
    """
    for this_command in sequence:
        response = run_command(this_command.split())


def init_git(default_branch_name: str) -> None:
    """
    Initialize git repo in the new project directory.

    Args:
        default_branch_name: Name of default git branch.
    """
    commands = [
        "git init",
        "git checkout -b {0}".format(default_branch_name),
    ]
    run_command_sequence(commands)


def commit_initial_files() -> None:
    """Commit initial set of file from template to source control."""
    # Generated files typically need reformatting to comply with PEP-8 formatting.
    commands = [
        "{{ cookiecutter._venv_bin }}/build-harness install",
        "{{ cookiecutter._venv_bin }}/build-harness formatting",
        "{{ cookiecutter._venv_bin }}/pre-commit install --install-hooks",
        "git add .",
    ]
    run_command_sequence(commands)
    # .split() is too crude for the whitespace containing argument here, so just use
    # `run_command` directly.
    run_command(["git","commit", "-m", "Initial files from template"])


def main() -> None:
    default_branch_name = "{{ cookiecutter.default_branch }}"

    init_git(default_branch_name)
    commit_initial_files()


if __name__ == "__main__":
    main()
