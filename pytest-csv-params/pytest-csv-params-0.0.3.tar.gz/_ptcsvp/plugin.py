"""
The main Plugin implementation
"""


class Plugin:  # pylint: disable=too-few-public-methods
    """
    Plugin Class
    """

    def __init__(self, config):
        """
        Hold the pytest config
        """
        self.config = config
