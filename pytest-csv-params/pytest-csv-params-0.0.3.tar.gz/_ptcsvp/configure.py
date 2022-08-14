"""
Pytest Plugin Configuration
"""

from _ptcsvp.plugin import Plugin


def pytest_configure(config, plugin_name="csv_params"):
    """
    Register our Plugin
    """
    config.pluginmanager.register(Plugin(config), f"{plugin_name}_plugin")


def pytest_unconfigure(config, plugin_name="csv_params"):
    """
    Remove our Plugin
    """
    config.pluginmanager.unregister(f"{plugin_name}_plugin")
