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
import os
import sys

import Crypto.Cipher.AES
import Crypto.Cipher.DES
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMessageBox

from cm.error import CmInterrupt
from cm.file.base import CipherName, HashName, KeyType
from cm.file.table_record import TableRecordCipherFile
from gui.common import ENCODINGS
from gui.common.env import report_with_exception
from gui.designer.new_cipher_file_dialog import Ui_NewCipherFileDialog

_translate = QtCore.QCoreApplication.translate


class NewCipherFileDialog(QtWidgets.QDialog, Ui_NewCipherFileDialog):
    """新建加密方式文件对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._ok = False
        self._encodings = []

        for name in ENCODINGS:
            self._encodings.append(name)
            self.encoding_combo_box.addItem(name, name)

        self.encoding_combo_box.setCurrentText('UTF-8')

        self.cipher_type_list_widget.addItem('DES3')
        self.cipher_type_list_widget.addItem('AES')
        self.cipher_type_list_widget.addItem('PKCS1')

        self.iter_count_label = QtWidgets.QLabel(self)
        self.iter_count_label.setObjectName('iter_count_label')
        self.iter_count_label.setText(_translate('NewCipherFileDialog', '加密迭代次数：'))
        self.iter_count_label.setToolTip(_translate('NewCipherFileDialog', '循环加密内容的次数'))
        self.iter_count_spin_box = QtWidgets.QSpinBox(self)
        self.iter_count_spin_box.setObjectName('iter_count_spin_box')
        self.iter_count_spin_box.setMinimum(1)
        self.iter_count_spin_box.setMaximum(2147483647)
        self.iter_count_spin_box.setValue(1000)

        self.cipher_grid_layout.addWidget(self.iter_count_label, 0, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.iter_count_spin_box, 0, 1, 1, 1)

        self.key_hash_name_label = QtWidgets.QLabel(self)
        self.key_hash_name_label.setObjectName('key_hash_name_label')
        self.key_hash_name_label.setText(_translate('NewCipherFileDialog', '使用的哈希算法：'))
        self.key_hash_name_label.setToolTip(_translate('NewCipherFileDialog', '密钥摘要使用的哈希算法'))
        self.key_hash_name_combo_box = QtWidgets.QComboBox(self)
        self.key_hash_name_combo_box.setObjectName('key_hash_name_combo_box')
        self.key_hash_name_combo_box.setEditable(True)

        self.key_hash_name_combo_box.addItem(HashName.SHA1, HashName.SHA1)
        self.key_hash_name_combo_box.addItem(HashName.SHA256, HashName.SHA256)
        self.key_hash_name_combo_box.addItem(HashName.SHA512, HashName.SHA512)
        self.key_hash_name_combo_box.addItem(HashName.BLAKE2B, HashName.BLAKE2B)
        self.key_hash_name_combo_box.setCurrentIndex(3)

        self.cipher_grid_layout.addWidget(self.key_hash_name_label, 1, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.key_hash_name_combo_box, 1, 1, 1, 1)

        self.key_hash_iter_count_label = QtWidgets.QLabel(self)
        self.key_hash_iter_count_label.setObjectName('key_hash_iter_count_label')
        self.key_hash_iter_count_label.setText(_translate('NewCipherFileDialog', '哈希迭代次数：'))
        self.key_hash_iter_count_label.setToolTip(_translate('NewCipherFileDialog', '密钥摘要的迭代次数'))
        self.key_hash_iter_count_spin_box = QtWidgets.QSpinBox(self)
        self.key_hash_iter_count_spin_box.setObjectName('key_hash_iter_count_spin_box')
        self.key_hash_iter_count_spin_box.setMinimum(1)
        self.key_hash_iter_count_spin_box.setMaximum(2147483647)
        self.key_hash_iter_count_spin_box.setValue(100)

        self.cipher_grid_layout.addWidget(self.key_hash_iter_count_label, 2, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.key_hash_iter_count_spin_box, 2, 1, 1, 1)

        self.password_salt_len_label = QtWidgets.QLabel(self)
        self.password_salt_len_label.setObjectName('password_salt_len_label')
        self.password_salt_len_label.setText(_translate('NewCipherFileDialog', '盐值长度：'))
        self.password_salt_len_label.setToolTip(_translate('NewCipherFileDialog', '防哈希碰撞的数据长度'))
        self.password_salt_len_spin_box = QtWidgets.QSpinBox(self)
        self.password_salt_len_spin_box.setObjectName('password_salt_len_spin_box')
        self.password_salt_len_spin_box.setMinimum(16)
        self.password_salt_len_spin_box.setValue(64)
        self.password_salt_len_spin_box.setMaximum(2147483647)

        self.cipher_grid_layout.addWidget(self.password_salt_len_label, 3, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.password_salt_len_spin_box, 3, 1, 1, 1)

        self.des_mode_label = QtWidgets.QLabel(self)
        self.des_mode_label.setObjectName('des_mode_label')
        self.des_mode_label.setText(_translate('NewCipherFileDialog', 'DES模式：'))
        self.des_mode_combo_box = QtWidgets.QComboBox(self)
        self.des_mode_combo_box.setObjectName('des_mode_combo_box')
        self.des_mode_combo_box.setEditable(True)

        self.des_mode_combo_box.addItem('CBC', Crypto.Cipher.DES.MODE_CBC)
        self.des_mode_combo_box.setCurrentIndex(0)

        self.cipher_grid_layout.addWidget(self.des_mode_label, 4, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.des_mode_combo_box, 4, 1, 1, 1)

        self.aes_mode_label = QtWidgets.QLabel(self)
        self.aes_mode_label.setObjectName('aes_mode_label')
        self.aes_mode_label.setText(_translate('NewCipherFileDialog', 'AES模式：'))
        self.aes_mode_combo_box = QtWidgets.QComboBox(self)
        self.aes_mode_combo_box.setObjectName('aes_mode_combo_box')
        self.aes_mode_combo_box.setEditable(True)

        self.aes_mode_combo_box.addItem('CBC', Crypto.Cipher.AES.MODE_CBC)
        self.aes_mode_combo_box.setCurrentIndex(0)

        self.cipher_grid_layout.addWidget(self.aes_mode_label, 4, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.aes_mode_combo_box, 4, 1, 1, 1)

        self.aes_subtype_label = QtWidgets.QLabel(self)
        self.aes_subtype_label.setObjectName('aes_subtype_label')
        self.aes_subtype_label.setText(_translate('NewCipherFileDialog', 'AES子类型：'))
        self.aes_subtype_combo_box = QtWidgets.QComboBox(self)
        self.aes_subtype_combo_box.setObjectName('aes_subtype_combo_box')
        self.aes_subtype_combo_box.setEditable(True)

        self.aes_subtype_combo_box.addItem(CipherName.AES128, CipherName.AES128)
        self.aes_subtype_combo_box.addItem(CipherName.AES192, CipherName.AES192)
        self.aes_subtype_combo_box.addItem(CipherName.AES256, CipherName.AES256)
        self.aes_subtype_combo_box.setCurrentIndex(2)

        self.cipher_grid_layout.addWidget(self.aes_subtype_label, 5, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.aes_subtype_combo_box, 5, 1, 1, 1)

        self.pkcs1_subtype_label = QtWidgets.QLabel(self)
        self.pkcs1_subtype_label.setObjectName('pkcs1_subtype_label')
        self.pkcs1_subtype_label.setText(_translate('NewCipherFileDialog', 'PKCS1子类型：'))
        self.pkcs1_subtype_combo_box = QtWidgets.QComboBox(self)
        self.pkcs1_subtype_combo_box.setObjectName('pkcs1_subtype_combo_box')
        self.pkcs1_subtype_combo_box.setEditable(True)

        self.pkcs1_subtype_combo_box.addItem(CipherName.PKCS1_OAEP, CipherName.PKCS1_OAEP)
        self.pkcs1_subtype_combo_box.addItem(CipherName.PKCS1_V1_5, CipherName.PKCS1_V1_5)
        self.pkcs1_subtype_combo_box.setCurrentIndex(0)

        self.cipher_grid_layout.addWidget(self.pkcs1_subtype_label, 3, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.pkcs1_subtype_combo_box, 3, 1, 1, 1)

        self.key_type_label = QtWidgets.QLabel(self)
        self.key_type_label.setObjectName('key_type_label')
        self.key_type_label.setText(_translate('NewCipherFileDialog', 'KEY类型：'))
        self.key_type_combo_box = QtWidgets.QComboBox(self)
        self.key_type_combo_box.setObjectName('key_type_combo_box')
        self.key_type_combo_box.setEditable(True)

        self.key_type_combo_box.addItem(KeyType.RSA_KEYSTORE, KeyType.RSA_KEYSTORE)
        self.key_type_combo_box.setCurrentIndex(0)

        self.cipher_grid_layout.addWidget(self.key_type_label, 4, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.key_type_combo_box, 4, 1, 1, 1)

        self.cipher_type_list_widget.itemSelectionChanged.connect(self._selection_changed)
        self.cipher_type_list_widget.setCurrentRow(1)
        self.current_location_encoding_push_button.clicked.connect(self._current_location_encoding)

    @report_with_exception
    def accept(self) -> None:
        self._ok = True
        self.close()
        super().accept()

    def create_file(self) -> TableRecordCipherFile:
        """弹出对话框创建文件"""
        self.exec()
        if self._ok:
            mode = self.cipher_type_list_widget.currentIndex().row()
            if mode == 0:
                return TableRecordCipherFile(content_encoding=self.encoding_combo_box.currentText(),
                                             cipher_name=CipherName.DES3,
                                             iter_count=self.iter_count_spin_box.value(),
                                             key_hash_name=self.key_hash_name_combo_box.currentData(),
                                             key_hash_iter_count=self.key_hash_iter_count_spin_box.value(),
                                             password_salt_len=self.password_salt_len_spin_box.value(),
                                             cipher_args=dict(mode=self.des_mode_combo_box.currentData(),
                                                              iv=os.urandom(8)))
            elif mode == 1:
                aes_mode = self.aes_mode_combo_box.currentData()
                return TableRecordCipherFile(content_encoding=self.encoding_combo_box.currentText(),
                                             cipher_name=self.aes_subtype_combo_box.currentData(),
                                             iter_count=self.iter_count_spin_box.value(),
                                             key_hash_name=self.key_hash_name_combo_box.currentData(),
                                             key_hash_iter_count=self.key_hash_iter_count_spin_box.value(),
                                             password_salt_len=self.password_salt_len_spin_box.value(),
                                             cipher_args=dict(mode=aes_mode, iv=os.urandom(16)))
            elif mode == 2:
                iter_count = self.iter_count_spin_box.value()
                if iter_count > 1:
                    button = QMessageBox(QMessageBox.Icon.Question,
                                         _translate('NewCipherFileDialog', '提示'),
                                         _translate('NewCipherFileDialog',
                                                    '非对称加密使用超过1的迭代次数极可能导致加密失败。'),
                                         QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Cancel,
                                         parent=self).exec()
                    if button == QMessageBox.StandardButton.Cancel:
                        raise CmInterrupt
                return TableRecordCipherFile(content_encoding=self.encoding_combo_box.currentText(),
                                             cipher_name=self.pkcs1_subtype_combo_box.currentData(),
                                             iter_count=self.iter_count_spin_box.value(),
                                             key_type=self.key_type_combo_box.currentData(),
                                             key_hash_name=self.key_hash_name_combo_box.currentData(),
                                             key_hash_iter_count=self.key_hash_iter_count_spin_box.value())
            else:
                raise RuntimeError(f'{_translate("NewCipherFileDialog", "状态异常：")}mode = {mode}')
        raise CmInterrupt

    @report_with_exception
    def _selection_changed(self):
        self._hide_conflict_widget()
        mode = self.cipher_type_list_widget.currentIndex().row()
        if mode == 0:
            self.password_salt_len_label.show()
            self.password_salt_len_spin_box.show()
            self.des_mode_label.show()
            self.des_mode_combo_box.show()
            self.iter_count_spin_box.setValue(2000)
        elif mode == 1:
            self.password_salt_len_label.show()
            self.password_salt_len_spin_box.show()
            self.aes_mode_label.show()
            self.aes_mode_combo_box.show()
            self.aes_subtype_label.show()
            self.aes_subtype_combo_box.show()
            self.iter_count_spin_box.setValue(1000)
        elif mode == 2:
            self.pkcs1_subtype_label.show()
            self.pkcs1_subtype_combo_box.show()
            self.key_type_label.show()
            self.key_type_combo_box.show()
            self.iter_count_spin_box.setValue(1)
        else:
            raise RuntimeError(f'{_translate("NewCipherFileDialog", "状态异常：")}mode = {mode}')

    @report_with_exception
    def _current_location_encoding(self, _):
        self.encoding_combo_box.setCurrentIndex(self._encodings.index(sys.getdefaultencoding().upper()))

    def _hide_conflict_widget(self):
        self.password_salt_len_label.hide()
        self.password_salt_len_spin_box.hide()

        self.des_mode_label.hide()
        self.des_mode_combo_box.hide()

        self.aes_mode_label.hide()
        self.aes_mode_combo_box.hide()

        self.aes_subtype_label.hide()
        self.aes_subtype_combo_box.hide()

        self.pkcs1_subtype_label.hide()
        self.pkcs1_subtype_combo_box.hide()

        self.key_type_label.hide()
        self.key_type_combo_box.hide()
