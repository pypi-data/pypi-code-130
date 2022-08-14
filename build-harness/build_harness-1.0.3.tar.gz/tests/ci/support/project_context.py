#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import dataclasses
import io
import os
import pathlib
import sys
import tempfile
import typing

from build_harness._utility import run_command


@dataclasses.dataclass
class ProjectContext:
    repo_dir: pathlib.Path
    temp_path: pathlib.Path
    template_dir: pathlib.Path
    venv_bin: pathlib.Path
    venv_dir: pathlib.Path


@dataclasses.dataclass
class StdIo:
    out: io.IOBase
    err: io.IOBase


@dataclasses.dataclass()
class ProjectData:
    captured_io: StdIo
    file_contents: typing.Dict[str, typing.Optional[str]]
    project_name: str


@contextlib.contextmanager
def capture_stdout() -> typing.Generator[StdIo, None, None]:
    original_stdio = StdIo(out=sys.stdout, err=sys.stderr)
    try:
        captured_stdio = StdIo(out=io.StringIO(), err=io.StringIO())
        sys.stdout = captured_stdio.out
        sys.stderr = captured_stdio.err

        yield captured_stdio
    finally:
        sys.stdout = original_stdio.out
        sys.stderr = original_stdio.err


def _setup_context(this_dir: pathlib.Path) -> ProjectContext:
    repo_dir = pathlib.Path(__file__).parent / "../../.."
    template_dir = repo_dir / "build_harness/templates"

    temp_path = pathlib.Path(this_dir)
    venv_dir = temp_path / ".venv"
    venv_bin = temp_path / ".venv/bin"

    run_command(["python3", "-m", "venv", str(venv_dir)])
    run_command([str(venv_bin / "pip"), "install", "."])

    this_context = ProjectContext(
        temp_path=temp_path,
        repo_dir=repo_dir,
        template_dir=template_dir,
        venv_dir=venv_dir,
        venv_bin=venv_bin,
    )

    return this_context


@contextlib.contextmanager
def build_cookiecutter_context(
    working_dir: typing.Optional[pathlib.Path] = None,
) -> typing.Generator[ProjectContext, None, None]:
    if not working_dir:
        with tempfile.TemporaryDirectory() as this_dir:
            this_context = _setup_context(this_dir)
            yield this_context
    else:
        # use the specified path as the working directory
        working_context = _setup_context(working_dir)
        yield working_context


def make_project_venv(
    project_name: str, temp_path: pathlib.Path
) -> pathlib.Path:
    project_dir = temp_path / project_name
    project_venv = project_dir / ".venv"
    project_venv_bin = project_venv / "bin"

    # install this build_harness to acquire correct dependencies
    os.makedirs(str(project_dir), exist_ok=True)
    run_command(["python3", "-m", "venv", str(project_venv)])
    run_command([str(project_venv_bin / "pip"), "install", "."])

    return project_dir


@contextlib.contextmanager
def run_cookiecutter(
    run_context: dict, project_name: str
) -> typing.Generator[typing.Tuple[ProjectContext, StdIo], None, None]:
    with capture_stdout() as captured_stdio:
        # Need to do the import here to ensure that cookiecutter stdio is captured
        # correctly.
        from cookiecutter.main import cookiecutter

        with build_cookiecutter_context() as this_context:
            make_project_venv(project_name, this_context.temp_path)

            cookiecutter(
                str(this_context.template_dir),
                extra_context=run_context,
                no_input=True,
                replay=False,
                overwrite_if_exists=True,
                output_dir=this_context.temp_path,
            )

            yield this_context, captured_stdio
