import json
import logging
import os
import pickle
import threading
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
from gui.designer.impl.new_cipher_file_dialog import NewCipherFileDialog

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
        self._edit_lock = False

    @classmethod
    def _spawn_pk(cls, pk: OpenSSL.crypto.PKey, _type, kl, progress: QtWidgets.QProgressDialog):
        pk.generate_key(_type, kl)
        progress.close()

    def spawn_rsa_cert(self):
        if not isinstance(self._cipher_file, CipherRSAFile):
            raise RuntimeError('状态异常')
        if self._cipher_file.hash_algorithm_sign:
            raise RuntimeError('该文件已经绑定了一个证书')
        pk = OpenSSL.crypto.PKey()
        kl, ok = QtWidgets.QInputDialog().getInt(window, '生成密钥对', '输入密钥长度（必须是2的倍数）：', 4096)
        if ok is False:
            raise KeyboardInterrupt
        progress = QtWidgets.QProgressDialog(window)
        progress.setWindowTitle("请稍等")
        progress.setLabelText("正在生成密钥...")
        progress.setRange(0, 0)
        threading.Timer(0, self._spawn_pk, (pk, OpenSSL.crypto.TYPE_RSA, kl, progress)).start()
        progress.exec_()
        puk = rsa.PublicKey.load_pkcs1_openssl_pem(OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pk))
        prk = rsa.PrivateKey.load_pkcs1(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk), 'DER')
        self._cipher_file.hash_algorithm_sign = rsa.sign(
            self._cipher_file.sign_hash_algorithm.encode(self._cipher_file.encoding), prk,
            self._cipher_file.sign_hash_algorithm).hex()
        pp_fp, _ = QtWidgets.QFileDialog().getSaveFileName(window, '保存证书文件', os.getcwd(),
                                                           '所有文件(*);;加密证书文件(*.pfx,*.p12,*.jks);;'
                                                           '二进制密钥文件(*.der,*.cer);;文本密钥文件(*.pem);;'
                                                           '私钥文件(*.key);;包含公钥的证书(*.crt)')
        if not pp_fp:
            raise KeyboardInterrupt
        pp_pwd = None
        try:
            pp_pwd = InputPasswordDialog().getpass('输入证书文件密码：', verify=True).encode(self._cipher_file.encoding)
        except KeyboardInterrupt:
            pass
        with open(pp_fp, 'wb') as pf:
            if pp_pwd:
                pf.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk, 'des-ede3-cbc', pp_pwd))
            else:
                pf.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk))
        return pp_fp, puk, prk

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
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(window, '选择包含密钥的文件', os.getcwd(),
                                                                '所有文件(*);;加密证书文件(*.pfx,*.p12,*.jks);;'
                                                                '二进制密钥文件(*.der,*.cer);;文本密钥文件(*.pem);;'
                                                                '私钥文件(*.key);;包含公钥的证书(*.crt)')
            puk = None
            prk = None
            if not filepath:
                filepath, puk, prk = self.spawn_rsa_cert()
            if not filepath:
                raise KeyboardInterrupt
            if puk is None:
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
        try:
            with open(filepath, 'rb') as f:
                self._cipher_file = pickle.load(f)
                self._filepath = filepath
            self.build_crypt_algorithm()
            self.refresh(reload=True)
            return
        except KeyboardInterrupt:
            pass
        except pickle.PickleError as e:
            raise RuntimeError(e)
        self._crypt_algorithm = None

    def save_file(self, filepath: str = None):
        if not filepath:
            if not self._filepath:
                self._filepath, _ = QtWidgets.QFileDialog.getSaveFileName(window, '保存密钥文件', os.getcwd(),
                                                                          '所有文件(*);;Pickle文件(*.pkl)')
            filepath = self._filepath
        if not filepath:
            raise KeyboardInterrupt
        if not self._cipher_file:
            raise RuntimeError('状态异常')
        with open(filepath, 'wb') as f:
            pickle.dump(self._cipher_file, f, self._cipher_file_protocol)
            self._edited = False
        self.refresh(reload=True)

    def dump_file(self):
        if not self._cipher_file:
            raise RuntimeError
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(window, '导出密钥文件', os.getcwd(),
                                                            '所有文件(*);;JSON文件(*.json)')
        with open(filepath, 'w') as f:
            json.dump(self._cipher_file.dict(), f, indent=2, cls=CryptoEncoder)

    def refresh(self, reload: bool = False):
        if reload is True:
            self.clear()
            self.setHorizontalHeaderLabels(['名称', '值'])
            if isinstance(self._cipher_file, SimpleCipherFile):
                for item in self._cipher_file.records:
                    left, right = self._make_row()
                    left.setText(item.key)
                    right.setText(item.value)
                    self.appendRow((left, right))
            elif isinstance(self._cipher_file, PPCipherFile):
                for item in self._cipher_file.records:
                    left, right = self._make_row()
                    left.setText(item.key)
                    right.setText(item.value)
                    if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
                        if not self._crypt_algorithm.verify((item.key + item.value).encode(self._cipher_file.encoding),
                                                            bytes.fromhex(item.sign)):
                            color_red = QtGui.QColor('red')
                            left.setForeground(color_red)
                            left.setToolTip('损坏或被篡改')
                            right.setForeground(color_red)
                            right.setToolTip('损坏或被篡改')
                    else:
                        color_orange = QtGui.QColor('orange')
                        left.setForeground(color_orange)
                        left.setToolTip('未加载公钥无法验证')
                        right.setForeground(color_orange)
                        right.setToolTip('未加载公钥无法验证')
                    self.appendRow((left, right))
            self.add()
        self.refreshed.emit()

    def add(self):
        self.appendRow(self._make_row())

    def try_edit(self, col: int, row: int):
        item = self.item(row, col)
        if item.isEditable():
            return
        if not self._cipher_file:
            self.make_cipher_file()
        if not self._crypt_algorithm:
            self.build_crypt_algorithm()
        self._edit_lock = True
        try:
            if col == 0:
                if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
                    if not self._crypt_algorithm.readonly:
                        item.setEditable(True)
                    return
            elif col == 1:
                item = self.item(row, 1)
                if isinstance(self._cipher_file, CipherFile):
                    value = bytes.fromhex(item.text())
                    if isinstance(self._crypt_algorithm, DESCryptAlgorithm):
                        value = self._crypt_algorithm.des_decrypt(value).rstrip(b'\0').decode(
                            self._cipher_file.encoding)
                    elif isinstance(self._crypt_algorithm, AESCryptAlgorithm):
                        value = self._crypt_algorithm.aes_decrypt(value).rstrip(b'\0').decode(
                            self._cipher_file.encoding)
                    elif isinstance(self._crypt_algorithm, RSACryptAlgorithm):
                        value = self._crypt_algorithm.rsa_decrypt(value).decode(self._cipher_file.encoding)
                    else:
                        return
                    item.setText(value)
                    item.setEditable(True)
            else:
                raise RuntimeError('状态异常')
        finally:
            self._edit_lock = False

    def _make_row(self) -> tuple[QtGui.QStandardItem, QtGui.QStandardItem]:
        left = QtGui.QStandardItem()
        if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
            if self._crypt_algorithm.readonly:
                left.setEditable(False)
        right = QtGui.QStandardItem()
        right.setEditable(False)
        return left, right

    def _edit_simple_value(self, value: str) -> str:
        value = value.encode(self._cipher_file.encoding)
        if isinstance(self._crypt_algorithm, DESCryptAlgorithm):
            value = self._crypt_algorithm.des_encrypt(value).hex()
        elif isinstance(self._crypt_algorithm, AESCryptAlgorithm):
            value = self._crypt_algorithm.aes_encrypt(value).hex()
        else:
            raise RuntimeError('无法修改')
        return value

    def _edit_pp_row(self, key: str, value: str) -> tuple[str, str, str]:
        value = value.encode(self._cipher_file.encoding)
        if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
            if self._crypt_algorithm.readonly:
                raise RuntimeError('无法修改')
            value = self._crypt_algorithm.rsa_encrypt(value).hex()
            sign = self._crypt_algorithm.sign((key + value).encode()).hex()
        else:
            raise RuntimeError('无法修改')
        return key, value, sign

    def make_cipher_file(self):
        try:
            self._cipher_file = NewCipherFileDialog().create_file()
            self.save_file()
        except KeyboardInterrupt:
            pass

    def _edit_data(self, col: int, row: int):
        if isinstance(self._cipher_file, SimpleCipherFile):
            key = self.item(row, 0).text()
            if row < len(self._cipher_file.records):
                if col == 0:
                    self._cipher_file.records[row].key = key
                elif col == 1:
                    item = self.item(row, 1)
                    value = self._edit_simple_value(item.text())
                    self._cipher_file.records[row].value = value
                else:
                    raise RuntimeError('状态异常')
            else:
                item = self.item(row, 1)
                value = self._edit_simple_value(item.text())
                self._cipher_file.records.append(self._cipher_file.Record(key=key, value=value))
        elif isinstance(self._cipher_file, PPCipherFile):
            item = self.item(row, 1)
            key, value, sign = self._edit_pp_row(self.item(row, 0).text(), item.text())
            if row < len(self._cipher_file.records):
                self._cipher_file.records[row].key = key
                self._cipher_file.records[row].value = value
                self._cipher_file.records[row].sign = sign
            else:
                self._cipher_file.records.append(self._cipher_file.Record(key=key, value=value, sign=sign))
        else:
            raise RuntimeError('未知文件格式')

    @report_with_exception
    def data_changed(self, index: QtCore.QModelIndex, _, __):
        col, row = index.column(), index.row()
        if not self.item(row, col).isEditable() or self._edit_lock:
            return
        try:
            if not self._cipher_file:
                self.make_cipher_file()
            if not self._crypt_algorithm:
                self.build_crypt_algorithm()
            self._edit_data(col, row)
        except KeyboardInterrupt:
            pass
        except RuntimeError as e:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '修改失败', str(e)).exec_()
        finally:
            self._edited = True
            self.refresh(reload=True)

    def remove(self, row: int):
        if isinstance(self._cipher_file, (SimpleCipherFile, PPCipherFile)):
            self._cipher_file.records.pop(row)
        else:
            raise RuntimeError('未知文件格式')
        self.removeRow(row)
        self._edited = True
        self.refresh(reload=True)
