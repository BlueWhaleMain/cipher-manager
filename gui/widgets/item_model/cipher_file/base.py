import json
import pickle
import typing

from PyQt5 import QtGui, QtCore

from cm.crypto.base import CryptoEncoder, CryptAlgorithm
from cm.crypto.file import SimpleCipherFile, PPCipherFile
from cm.crypto.rsa.base import RSACryptAlgorithm
from cm.file import CipherFile
from gui.common.env import report_with_exception

_CipherFileType = typing.TypeVar('_CipherFileType', bound=CipherFile)
_CryptAlgorithm = typing.TypeVar('_CryptAlgorithm', bound=CryptAlgorithm)


class CipherFileItemModel(QtGui.QStandardItemModel):
    refreshed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._edited: bool = False
        self._filepath: typing.Optional[str] = None
        self._cipher_file: typing.Optional[_CipherFileType] = None
        self._cipher_file_protocol: int = pickle.DEFAULT_PROTOCOL
        self._crypt_algorithm: typing.Optional[_CryptAlgorithm] = None
        self.dataChanged.connect(self.data_changed)
        self.refresh(reload=True)

    @property
    def edited(self) -> bool:
        return self._edited

    @property
    def filepath(self) -> str:
        return self._filepath

    def load_file(self, filepath: str):
        with open(filepath, 'rb') as f:
            self._cipher_file = pickle.load(f)
            self._filepath = filepath
            self._edited = False
            self.refresh(reload=True)

    def save_file(self, filepath: str = None):
        if not filepath:
            filepath = self._filepath
        if not filepath or not self._cipher_file:
            raise RuntimeError
        with open(filepath, 'wb') as f:
            pickle.dump(self._cipher_file, f, self._cipher_file_protocol)
            self._edited = False
            self.refresh(reload=True)

    def dump_file(self, filepath: str):
        if not self._cipher_file:
            raise RuntimeError
        with open(filepath, 'w') as f:
            json.dump(self._cipher_file.dict(), f, indent=2, cls=CryptoEncoder)

    def refresh(self, reload: bool = False):
        if reload is True:
            self.clear()
            self.setHorizontalHeaderLabels(['名称', '值'])
            if isinstance(self._cipher_file, SimpleCipherFile):
                for item in self._cipher_file.records:
                    right = QtGui.QStandardItem(item.value)
                    right.setEditable(False)
                    self.appendRow((QtGui.QStandardItem(item.key), right))
            elif isinstance(self._cipher_file, PPCipherFile):
                for item in self._cipher_file.records:
                    left = QtGui.QStandardItem(item.key)
                    right = QtGui.QStandardItem(item.value)
                    right.setEditable(False)
                    if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
                        if not self._crypt_algorithm.verify((item.key + item.value).encode(self._cipher_file.encoding),
                                                            bytes.fromhex(item.sign)):
                            color_red = QtGui.QColor('red')
                            left.setForeground(color_red)
                            left.setToolTip('损坏或被篡改')
                            right.setForeground(color_red)
                            right.setToolTip('损坏或被篡改')
                    else:
                        color_yellow = QtGui.QColor('yellow')
                        left.setForeground(color_yellow)
                        right.setForeground(color_yellow)
                    self.appendRow((left, right))
            self.add()
        self.refreshed.emit()

    def add(self):
        right = QtGui.QStandardItem()
        right.setEditable(False)
        self.appendRow((QtGui.QStandardItem(), right))

    @report_with_exception
    def data_changed(self, index: QtCore.QModelIndex, _, __):
        if isinstance(self._cipher_file, SimpleCipherFile):
            if index.row() < len(self._cipher_file.records):
                if index.column() == 0:
                    self._cipher_file.records[index.row()].key = self.item(index.row(), 0).text()
            # else:
            #     self._cipher_file.records.append(self._cipher_file.Record(key=self.item(index.row(), 0).text(),
            #                                                               value=self.item(index.row(), 1).text()))
            return
        if isinstance(self._cipher_file, PPCipherFile):
            pass
        self._edited = True
        self.refresh()
