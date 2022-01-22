import threading

import OpenSSL.crypto
from PyQt5 import QtWidgets, QtGui

from gui.designer.encrypt_test_dialog import Ui_EncryptTestDialog
from gui.widgets.item.readonly import ReadOnlyItem

ENCRYPT_ALGORITHM = ['DES']
HASH_ALGORITHM = ['EDE3']
MODE = ['ECB', 'CBC', 'CFB', 'OFB']


class EncryptTestDialog(QtWidgets.QDialog, Ui_EncryptTestDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = QtGui.QStandardItemModel()
        self.mapping_table_view.setModel(self.model)
        self.mapping_table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self._task = None

    def load(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['名称', '加密算法', '模式'])
        red_color = QtGui.QColor('red')
        green_color = QtGui.QColor('green')
        pk = OpenSSL.crypto.PKey()
        pk.generate_key(OpenSSL.crypto.TYPE_RSA, 1024)
        for enc in ENCRYPT_ALGORITHM:
            for has in HASH_ALGORITHM:
                for mod in MODE:
                    name = f'{enc}-{has}-{mod}'
                    row = [ReadOnlyItem(name), ReadOnlyItem(enc), ReadOnlyItem(mod)]
                    self.model.appendRow(row)
                    try:
                        OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk, name, b'123')
                        for r in row:
                            r.setForeground(green_color)
                    except Exception as e:
                        for r in row:
                            r.setForeground(red_color)
                            r.setToolTip(str(e))
        self._task = None

    def run(self):
        self._task = threading.Timer(0, self.load)
        self._task.start()
        self.exec_()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self._task:
            self._task.cancel()
