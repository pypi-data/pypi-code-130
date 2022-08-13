"""Main library."""
from robotlibcore import DynamicCore
from HjyRobotLib.mystuff import Library1, Library2
from robot.api.deco import keyword

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


def hello_world():
    print("hello world")
    return "hello world"


if __name__ == '__main__':
    hello_world()
    pass
