"""
The main Plugin implementation
"""

from _pytest.config import Config

BASE_DIR_KEY = "__pytest_csv_plugins__config__base_dir"


class Plugin:  # pylint: disable=too-few-public-methods
    """
    Plugin Class
    """

    def __init__(self, config: Config) -> None:
        """
        Hold the pytest config
        """
        setattr(Plugin, BASE_DIR_KEY, config.option.csv_params_base_dir)
