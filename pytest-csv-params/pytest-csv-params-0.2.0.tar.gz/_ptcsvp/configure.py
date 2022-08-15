"""
Pytest Plugin Configuration
"""
from _pytest.config import Config

from _ptcsvp.plugin import Plugin


def pytest_configure(config: Config, plugin_name: str = "csv_params") -> None:
    """
    Register our Plugin
    """
    config.pluginmanager.register(Plugin(config), f"{plugin_name}_plugin")


def pytest_unconfigure(config: Config, plugin_name: str = "csv_params") -> None:
    """
    Remove our Plugin
    """
    config.pluginmanager.unregister(f"{plugin_name}_plugin")
