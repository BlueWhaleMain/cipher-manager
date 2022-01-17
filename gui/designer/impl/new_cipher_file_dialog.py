import encodings

from PyQt5 import QtWidgets

from gui.common.env import report_with_exception
from gui.designer.new_cipher_file_dialog import Ui_NewCipherFileDialog


class NewCipherFileDialog(QtWidgets.QDialog, Ui_NewCipherFileDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._encoding = 'utf_8'
        self._ok = False
        for encoding in set(encodings.aliases.aliases.values()):
            self.comboBox.addItem(encoding, encoding)
        self.comboBox.setCurrentText(self._encoding)
        self.comboBox.currentIndexChanged.connect(self.index_changed)
        self.listWidget.addItem('DES')
        self.listWidget.addItem('AES')
        self.listWidget.addItem('RSA')
        self.listWidget.itemSelectionChanged.connect(self.selection_changed)

    def accept(self) -> None:
        self._ok = True

    def create_file(self):
        self.exec_()
        if self._ok:
            pass
        else:
            raise KeyboardInterrupt

    @report_with_exception
    def selection_changed(self):
        if self.listWidget.currentIndex().row() == 0:
            pass

    @report_with_exception
    def index_changed(self, *args):
        print(args)
