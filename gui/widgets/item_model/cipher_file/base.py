import json
import logging
import os
import pickle
import typing

import OpenSSL
import rsa
from PyQt5 import QtGui, QtCore, QtWidgets

from cm.crypto.aes.base import AESCryptAlgorithm
from cm.crypto.aes.file import CipherAesFile
from cm.crypto.base import CryptoEncoder, CryptAlgorithm
from cm.crypto.des.base import DESCryptAlgorithm
from cm.crypto.des.file import CipherDesFile
from cm.crypto.file import SimpleCipherFile, PPCipherFile
from cm.crypto.rsa.base import RSACryptAlgorithm
from cm.crypto.rsa.file import CipherRSAFile
from cm.file import CipherFile
from cm.hash import get_hash_algorithm
from gui.common.env import report_with_exception, window
from gui.designer.impl.input_password_dialog import InputPasswordDialog

_CipherFileType = typing.TypeVar('_CipherFileType', bound=CipherFile)
_CryptAlgorithm = typing.TypeVar('_CryptAlgorithm', bound=CryptAlgorithm)


class CipherFileItemModel(QtGui.QStandardItemModel):
    __logger = logging.getLogger(__name__)
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

    def build_crypt_algorithm(self):
        if isinstance(self._cipher_file, SimpleCipherFile):
            rp = InputPasswordDialog().getpass('输入根密码').encode(self._cipher_file.encoding)
            if isinstance(self._cipher_file, CipherDesFile):
                self._crypt_algorithm = DESCryptAlgorithm(rp, self._cipher_file.des_cfg)
            elif isinstance(self._cipher_file, CipherAesFile):
                self._crypt_algorithm = AESCryptAlgorithm(rp, self._cipher_file.aes_cfg)
            else:
                raise RuntimeError(f'未知的加密方式：{self._cipher_file.encrypt_algorithm}。')
            if not bytes.fromhex(self._cipher_file.rph) == get_hash_algorithm(
                    self._cipher_file.hash_algorithm).hash(rp + bytes.fromhex(self._cipher_file.salt)):
                raise RuntimeError('密码错误！')
        elif isinstance(self._cipher_file, PPCipherFile):
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(window, '选取文件', os.getcwd(),
                                                                '所有文件(*);;加密证书文件(*.pfx,*.p12,*.jks);;'
                                                                '二进制密钥文件(*.der,*.cer);;文本密钥文件(*.pem);;'
                                                                '私钥文件(*.key);;包含公钥的证书(*.crt)')
            if not filepath:
                raise KeyboardInterrupt
            pp_pwd = None
            try:
                pp_pwd = InputPasswordDialog().getpass('输入证书文件密码', '没有密码点击取消').encode(self._cipher_file.encoding)
            except KeyboardInterrupt:
                pass
            with open(filepath, 'rb') as f:
                pk = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read(), pp_pwd)
            puk = rsa.PublicKey.load_pkcs1_openssl_pem(
                OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pk))
            prk = None
            try:
                prk = rsa.PrivateKey.load_pkcs1(
                    OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk), 'DER')
            except Exception as ce:
                self.__logger.error(ce, exc_info=True)
            if isinstance(self._cipher_file, CipherRSAFile):
                self._crypt_algorithm = RSACryptAlgorithm(self._cipher_file.sign_hash_algorithm, puk, prk)
            else:
                raise RuntimeError(f'未知的加密方式：{self._cipher_file.encrypt_algorithm}')
            if not self._crypt_algorithm.verify(self._cipher_file.sign_hash_algorithm.encode(),
                                                bytes.fromhex(self._cipher_file.hash_algorithm_sign)):
                raise RuntimeError('证书与密钥文件不符、文件损坏，或者遭到篡改。')
        else:
            raise RuntimeError(f'未知格式的密钥文件{type(self._cipher_file).__name__}')
        self.refresh(reload=True)

    @property
    def edited(self) -> bool:
        return self._edited

    @property
    def filepath(self) -> str:
        return self._filepath

    def load_file(self, filepath: str):
        self._crypt_algorithm = None
        self._cipher_file = None
        self._filepath = None
        self._edited = False
        with open(filepath, 'rb') as f:
            self._cipher_file = pickle.load(f)
            self._filepath = filepath
        try:
            self.build_crypt_algorithm()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '解密失败', str(e)).exec_()
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
                        left.setToolTip('未加载公钥无法验证')
                        right.setForeground(color_yellow)
                        right.setToolTip('未加载公钥无法验证')
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
