from PyQt5 import QtWidgets, QtGui

from cm.crypto.file import SimpleCipherFile, PPCipherFile
from cm.file import CipherFile
from gui.designer.attribute_dialog import Ui_AttributeDialog
from gui.widgets.item.readonly import ReadOnlyItem


class AttributeDialog(QtWidgets.QDialog, Ui_AttributeDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['名称', '值'])
        self.attribute_tree_view.setModel(self.model)
        self.attribute_tree_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

    @classmethod
    def counter_row(cls, item: QtGui.QStandardItem, cipher_file):
        color_gray = QtGui.QColor('gray')
        left = ReadOnlyItem('存储的记录数量')
        left.setForeground(color_gray)
        right = ReadOnlyItem(str(len(cipher_file.records)))
        right.setForeground(color_gray)
        item.appendRow((left, right))

    def load_file(self, cipher_file: CipherFile):
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
            self.counter_row(simple_cipher_item, cipher_file)
            cipher_item.appendRow(simple_cipher_item)
        elif isinstance(cipher_file, PPCipherFile):
            pp_cipher_item = ReadOnlyItem('公私钥文件附加属性')
            cipher_item.appendRow(pp_cipher_item)
            pp_cipher_item.appendRow(
                (ReadOnlyItem('签名使用的哈希算法'), ReadOnlyItem(cipher_file.sign_hash_algorithm)))
            pp_cipher_item.appendRow(
                (ReadOnlyItem('签名哈希值'), ReadOnlyItem(cipher_file.hash_algorithm_sign)))
            self.counter_row(pp_cipher_item, cipher_file)
            cipher_item.appendRow(pp_cipher_item)
        else:
            unknown_item = ReadOnlyItem('未知文件附加属性')
            unknown_item.setForeground(color_red)
            cipher_item.appendRow(unknown_item)
        self.model.appendRow(cipher_item)
        self.attribute_tree_view.expandAll()
        self.exec_()
