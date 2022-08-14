#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Common constants for command definitions."""

import enum

DEFAULT_PROJECT_PATH = "."

DEFAULT_CONSOLE_LOGGING_ENABLED = False
DEFAULT_FILE_LOGGING_DISABLED = False
DEFAULT_FILE_ROTATION_BACKUPS = 10
DEFAULT_FILE_ROTATION_ENABLED = True
DEFAULT_FILE_ROTATION_SIZE_MB = 1
DEFAULT_LOG_FILE = "build_harness.log"

DEFAULT_LOG_LEVEL = "warning"
VALID_LOG_LEVELS = ["critical", "error", "warning", "info", "debug", "notset"]


@enum.unique
class PublishOptions(enum.Enum):
    """Enumeration of artifact publish options."""

    yes = enum.auto()
    no = enum.auto()
    dryrun = enum.auto()
    test = enum.auto()
