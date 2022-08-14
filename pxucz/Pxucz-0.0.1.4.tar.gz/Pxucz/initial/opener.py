import os
import sys
import threading
import time

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QCoreApplication

from Pxucz.initial.set_variables import INITIAL_LOADER_TEXT, INITIAL_LOADER_CLOSE
from Pxucz.utils import global_variables


class LoadingUI(QWidget):
    def __init__(self, size_x, size_y):
        super().__init__()
        self.size_x = size_x
        self.size_y = size_y
        self.loglabel = QLabel()
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.setLogLabelText())
        self.timer.setInterval(10)
        self.timer.start()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pxucz_Loader")
        self.resize(self.size_x, self.size_y)

        layout = QVBoxLayout()
        layout.addWidget(self.loglabel)
        self.setLayout(layout)

    def setLogLabelText(self):
        print(global_variables.get_var(INITIAL_LOADER_TEXT))
        if global_variables.get_var(INITIAL_LOADER_TEXT) == INITIAL_LOADER_CLOSE:
            self.close()
        self.loglabel.setText(global_variables.get_var(INITIAL_LOADER_TEXT))


global app, loaderThread, t


def window_shower(size_x: int, size_y: int):
    global app, t
    app = QApplication(sys.argv)
    loadingWin = LoadingUI(size_x=size_x, size_y=size_y)
    loadingWin.show()
    app.exec()
    sys.exit(0)


def start(size_x: int, size_y: int):
    global loaderThread, t
    t = threading.Thread(target=window_shower, args=(size_x, size_y))
    t.daemon = True
    t.start()
