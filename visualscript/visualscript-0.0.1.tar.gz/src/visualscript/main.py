import os
import sys

from PyQt5.QtWidgets import QApplication
from editor.editor_window import VPWindow
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    wnd = VPWindow()
    wnd.showMaximized()

    sys.exit(app.exec_())