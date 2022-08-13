"""Main library."""
from robotlibcore import DynamicCore, keyword
from .mystuff import Library1, Library2

__version__ = "0.0.1"


class HjyRobotLib(DynamicCore):
    """General library documentation."""
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        libraries = [Library1(), Library2()]
        DynamicCore.__init__(self, libraries)

    @keyword
    def keyword_in_main(self):
        pass

