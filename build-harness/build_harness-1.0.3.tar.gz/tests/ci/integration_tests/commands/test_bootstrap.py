#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import logging
import os
import pathlib
import typing

from build_harness.commands import main
from tests.ci.support.click_runner import click_runner  # noqa: F401
from tests.ci.support.project_context import (
    build_cookiecutter_context,
    make_project_venv,
)

log = logging.getLogger(__name__)


@contextlib.contextmanager
def managed_dependencies(
    project_name: str,
) -> typing.Generator[pathlib.Path, None, None]:
    cwd = pathlib.Path.cwd()
    with build_cookiecutter_context() as this_context:
        make_project_venv(project_name, this_context.temp_path)
        os.chdir(this_context.temp_path)
        yield

    os.chdir(cwd)


class TestBootstrap:
    PROJECT_NAME = "my_new_project"
    COMMAND_BASE = ["bootstrap", "--disable-dependencies", "my_new_project"]

    def test_default(self, click_runner):
        with managed_dependencies(self.PROJECT_NAME):
            result = click_runner.invoke(main, self.COMMAND_BASE.copy())

            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0
            assert pathlib.Path("my_new_project").is_dir()

    def test_ci(self, click_runner):
        with managed_dependencies(self.PROJECT_NAME):
            result = click_runner.invoke(
                main, (self.COMMAND_BASE.copy() + ["--ci", "gitlabci"])
            )

            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0
            assert pathlib.Path("my_new_project").is_dir()

    def test_packager(self, click_runner):
        with managed_dependencies(self.PROJECT_NAME):
            result = click_runner.invoke(
                main, (self.COMMAND_BASE.copy() + ["--packager", "flit"])
            )

            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0
            assert pathlib.Path("my_new_project").is_dir()

    def test_default_branch(self, click_runner):
        with click_runner.isolated_filesystem():
            result = click_runner.invoke(
                main, (self.COMMAND_BASE.copy() + ["--default-branch", "fancy"])
            )

            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0
            assert pathlib.Path("my_new_project").is_dir()

    def test_force(self, click_runner):
        with managed_dependencies(self.PROJECT_NAME):
            result = click_runner.invoke(
                main, (self.COMMAND_BASE.copy() + ["--force"])
            )

            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0
            assert pathlib.Path("my_new_project").is_dir()
