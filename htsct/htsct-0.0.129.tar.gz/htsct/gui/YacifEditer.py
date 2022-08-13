import sys
from pathlib import Path

import yaml
from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import QMainWindow, QFileDialog, QApplication

from htsct.gui.UI_YacifEditer import Ui_MainWindow
from htsct.utils.tools import parse_cif_ase_string, md5_hex


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.stringListModel = QStringListModel()
        self.listView.setModel(self.stringListModel)

    def openFileSlot(self):
        obj = self.sender()
        objName = obj.objectName()
        if objName in ("openFilePath", "actionOpenFile"):
            fileDialog = QFileDialog(self, directory=".")
            fileDirectory = fileDialog.getExistingDirectory(self, "选择根目录...")
            if fileDirectory:
                self.filePath.setText(Path(fileDirectory).__str__())
        if objName == "openSavePath":
            fileDialog = QFileDialog(self, directory=".")
            fileDirectory = fileDialog.getExistingDirectory(self, "选择保存目录...")
            if fileDirectory:
                self.savePath.setText(Path(fileDirectory).__str__())

    def loadYacifSlot(self):
        self.fileName.clear()
        filePath = Path(self.filePath.text())
        cifs = [i.name for i in filePath.glob("*.yacif")]
        self.fileName.addItems(cifs)

    def openYacifSlot(self):
        if Path(self.fileName.currentText()).suffix == ".yacif":
            yacif = Path(self.filePath.text()) / self.fileName.currentText()
            with yacif.open(encoding="utf-8") as fd:
                data = yaml.load(fd, Loader=yaml.FullLoader)
            cif = data.pop("cif")
            atoms = parse_cif_ase_string(cif)
            atoms.edit()
            tmp = Path(self.filePath.text()) / "tmp.cif"
            atoms.write(tmp, format="cif")
            new_cif = tmp.read_text("utf-8")
            data["cif"] = new_cif
            ID = data["structureInfo"]["ID"]
            Formula = data["structureInfo"]["Formula"]
            new_yacif = Path(self.savePath.text()) / f"{ID}.{Formula}_{md5_hex(tmp)}.yacif"
            with new_yacif.open("w+") as fd:
                yaml.dump(data, fd)
                print(f"保存{new_yacif}成功...")
                self.statusbar.showMessage(f"保存{new_yacif}成功...", timeout=1)
            tmp.unlink(missing_ok=True)
            self.addFile(new_yacif.__str__())

    def addFile(self, filePath):
        row = self.stringListModel.rowCount()
        self.stringListModel.insertRow(row)
        self.stringListModel.setData(self.stringListModel.index(row), filePath)

    def deleteRowSlot(self):
        index = self.listView.currentIndex()
        Path(index.data()).unlink(missing_ok=True)
        self.stringListModel.removeRow(index.row())

    def nextYacifSlot(self):
        count = self.fileName.count()
        newIndex = self.fileName.currentIndex() + 1
        if count:
            self.fileName.setCurrentIndex(newIndex if newIndex < count else 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
