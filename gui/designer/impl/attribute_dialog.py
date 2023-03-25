import typing

from PyQt5 import QtWidgets, QtGui

from cm.crypto.aes.base import AESModeEnum
from cm.crypto.aes.file import CipherAesFile
from cm.crypto.des.base import DESModeEnum, DESPadModeEnum
from cm.crypto.des.file import CipherDesFile
from cm.crypto.file import SimpleCipherFile, PPCipherFile
from cm.crypto.rsa.file import CipherRSAFile
from cm.file import CipherFile
from gui.designer.attribute_dialog import Ui_attribute_dialog
from gui.widgets.item.readonly import ReadOnlyItem


class AttributeDialog(QtWidgets.QDialog, Ui_attribute_dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.model: QtGui.QStandardItemModel = QtGui.QStandardItemModel(self.attribute_tree_view)
        self.model.setHorizontalHeaderLabels(['名称', '值'])
        self.attribute_tree_view.setModel(self.model)
        self.attribute_tree_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

    def load_file(self, cipher_file: CipherFile) -> int:
        self.model.removeRows(0, self.model.rowCount())
        cipher_item = ReadOnlyItem('密钥文件属性')
        cipher_item.appendRow((ReadOnlyItem('文件编码'), ReadOnlyItem(cipher_file.encoding)))
        cipher_item.appendRow((ReadOnlyItem('加密类型'), ReadOnlyItem(cipher_file.encrypt_algorithm)))
        color_red = QtGui.QColor('red')
        if isinstance(cipher_file, SimpleCipherFile):
            simple_cipher_item = ReadOnlyItem('常规密钥文件附加属性')
            simple_cipher_item.appendRow(
                (ReadOnlyItem('使用的哈希算法'), ReadOnlyItem(cipher_file.hash_algorithm)))
            simple_cipher_item.appendRow((ReadOnlyItem('根密码哈希值'), ReadOnlyItem(cipher_file.rph)))
            simple_cipher_item.appendRow((ReadOnlyItem('根密码盐值'), ReadOnlyItem(cipher_file.salt)))
            self._counter_row(simple_cipher_item, cipher_file)
            if isinstance(cipher_file, CipherDesFile):
                cipher_des_item = ReadOnlyItem('DES文件附加属性')
                cipher_des_item.appendRow(
                    (ReadOnlyItem('模式'), ReadOnlyItem(DESModeEnum(cipher_file.des_cfg.mode).description)))
                _IV = cipher_file.des_cfg.IV
                cipher_des_item.appendRow((ReadOnlyItem('向量'), ReadOnlyItem(_IV.hex() if _IV else '空')))
                pad = cipher_file.des_cfg.pad
                cipher_des_item.appendRow((ReadOnlyItem('填充'), ReadOnlyItem(pad.hex() if pad else '空')))
                cipher_des_item.appendRow(
                    (ReadOnlyItem('填充模式'), ReadOnlyItem(DESPadModeEnum(cipher_file.des_cfg.padmode).description)))
                simple_cipher_item.appendRow(cipher_des_item)
            elif isinstance(cipher_file, CipherAesFile):
                cipher_aes_item = ReadOnlyItem('AES文件附加属性')
                cipher_aes_item.appendRow(
                    (ReadOnlyItem('模式'), ReadOnlyItem(AESModeEnum(cipher_file.aes_cfg.mode).description)))
                _IV = cipher_file.aes_cfg.IV
                cipher_aes_item.appendRow((ReadOnlyItem('向量'), ReadOnlyItem(_IV.hex() if _IV else '空')))
                simple_cipher_item.appendRow(cipher_aes_item)
            cipher_item.appendRow(simple_cipher_item)
        elif isinstance(cipher_file, PPCipherFile):
            pp_cipher_item = ReadOnlyItem('公私钥文件附加属性')
            cipher_item.appendRow(pp_cipher_item)
            pp_cipher_item.appendRow(
                (ReadOnlyItem('签名使用的哈希算法'), ReadOnlyItem(cipher_file.sign_hash_algorithm)))
            pp_cipher_item.appendRow(
                (ReadOnlyItem('签名哈希值'), ReadOnlyItem(cipher_file.hash_algorithm_sign)))
            self._counter_row(pp_cipher_item, cipher_file)
            if isinstance(cipher_file, CipherRSAFile):
                cipher_rsa_item = ReadOnlyItem('RSA文件附加属性')
                pp_cipher_item.appendRow(cipher_rsa_item)
            cipher_item.appendRow(pp_cipher_item)
        else:
            unknown_item = ReadOnlyItem('未知文件附加属性')
            unknown_item.setForeground(color_red)
            cipher_item.appendRow(unknown_item)
        self.model.appendRow(cipher_item)
        self.attribute_tree_view.expandAll()
        return self.exec_()

    @classmethod
    def _counter_row(cls, item: QtGui.QStandardItem, cipher_file: typing.Union[SimpleCipherFile, PPCipherFile]) -> None:
        color_gray = QtGui.QColor('gray')
        left = ReadOnlyItem('存储的记录数量')
        left.setForeground(color_gray)
        right = ReadOnlyItem(str(len(cipher_file.records)))
        right.setForeground(color_gray)
        item.appendRow((left, right))
