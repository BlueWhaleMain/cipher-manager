#  MIT License
#
#  Copyright (c) 2022-2025 BlueWhaleMain
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import json

from PyQt6 import QtWidgets, QtGui

from cm.base import CmJsonEncoder
from cm.file.base import CipherFile
from cm.file.table_record import TableRecordCipherFile
from gui.designer.attribute_dialog import Ui_attribute_dialog
from gui.widgets.item.analyze import AnalyzeItem
from gui.widgets.item.readonly import ReadOnlyItem


class AttributeDialog(QtWidgets.QDialog, Ui_attribute_dialog):
    """属性对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.model: QtGui.QStandardItemModel = QtGui.QStandardItemModel(self.attribute_tree_view)
        self.model.setHorizontalHeaderLabels(['名称', '值'])
        self.attribute_tree_view.setModel(self.model)
        self.attribute_tree_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def load_file(self, cipher_file: CipherFile) -> int:
        """加载一个加密方式文件的属性"""
        self.model.removeRows(0, self.model.rowCount())
        cipher_item = ReadOnlyItem('加密定义文件属性')
        cipher_item.appendRow((ReadOnlyItem('内容类型'), ReadOnlyItem(cipher_file.content_type)))
        cipher_item.appendRow((ReadOnlyItem('内容编码'), ReadOnlyItem(cipher_file.content_encoding)))
        cipher_item.appendRow((ReadOnlyItem('加密算法名称'), ReadOnlyItem(cipher_file.cipher_name)))

        cipher_args_item = ReadOnlyItem('加密算法参数')
        for k, v in cipher_file.cipher_args.items():
            cipher_args_item.appendRow((ReadOnlyItem(k), AnalyzeItem(v)))
        cipher_item.appendRow(cipher_args_item)

        cipher_item.appendRow((ReadOnlyItem('加密迭代次数'), AnalyzeItem(cipher_file.iter_count)))

        password_store_item = ReadOnlyItem('密码存储')
        password_store_item.appendRow((ReadOnlyItem('密码哈希'),
                                       AnalyzeItem(cipher_file.key_hash)))
        password_store_item.appendRow((ReadOnlyItem('哈希算法'), ReadOnlyItem(cipher_file.key_hash_name)))

        key_hash_args_item = ReadOnlyItem('哈希算法参数')
        for k, v in cipher_file.key_hash_args.items():
            key_hash_args_item.appendRow((ReadOnlyItem(k), AnalyzeItem(v)))
        password_store_item.appendRow(key_hash_args_item)

        password_store_item.appendRow((ReadOnlyItem('哈希迭代次数'),
                                       AnalyzeItem(cipher_file.key_hash_iter_count)))
        password_store_item.appendRow((ReadOnlyItem('密码盐值'),
                                       AnalyzeItem(cipher_file.password_salt)))
        password_store_item.appendRow((ReadOnlyItem('密码盐值长度'), AnalyzeItem(cipher_file.password_salt_len)))
        cipher_item.appendRow(password_store_item)

        if isinstance(cipher_file, TableRecordCipherFile):
            record_cipher_item = ReadOnlyItem('表格内容附加属性')
            self._counter_row(record_cipher_item, cipher_file)
            cipher_item.appendRow(record_cipher_item)
        self.model.appendRow(cipher_item)
        self.attribute_tree_view.expandAll()
        self.raw_data_text_edit.setMarkdown(f"""
```json
{json.dumps(cipher_file.model_dump(), cls=CmJsonEncoder, indent=2)}
```""")
        return self.exec()

    @classmethod
    def _counter_row(cls, item: QtGui.QStandardItem, cipher_file: TableRecordCipherFile) -> None:
        color_gray = QtGui.QColor('gray')
        left = ReadOnlyItem('存储的记录数量')
        left.setForeground(color_gray)
        right = AnalyzeItem(cipher_file.sum)
        right.setForeground(color_gray)
        item.appendRow((left, right))
