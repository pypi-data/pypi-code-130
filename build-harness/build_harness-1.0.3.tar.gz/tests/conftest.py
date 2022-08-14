#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pytest

import build_harness.commands.build_harness_group


@pytest.fixture
def mock_sysargv():
    build_harness.commands.build_harness_group.sys.argv = [
        "/some/conftest/path/build-harness"
    ]
