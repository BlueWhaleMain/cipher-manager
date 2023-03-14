import encodings

from PyQt5 import QtWidgets

from cm.crypto.aes.base import AesCfg, AESCryptAlgorithm, AESModeEnum
from cm.crypto.aes.file import CipherAesFile
from cm.crypto.base import random_bytes
from cm.crypto.des.base import DesCfg, DESCryptAlgorithm, DESModeEnum, DESPadModeEnum
from cm.crypto.des.file import CipherDesFile
from cm.crypto.rsa.file import CipherRSAFile
from cm.file import CipherFile
from cm.hash import all_hash_algorithm
from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.designer.new_cipher_file_dialog import Ui_NewCipherFileDialog

es = []
for encoding in set(encodings.aliases.aliases.values()):
    es.append(encodings.search_function(encoding).name.upper())
es.sort()

hs = all_hash_algorithm()


class NewCipherFileDialog(QtWidgets.QDialog, Ui_NewCipherFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._ok = False
        for name in es:
            self.encoding_combo_box.addItem(name, name)
        self.encoding_combo_box.setCurrentText('UTF-8')
        self.cipher_type_list_widget.addItem('DES')
        self.cipher_type_list_widget.addItem('AES')
        self.cipher_type_list_widget.addItem('RSA')
        self.hash_algorithm_label = QtWidgets.QLabel()
        self.hash_algorithm_label.setObjectName('hash_algorithm_label')
        self.hash_algorithm_label.setText('使用的哈希算法：')
        self.hash_algorithm_combo_box = QtWidgets.QComboBox()
        self.hash_algorithm_combo_box.setObjectName('hash_algorithm_combo_box')
        self.hash_algorithm_combo_box.setEditable(True)
        for h in hs:
            self.hash_algorithm_combo_box.addItem(h.__TYPE__, h)
        self.salt_length_label = QtWidgets.QLabel()
        self.salt_length_label.setObjectName('salt_length_label')
        self.salt_length_label.setText('盐值长度：')
        self.salt_length_spin_box = QtWidgets.QSpinBox()
        self.salt_length_spin_box.setObjectName('salt_length_spin_box')
        self.salt_length_spin_box.setMinimum(16)
        self.salt_length_spin_box.setValue(32)

        self.cipher_grid_layout.addWidget(self.hash_algorithm_label, 0, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.hash_algorithm_combo_box, 0, 1, 1, 1)
        self.cipher_grid_layout.addWidget(self.salt_length_label, 1, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.salt_length_spin_box, 1, 1, 1, 1)

        self.des_mode_label = QtWidgets.QLabel()
        self.des_mode_label.setObjectName('des_mode_label')
        self.des_mode_label.setText('DES模式：')
        self.des_mode_combo_box = QtWidgets.QComboBox()
        self.des_mode_combo_box.setObjectName('des_mode_combo_box')
        self.des_mode_combo_box.setEditable(True)
        self.des_mode_combo_box.addItem('ECB', DESModeEnum.ECB)
        self.des_mode_combo_box.addItem('CBC', DESModeEnum.CBC)
        self.des_mode_combo_box.setCurrentIndex(1)
        self.des_pad_mode_label = QtWidgets.QLabel()
        self.des_pad_mode_label.setObjectName('des_pad_mode_label')
        self.des_pad_mode_label.setText('DES填充模式：')
        self.des_pad_mode_combo_box = QtWidgets.QComboBox()
        self.des_pad_mode_combo_box.setObjectName('des_pad_mode_combo_box')
        self.des_pad_mode_combo_box.setEditable(True)
        self.des_pad_mode_combo_box.addItem('NORMAL', DESPadModeEnum.NORMAL)
        self.des_pad_mode_combo_box.addItem('PKCS5', DESPadModeEnum.PKCS5)
        self.des_pad_mode_combo_box.setCurrentIndex(1)

        self.cipher_grid_layout.addWidget(self.des_mode_label, 2, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.des_mode_combo_box, 2, 1, 1, 1)
        self.cipher_grid_layout.addWidget(self.des_pad_mode_label, 3, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.des_pad_mode_combo_box, 3, 1, 1, 1)

        self.aes_mode_label = QtWidgets.QLabel()
        self.aes_mode_label.setObjectName('aes_mode_label')
        self.aes_mode_label.setText('AES模式：')
        self.aes_mode_combo_box = QtWidgets.QComboBox()
        self.aes_mode_combo_box.setObjectName('aes_mode_combo_box')
        self.aes_mode_combo_box.setEditable(True)
        self.aes_mode_combo_box.addItem('CBC', AESModeEnum.CBC)
        self.aes_mode_combo_box.addItem('CFB', AESModeEnum.CFB)
        self.aes_mode_combo_box.addItem('OFB', AESModeEnum.OFB)
        self.aes_mode_combo_box.setCurrentIndex(0)

        self.cipher_grid_layout.addWidget(self.aes_mode_label, 2, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.aes_mode_combo_box, 2, 1, 1, 1)

        self.sign_hash_algorithm_label = QtWidgets.QLabel()
        self.sign_hash_algorithm_label.setObjectName('sign_hash_algorithm_label')
        self.sign_hash_algorithm_label.setText('使用的签名哈希算法：')
        self.sign_hash_algorithm_combo_box = QtWidgets.QComboBox()
        self.sign_hash_algorithm_combo_box.setObjectName('sign_hash_algorithm_combo_box')
        self.sign_hash_algorithm_combo_box.setEditable(True)
        for h in hs:
            self.sign_hash_algorithm_combo_box.addItem(h.__TYPE__, h)

        self.cipher_grid_layout.addWidget(self.sign_hash_algorithm_label, 2, 0, 1, 1)
        self.cipher_grid_layout.addWidget(self.sign_hash_algorithm_combo_box, 2, 1, 1, 1)

        self.cipher_type_list_widget.itemSelectionChanged.connect(self.selection_changed)
        self.cipher_type_list_widget.setCurrentRow(0)

    @report_with_exception
    def accept(self) -> None:
        self._ok = True
        self.close()
        super().accept()

    def create_file(self) -> CipherFile:
        self.exec_()
        if self._ok:
            mode = self.cipher_type_list_widget.currentIndex().row()
            if mode == 0:
                salt = random_bytes(self.salt_length_spin_box.value())
                return CipherDesFile(encoding=self.encoding_combo_box.currentText(),
                                     hash_algorithm=self.hash_algorithm_combo_box.currentText(), salt=salt.hex(),
                                     des_cfg=DesCfg(mode=self.des_mode_combo_box.currentData(),
                                                    padmode=self.des_pad_mode_combo_box.currentData(),
                                                    IV=DESCryptAlgorithm.generate_iv()))
            elif mode == 1:
                salt = random_bytes(self.salt_length_spin_box.value())
                aes_mode = self.aes_mode_combo_box.currentData()
                return CipherAesFile(encoding=self.encoding_combo_box.currentText(),
                                     hash_algorithm=self.hash_algorithm_combo_box.currentText(), salt=salt.hex(),
                                     aes_cfg=AesCfg(mode=aes_mode,
                                                    IV=AESCryptAlgorithm.generate_iv(aes_mode)))
            elif mode == 2:
                return CipherRSAFile(encoding=self.encoding_combo_box.currentText(),
                                     sign_hash_algorithm=self.sign_hash_algorithm_combo_box.currentText())
            else:
                raise OperationInterruptError('状态异常')
        else:
            raise OperationInterruptError

    def show_simple_cipher_widget(self):
        self.hash_algorithm_label.show()
        self.hash_algorithm_combo_box.show()
        self.salt_length_label.show()
        self.salt_length_spin_box.show()

    def hide_widget(self):
        self.hash_algorithm_label.hide()
        self.hash_algorithm_combo_box.hide()
        self.salt_length_label.hide()
        self.salt_length_spin_box.hide()

        self.des_mode_label.hide()
        self.des_mode_combo_box.hide()
        self.des_pad_mode_label.hide()
        self.des_pad_mode_combo_box.hide()

        self.aes_mode_label.hide()
        self.aes_mode_combo_box.hide()

        self.sign_hash_algorithm_label.hide()
        self.sign_hash_algorithm_combo_box.hide()

    @report_with_exception
    def selection_changed(self):
        self.hide_widget()
        mode = self.cipher_type_list_widget.currentIndex().row()
        if mode == 0:
            self.show_simple_cipher_widget()
            self.des_mode_label.show()
            self.des_mode_combo_box.show()
            self.des_pad_mode_label.show()
            self.des_pad_mode_combo_box.show()
        elif mode == 1:
            self.show_simple_cipher_widget()
            self.aes_mode_label.show()
            self.aes_mode_combo_box.show()
        elif mode == 2:
            self.sign_hash_algorithm_label.show()
            self.sign_hash_algorithm_combo_box.show()
        else:
            raise OperationInterruptError('状态异常')
