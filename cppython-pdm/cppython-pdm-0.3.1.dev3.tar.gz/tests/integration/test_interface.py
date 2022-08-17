"""
TODO
"""
from typing import Type

import pytest
from pdm.core import Core
from pytest_cppython.plugin import InterfaceIntegrationTests
from pytest_mock import MockerFixture

from cppython_pdm.plugin import CPPythonPlugin


class TestCPPythonInterface(InterfaceIntegrationTests[CPPythonPlugin]):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="interface_type")
    def fixture_interface_type(self) -> Type[CPPythonPlugin]:
        """
        A required testing hook that allows type generation
        """
        return CPPythonPlugin

    def test_entrypoint(self, mocker: MockerFixture):
        """
        Verify that this project's plugin hook is setup correctly
        """

        patch = mocker.patch("cppython_pdm.plugin.CPPythonPlugin")

        core = Core()
        core.load_plugins()

        assert patch.called
