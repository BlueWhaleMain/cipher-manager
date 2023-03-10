import threading
import typing

import OpenSSL.crypto
from PyQt5 import QtWidgets, QtGui

from gui.common.env import report_with_exception
from gui.designer.encrypt_test_dialog import Ui_EncryptTestDialog
from gui.widgets.item.readonly import ReadOnlyItem


def test_tuple() -> typing.Generator[tuple[str, str, str], None, None]:
    yield 'DES', 'EDE3', 'CBC'
    sizes = ['128', '192', '256']
    aes_modes = ['ECB', 'CBC', 'CFB', 'OFB']
    for s in sizes:
        for m in aes_modes:
            yield 'AES', s, m


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
        for enc, has, mod in test_tuple():
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

    @report_with_exception
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self._task:
            self._task.cancel()
