import sys
import subprocess
import time
import win32gui

from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea, QPushButton
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.mdi = QMdiArea()
        self.widget = QWidget()
        self.init_uI()

    def start_wx(self):
        hwnd1 = win32gui.FindWindowEx(0, 0, "WeChatLoginWndForPC", u"微信")
        if hwnd1 is not 0:
            window = QWindow.fromWinId(hwnd1)
            embed_widget = self.createWindowContainer(window, self)
            self.setWidget(embed_widget)
        else:
            print("没有检查到微信")

    def init_uI(self):
        self.start_wx()
        self.setGeometry(0, 0, 1920, 1200)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
