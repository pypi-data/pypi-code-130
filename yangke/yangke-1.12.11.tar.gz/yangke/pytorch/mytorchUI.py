from yangke.common.config import logger
from yangke.common.qt import YkWindow, run_app


class MainWindow(YkWindow):
    def __init__(self):
        super(MainWindow, self).__init__()


run_app(MainWindow)
