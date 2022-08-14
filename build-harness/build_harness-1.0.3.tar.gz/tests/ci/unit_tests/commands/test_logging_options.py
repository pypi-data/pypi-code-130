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

import pytest
from click.testing import CliRunner

import build_harness.commands._logging
import build_harness.commands.build_harness_group
from build_harness.commands import main
from build_harness.commands._declarations import VALID_LOG_LEVELS
from tests.ci.support.click_runner import click_runner  # noqa: F401


@pytest.fixture()
def mock_code_style(mocker):
    mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
    mock_isort_result.returncode = 0
    mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
    mock_black_result.returncode = 0
    mocker.patch(
        "build_harness.commands.code_style.run_command",
        side_effect=[mock_isort_result, mock_black_result],
    )
    build_harness.commands.build_harness_group.sys.argv = [
        "/some/test_logging_options/path/build-harness"
    ]


@pytest.fixture()
def mock_command_state(mocker):
    mocker.patch(
        "build_harness.commands._logging.logging.handlers.RotatingFileHandler"
    )
    mocker.patch.object(build_harness.commands._logging.logging, "getLogger")
    this_command_state = mocker.patch(
        "build_harness.commands.build_harness_group.CommandState"
    )

    return this_command_state


def test_default_logging(click_runner, mock_code_style, mock_command_state):
    result = click_runner.invoke(main, ["formatting"])
    assert result.exit_code == 0

    mock_command_state.assert_called_once()
    # assume only kwargs are used in the call
    call_args = mock_command_state.call_args_list[0].kwargs
    assert not call_args["logging_state"].configuration.disable_file_logging
    assert not call_args["logging_state"].configuration.enable_console_logging
    assert call_args["logging_state"].configuration.log_level == logging.WARNING


def test_enable_console_logging(
    click_runner, mock_code_style, mock_command_state
):
    result = click_runner.invoke(main, ["--log-enable-console", "formatting"])
    assert result.exit_code == 0

    mock_command_state.assert_called_once()
    # assume only kwargs are used in the call
    call_args = mock_command_state.call_args_list[0].kwargs
    assert not call_args["logging_state"].configuration.disable_file_logging
    assert call_args["logging_state"].configuration.enable_console_logging
    assert call_args["logging_state"].configuration.log_level == logging.WARNING


def test_disable_file_logging(
    click_runner, mock_code_style, mock_command_state
):
    result = click_runner.invoke(main, ["--log-disable-file", "formatting"])
    assert result.exit_code == 0

    mock_command_state.assert_called_once()
    # assume only kwargs are used in the call
    call_args = mock_command_state.call_args_list[0].kwargs
    assert call_args["logging_state"].configuration.disable_file_logging
    assert not call_args["logging_state"].configuration.enable_console_logging
    assert call_args["logging_state"].configuration.log_level == logging.WARNING


class TestLogLevel:
    def _do_test(self, this_level: str, mock_state):
        click_runner = CliRunner()
        result = click_runner.invoke(
            main, ["--log-level", this_level, "formatting"]
        )
        if result.exit_code != 0:
            pytest.fail("Valid log level failed test, {0}".format(this_level))

        mock_state.assert_called_once()
        # assume only kwargs are used in the call
        call_args = mock_state.call_args_list[0].kwargs
        assert call_args["logging_state"].configuration.log_level == getattr(
            logging, this_level.upper()
        )

    def test_critical(self, mock_code_style, mock_command_state):
        self._do_test("critical", mock_command_state)

    def test_error(self, mock_code_style, mock_command_state):
        self._do_test("error", mock_command_state)

    def test_warning(self, mock_code_style, mock_command_state):
        self._do_test("warning", mock_command_state)

    def test_info(self, mock_code_style, mock_command_state):
        self._do_test("info", mock_command_state)

    def test_debug(self, mock_code_style, mock_command_state):
        self._do_test("debug", mock_command_state)

    def test_notset(self, mock_code_style, mock_command_state):
        self._do_test("notset", mock_command_state)

    def test_bad_level(self, click_runner, mock_code_style, mock_command_state):
        result = click_runner.invoke(
            main, ["--log-level", "bad_level", "formatting"]
        )
        assert result.exit_code != 0

    def test_mixed_case(
        self, click_runner, mock_code_style, mock_command_state
    ):
        result = click_runner.invoke(
            main, ["--log-level", "Debug", "formatting"]
        )
        assert result.exit_code == 0

        mock_command_state.assert_called_once()
        # assume only kwargs are used in the call
        call_args = mock_command_state.call_args_list[0].kwargs
        assert (
            call_args["logging_state"].configuration.log_level == logging.DEBUG
        )

    def test_upper_case(
        self, click_runner, mock_code_style, mock_command_state
    ):
        result = click_runner.invoke(
            main, ["--log-level", "DEBUG", "formatting"]
        )
        assert result.exit_code == 0

        mock_command_state.assert_called_once()
        # assume only kwargs are used in the call
        call_args = mock_command_state.call_args_list[0].kwargs
        assert (
            call_args["logging_state"].configuration.log_level == logging.DEBUG
        )
