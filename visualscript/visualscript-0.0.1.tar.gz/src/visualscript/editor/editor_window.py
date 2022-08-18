import os, sys, asyncio
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class VPWindow(QMainWindow):
    def __init__(self, file_paths=tuple()):
        self.file_paths = file_paths
        super().__init__()