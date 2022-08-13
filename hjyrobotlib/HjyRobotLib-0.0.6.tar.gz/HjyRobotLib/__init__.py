"""Main library."""

from robotlibcore import DynamicCore, keyword

from HjyRobotLib.mystuff import Library1, Library2


class HjyRobotLib(DynamicCore):
    """General library documentation."""

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
