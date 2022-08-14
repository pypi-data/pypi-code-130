#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import logging
import pathlib
import typing

import pytest

from build_harness.commands._declarations import (
    DEFAULT_LOG_FILE,
    VALID_LOG_LEVELS,
)
from build_harness.commands._logging import LoggingState
from tests.ci.support.captured_io import capture_io
from tests.ci.support.directory import change_directory


class TestLoggingState:
    def test_disable_console_logging(self):
        arguments = {
            "disable_file_logging": True,
            "enable_console_logging": False,
            "log_level_text": "warning",
        }
        captured_err, captured_out, _ = self._do_test(arguments)

        assert not captured_err
        assert not captured_out

    def _do_test(
        self, arguments: dict
    ) -> typing.Tuple[str, str, typing.Optional[str]]:
        with capture_io() as captured, change_directory() as temp_dir:
            expected_log_file: pathlib.Path = temp_dir / "build_harness.log"
            under_test = LoggingState(**arguments)

            log = logging.getLogger("MockLogging")
            log.debug("debug message")
            log.info("info message")
            log.warning("warning message")
            log.error("error message")
            log.critical("critical message")

            assert (
                under_test.configuration.disable_file_logging
                == arguments["disable_file_logging"]
            )
            assert (
                under_test.configuration.enable_console_logging
                == arguments["enable_console_logging"]
            )
            assert under_test.configuration.log_level == getattr(
                logging, arguments["log_level_text"].upper()
            )

            if arguments["disable_file_logging"]:
                assert under_test.configuration.log_file_path is None
                assert not expected_log_file.exists()

                file_contents = None
            else:
                assert under_test.configuration.log_file_path == pathlib.Path(
                    DEFAULT_LOG_FILE
                )
                assert expected_log_file.is_file()

                with expected_log_file.open("r") as f:
                    file_contents = f.read()

            captured.err.seek(0)
            captured.out.seek(0)

            captured_err = captured.err.read()
            captured_out = captured.out.read()

        return captured_err, captured_out, file_contents

    def test_enable_console_logging(self):
        arguments = {
            "disable_file_logging": True,
            "enable_console_logging": True,
            "log_level_text": "warning",
        }
        captured_err, captured_out, _ = self._do_test(arguments)

        assert not captured_out
        assert "debug" not in captured_err
        assert "info" not in captured_err
        assert "warning message" in captured_err
        assert "error message" in captured_err
        assert "critical message" in captured_err

    def test_disable_file_logging(self):
        arguments = {
            "disable_file_logging": True,
            "enable_console_logging": False,
            "log_level_text": "warning",
        }
        captured_err, captured_out, _ = self._do_test(arguments)

        assert not captured_err
        assert not captured_out

    def test_enable_file_logging(self):
        arguments = {
            "disable_file_logging": False,
            "enable_console_logging": False,
            "log_level_text": "warning",
        }
        captured_err, captured_out, file_contents = self._do_test(arguments)

        assert not captured_err
        assert not captured_out

        assert "debug" not in file_contents
        assert "info" not in file_contents
        assert "warning message" in file_contents
        assert "error message" in file_contents
        assert "critical message" in file_contents

    def test_enable_both_file_console(self):
        arguments = {
            "disable_file_logging": False,
            "enable_console_logging": True,
            "log_level_text": "warning",
        }
        captured_err, captured_out, file_contents = self._do_test(arguments)

        assert "debug" not in captured_err
        assert "info" not in captured_err
        assert "warning message" in captured_err
        assert "error message" in captured_err
        assert "critical message" in captured_err

        assert "debug" not in file_contents
        assert "info" not in file_contents
        assert "warning message" in file_contents
        assert "error message" in file_contents
        assert "critical message" in file_contents

    def test_log_levels(self):
        for this_level in VALID_LOG_LEVELS:
            arguments = {
                "disable_file_logging": True,
                "enable_console_logging": True,
                "log_level_text": this_level,
            }
            captured_err, captured_out, _ = self._do_test(arguments)

            if captured_out:
                pytest.fail("Captured stdout should be empty")

            if this_level != "notset":
                expected_level = this_level.upper()
                if (expected_level not in captured_err) and (
                    "{0} message".format(expected_level.lower())
                    not in captured_err
                ):
                    pytest.fail(
                        "Log level {0} not present in captured stderr, "
                        "{1}".format(
                            expected_level,
                            captured_err if captured_err else "<empty>",
                        )
                    )
            else:
                # notset enables logging at all levels
                for log_level in VALID_LOG_LEVELS:
                    if log_level != "notset":
                        assert "{0} message".format(log_level) in captured_err
