import json
import logging
import os
import pickle
import shutil
import threading
import typing

import OpenSSL
import rsa
from PyQt5 import QtWidgets, QtGui, QtCore

from cm.crypto.aes.base import AESCryptAlgorithm
from cm.crypto.aes.file import CipherAesFile
from cm.crypto.base import CryptAlgorithm, CryptoEncoder
from cm.crypto.des.base import DESCryptAlgorithm
from cm.crypto.des.file import CipherDesFile
from cm.crypto.file import SimpleCipherFile, PPCipherFile
from cm.crypto.rsa.base import RSACryptAlgorithm
from cm.crypto.rsa.file import CipherRSAFile
from cm.file import CipherFile
from cm.hash import get_hash_algorithm
from cm.support.file import CipherFileSupport
from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.designer.impl.attribute_dialog import AttributeDialog
from gui.designer.impl.input_password_dialog import InputPasswordDialog
from gui.designer.impl.new_cipher_file_dialog import NewCipherFileDialog
from gui.designer.impl.random_password_dialog import RandomPasswordDialog
from gui.designer.impl.text_show_dialog import TextShowDialog

_CipherFileType = typing.TypeVar('_CipherFileType', bound=CipherFile)
_CryptAlgorithm = typing.TypeVar('_CryptAlgorithm', bound=CryptAlgorithm)
_logger = logging.getLogger(__name__)


class CipherFileTableView(QtWidgets.QTableView):
    refreshed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.__cipher_file: typing.Optional[_CipherFileType] = None
        self.__crypt_algorithm: typing.Optional[_CryptAlgorithm] = None
        self._cipher_file_protocol: int = pickle.DEFAULT_PROTOCOL
        self._filepath: typing.Optional[str] = None
        self._edit_lock: bool = False
        self._edited: bool = False
        self._new_cipher_file_dialog: NewCipherFileDialog = NewCipherFileDialog(self)
        self._attribute_dialog: AttributeDialog = AttributeDialog(self)
        self._text_show_dialog: TextShowDialog = TextShowDialog(self)
        self._random_password_dialog: RandomPasswordDialog = RandomPasswordDialog(self)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.context_menu = QtWidgets.QMenu(self)
        _translate = QtCore.QCoreApplication.translate
        self.action_view = QtWidgets.QAction(self)
        self.action_view.setText(_translate('CipherFileTableView', '查看'))
        self.context_menu.addAction(self.action_view)
        self.action_generate = QtWidgets.QAction(self)
        self.action_generate.setText(_translate('CipherFileTableView', '生成'))
        self.context_menu.addAction(self.action_generate)
        self.context_menu.addSeparator()
        self.action_remove = QtWidgets.QAction(self)
        self.action_remove.setText(_translate('CipherFileTableView', '删除'))
        self.context_menu.addAction(self.action_remove)
        self.customContextMenuRequested.connect(self.create_context_menu)
        self.doubleClicked.connect(self._double_click)
        self.action_view.triggered.connect(self._view_item)
        self.action_generate.triggered.connect(self._generate_item)
        self.action_remove.triggered.connect(self._remove_item)
        self.setAcceptDrops(True)

    @report_with_exception
    def setModel(self, model: typing.Optional[QtCore.QAbstractItemModel]) -> None:
        super().setModel(model)
        model.dataChanged.connect(self._data_changed)
        self._refresh(reload=True)

    @report_with_exception
    def create_context_menu(self, _):
        self.context_menu.popup(QtGui.QCursor.pos())

    @property
    def edited(self) -> bool:
        return self._edited

    @property
    def current_dir(self) -> str:
        if self._filepath:
            return os.path.dirname(self._filepath)
        return os.getcwd()

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def has_file(self) -> bool:
        return bool(self.__cipher_file)

    def new_file(self) -> None:
        if self.__cipher_file and self._edited:
            raise OperationInterruptError('有操作未保存')
        self._cipher_file = self._new_cipher_file_dialog.create_file()
        self.save_file()

    def open_file(self, filepath: str = None) -> None:
        if self.__cipher_file and self._edited:
            raise OperationInterruptError('有操作未保存')
        if not filepath:
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择密钥文件', self.current_dir,
                                                                '所有文件(*);;Pickle文件(*.pkl)')
        if not filepath:
            return
        try:
            with open(filepath, 'rb') as f:
                try:
                    self._cipher_file = pickle.load(f)
                except Exception as e:
                    raise OperationInterruptError('文件格式异常', e)
                self._filepath = filepath
            self._refresh()
            return
        except OperationInterruptError:
            raise
        except Exception as e:
            self._refresh()
            raise OperationInterruptError('文件读取失败', e)

    def import_file(self) -> None:
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', self.current_dir,
                                                            '所有文件(*);;JSON文件(*.json)')
        if not filepath:
            return
        cipher_file, errors = CipherFileSupport.parse_file(filepath)
        if not cipher_file:
            raise OperationInterruptError('文件读取失败', Exception(*errors))
        self._cipher_file = cipher_file
        self.save_file()

    def save_file(self, filepath: str = None) -> None:
        if not self.__cipher_file:
            raise OperationInterruptError('没有要保存的数据')
        if not filepath:
            if not self._filepath:
                # 没有保存的路径属于新文件
                self._edited = True
                self._refresh()
                self._filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, '保存密钥文件',
                                                                          self.current_dir,
                                                                          '所有文件(*);;Pickle文件(*.pkl)')
            filepath = self._filepath
        if not filepath:
            raise OperationInterruptError
        with open(filepath, 'wb') as f:
            pickle.dump(self._cipher_file, f, self._cipher_file_protocol)
            self._edited = False
        self._refresh(reload=True)

    def move_file(self) -> None:
        if not self.__cipher_file:
            raise OperationInterruptError('文件不可用，无法移动')
        if not self._filepath:
            raise OperationInterruptError('文件未保存，无法移动')
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, '重命名/移动密钥文件', self.current_dir,
                                                            '所有文件(*);;Pickle文件(*.pkl)')
        if not filepath:
            raise OperationInterruptError
        shutil.move(self._filepath, filepath)
        self._filepath = filepath
        self._refresh()

    def save_new_file(self) -> None:
        if not self.__cipher_file:
            raise OperationInterruptError('没有要保存的数据')
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, '另存密钥文件', self.current_dir,
                                                            '所有文件(*);;Pickle文件(*.pkl)')
        if not filepath:
            raise OperationInterruptError
        with open(filepath, 'wb') as f:
            pickle.dump(self._cipher_file, f, self._cipher_file_protocol)
            self._edited = False
        self._filepath = filepath
        self._refresh(reload=True)

    def dump_file(self) -> None:
        if not self.__cipher_file:
            raise OperationInterruptError
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, '导出密钥文件', self.current_dir,
                                                            '所有文件(*);;JSON文件(*.json)')
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(self._cipher_file.dict(), f, indent=2, cls=CryptoEncoder)

    def open_attribute_dialog(self) -> None:
        if not self.__cipher_file:
            raise OperationInterruptError
        self._attribute_dialog.load_file(self._cipher_file)

    def lock(self):
        self.__crypt_algorithm = None
        self._refresh(reload=True)

    @property
    def _crypt_algorithm(self) -> _CryptAlgorithm:
        if not self.__crypt_algorithm:
            try:
                self._build_crypt_algorithm()
            except OperationInterruptError:
                raise
            except Exception as e:
                self._cipher_file = None
                raise OperationInterruptError('构建加密对象失败，密钥记录可能已损坏', e)
        return self.__crypt_algorithm

    @property
    def _cipher_file(self) -> _CipherFileType:
        if not self.__cipher_file:
            self.new_file()
        return self.__cipher_file

    @_cipher_file.setter
    def _cipher_file(self, val: _CipherFileType) -> None:
        self.__cipher_file = val
        # 加密对象失去意义
        self.__crypt_algorithm = None
        # 不能指向原来的文件
        self._filepath = None
        # 重新加载，不存在修改
        self._edited = False
        # 需要刷新界面
        self._refresh(reload=True)

    @report_with_exception
    def _view_item(self, _):
        self._text_show_dialog.show_text(self.action_view.text(), self._get(self.currentIndex()))

    @report_with_exception
    def _generate_item(self, _):
        index = self.currentIndex()
        self._set(index, self._random_password_dialog.manual_spawn())

    @report_with_exception
    def _remove_item(self, _):
        self._remove(self.currentIndex().row())

    @report_with_exception
    def _double_click(self, index: QtCore.QModelIndex):
        self._try_edit(index.column(), index.row())

    @report_with_exception
    def _data_changed(self, index: QtCore.QModelIndex, _, __):
        col, row = index.column(), index.row()
        if not self.model().item(row, col).isEditable() or self._edit_lock:
            return
        try:
            self._edit_data(col, row)
            self._edited = True
        finally:
            self._refresh(reload=True)

    def _add(self):
        self.model().appendRow(self._make_row())

    def _get(self, index: QtCore.QModelIndex) -> str:
        return self.model().item(index.row(), index.column()).text()

    def _set(self, index: QtCore.QModelIndex, val: str) -> None:
        self._try_edit(index.column(), index.row())
        self.model().item(index.row(), index.column()).setText(val)

    def _remove(self, row: int):
        if isinstance(self.__cipher_file, (SimpleCipherFile, PPCipherFile)):
            try:
                self._cipher_file.records.pop(row)
                self._edited = True
            except IndexError:
                pass
        elif self.__cipher_file:
            raise OperationInterruptError('未知文件格式')
        else:
            raise OperationInterruptError
        self._refresh(reload=True)

    def _try_edit(self, col: int, row: int):
        item = self.model().item(row, col)
        if item.isEditable():
            return
        self._edit_lock = True
        try:
            if col == 0:
                if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
                    if not self._crypt_algorithm.readonly:
                        # 重新获得QStandardItem对象，规避C对象被回收的异常
                        # 若问题已解决，请移除此行代码
                        item = self.model().item(row, 0)
                        # 在未提供解密方式的情况下尝试编辑名称框
                        # RuntimeError: wrapped C/C++ object of type QStandardItem has been deleted
                        # 可能是弹出对话框处理其他逻辑时，QStandardItem对象被回收
                        item.setEditable(True)
                    return
            elif col == 1:
                if self._cipher_file:
                    # 重新获得QStandardItem对象，规避C对象被回收的异常
                    # 若问题已解决，请移除此行代码
                    item = self.model().item(row, 1)
                    # 在新建文件的情况下尝试编辑密码框
                    # RuntimeError: wrapped C/C++ object of type QStandardItem has been deleted
                    # 可能是弹出对话框处理其他逻辑时，QStandardItem对象被回收
                    value = item.text()
                    if value:
                        value = bytes.fromhex(value)
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
                        # 重新获得QStandardItem对象，规避C对象被回收的异常
                        # 若问题已解决，请移除此行代码
                        item = self.model().item(row, 1)
                        # 在未提供解密方式的情况下尝试编辑密码框
                        # RuntimeError: wrapped C/C++ object of type QStandardItem has been deleted
                        # 可能是弹出对话框处理其他逻辑时，QStandardItem对象被回收
                        item.setText(value)
                    if self._crypt_algorithm:
                        # 重新获得QStandardItem对象，规避C对象被回收的异常
                        # 若问题已解决，请移除此行代码
                        item = self.model().item(row, 1)
                        # 在密码框为空且未提供解密方式的情况下尝试编辑密码框
                        # RuntimeError: wrapped C/C++ object of type QStandardItem has been deleted
                        # 可能是弹出对话框处理其他逻辑时，QStandardItem对象被回收
                        item.setEditable(True)
            else:
                raise OperationInterruptError('状态异常')
        finally:
            self._edit_lock = False

    def _build_crypt_algorithm(self):
        if isinstance(self._cipher_file, SimpleCipherFile):
            rp = InputPasswordDialog(self).getpass('输入根密码', verify=self._cipher_file.rph == '').encode(
                self._cipher_file.encoding)
            if isinstance(self._cipher_file, CipherDesFile):
                self.__crypt_algorithm = DESCryptAlgorithm(rp, self._cipher_file.des_cfg)
            elif isinstance(self._cipher_file, CipherAesFile):
                self.__crypt_algorithm = AESCryptAlgorithm(rp, self._cipher_file.aes_cfg)
            else:
                raise OperationInterruptError(f'未知的加密方式：{self._cipher_file.encrypt_algorithm}。')
            if self._cipher_file.rph == '':
                self._cipher_file.rph = get_hash_algorithm(
                    self._cipher_file.hash_algorithm).hash(rp + bytes.fromhex(self._cipher_file.salt)).hex()
                self._edited = True
            elif not bytes.fromhex(self._cipher_file.rph) == get_hash_algorithm(
                    self._cipher_file.hash_algorithm).hash(rp + bytes.fromhex(self._cipher_file.salt)):
                self.__crypt_algorithm = None
                raise OperationInterruptError('密码错误！')
        elif isinstance(self._cipher_file, PPCipherFile):
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择包含密钥的文件', self.current_dir,
                                                                '所有文件(*);;加密证书文件(*.pfx,*.p12,*.jks);;'
                                                                '二进制密钥文件(*.der,*.cer);;文本密钥文件(*.pem);;'
                                                                '私钥文件(*.key);;包含公钥的证书(*.crt)')
            puk = None
            prk = None
            if not filepath:
                # 绑定过证书则不尝试生成新证书
                if self._cipher_file.hash_algorithm_sign:
                    raise OperationInterruptError
                filepath, puk, prk = self._spawn_rsa_cert()
            if not filepath:
                raise OperationInterruptError
            if puk is None:
                pp_pwd = None
                try:
                    pp_pwd = InputPasswordDialog(self).getpass('输入证书文件密码', '没有密码点击取消').encode(
                        self._cipher_file.encoding)
                except OperationInterruptError:
                    pass
                try:
                    with open(filepath, 'rb') as f:
                        pk = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read(), pp_pwd)
                except Exception as e:
                    raise OperationInterruptError('私钥文件加载失败', e)
                puk = rsa.PublicKey.load_pkcs1_openssl_pem(
                    OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pk))
                prk = None
                try:
                    prk = rsa.PrivateKey.load_pkcs1(
                        OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk), 'DER')
                except Exception as ce:
                    _logger.error(ce, exc_info=True)
            if isinstance(self._cipher_file, CipherRSAFile):
                self.__crypt_algorithm = RSACryptAlgorithm(self._cipher_file.sign_hash_algorithm, puk, prk)
            else:
                raise OperationInterruptError(f'未知的加密方式：{self._cipher_file.encrypt_algorithm}')
            if not self._crypt_algorithm.verify(self._cipher_file.sign_hash_algorithm.encode(),
                                                bytes.fromhex(self._cipher_file.hash_algorithm_sign)):
                self.__crypt_algorithm = None
                raise OperationInterruptError('证书与密钥文件不符、文件损坏，或者遭到篡改。')
        else:
            raise OperationInterruptError(f'未知格式的密钥文件{type(self._cipher_file).__name__}')
        self._refresh(reload=True)

    def _spawn_rsa_cert(self):
        if not isinstance(self._cipher_file, CipherRSAFile):
            raise OperationInterruptError('状态异常')
        if self._cipher_file.hash_algorithm_sign:
            raise OperationInterruptError('该文件已经绑定了一个证书')
        pk = OpenSSL.crypto.PKey()
        kl, ok = QtWidgets.QInputDialog().getInt(self, '生成密钥对', '输入密钥长度（必须是2的倍数）：', 4096)
        if ok is False:
            raise OperationInterruptError
        progress = QtWidgets.QProgressDialog(self)
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
        self._edited = True
        pp_fp, _ = QtWidgets.QFileDialog().getSaveFileName(self, '保存证书文件', self.current_dir,
                                                           '所有文件(*);;加密证书文件(*.pfx,*.p12,*.jks);;'
                                                           '二进制密钥文件(*.der,*.cer);;文本密钥文件(*.pem);;'
                                                           '私钥文件(*.key);;包含公钥的证书(*.crt)')
        if not pp_fp:
            raise OperationInterruptError
        pp_pwd = None
        try:
            pp_pwd = InputPasswordDialog(self).getpass('输入证书文件密码：', verify=True).encode(
                self._cipher_file.encoding)
        except OperationInterruptError:
            pass
        with open(pp_fp, 'wb') as pf:
            if pp_pwd:
                pf.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk, 'des-ede3-cbc', pp_pwd))
            else:
                pf.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk))
        return pp_fp, puk, prk

    @classmethod
    def _spawn_pk(cls, pk: OpenSSL.crypto.PKey, _type, kl, progress: QtWidgets.QProgressDialog):
        pk.generate_key(_type, kl)
        progress.close()

    def _edit_data(self, col: int, row: int):
        if isinstance(self._cipher_file, SimpleCipherFile):
            key = self.model().item(row, 0).text()
            if row < len(self._cipher_file.records):
                if col == 0:
                    self._cipher_file.records[row].key = key
                elif col == 1:
                    item = self.model().item(row, 1)
                    value = self._edit_simple_value(item.text())
                    self._cipher_file.records[row].value = value
                else:
                    raise OperationInterruptError('状态异常')
            else:
                item = self.model().item(row, 1)
                value = self._edit_simple_value(item.text())
                self._cipher_file.records.append(self._cipher_file.Record(key=key, value=value))
        elif isinstance(self._cipher_file, PPCipherFile):
            item = self.model().item(row, 1)
            key, value, sign = self._edit_pp_row(self.model().item(row, 0).text(), item.text())
            if row < len(self._cipher_file.records):
                self._cipher_file.records[row].key = key
                self._cipher_file.records[row].value = value
                self._cipher_file.records[row].sign = sign
            else:
                self._cipher_file.records.append(self._cipher_file.Record(key=key, value=value, sign=sign))
        elif self._cipher_file:
            raise OperationInterruptError('未知文件格式')

    def _edit_simple_value(self, value: str) -> str:
        value = value.encode(self._cipher_file.encoding)
        if isinstance(self._crypt_algorithm, DESCryptAlgorithm):
            value = self._crypt_algorithm.des_encrypt(value).hex()
        elif isinstance(self._crypt_algorithm, AESCryptAlgorithm):
            value = self._crypt_algorithm.aes_encrypt(value).hex()
        else:
            raise OperationInterruptError('无法修改')
        return value

    def _edit_pp_row(self, key: str, value: str) -> tuple[str, str, str]:
        value = value.encode(self._cipher_file.encoding)
        if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
            if self._crypt_algorithm.readonly:
                raise OperationInterruptError('无法修改')
            value = self._crypt_algorithm.rsa_encrypt(value).hex()
            sign = self._crypt_algorithm.sign((key + value).encode()).hex()
        else:
            raise OperationInterruptError('无法修改')
        return key, value, sign

    def _refresh(self, reload: bool = False):
        if reload is True:
            self.model().removeRows(0, self.model().rowCount())
            if isinstance(self.__cipher_file, SimpleCipherFile):
                for item in self._cipher_file.records:
                    left, right = self._make_row()
                    left.setText(item.key)
                    right.setText(item.value)
                    self.model().appendRow((left, right))
            elif isinstance(self.__cipher_file, PPCipherFile):
                for item in self._cipher_file.records:
                    left, right = self._make_row()
                    left.setText(item.key)
                    right.setText(item.value)
                    if isinstance(self.__crypt_algorithm, RSACryptAlgorithm):
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
                    self.model().appendRow((left, right))
            self._add()
        self.refreshed.emit()

    def _make_row(self) -> tuple[QtGui.QStandardItem, QtGui.QStandardItem]:
        left = QtGui.QStandardItem()
        if self.__crypt_algorithm:
            if isinstance(self._crypt_algorithm, RSACryptAlgorithm):
                if self._crypt_algorithm.readonly:
                    left.setEditable(False)
        else:
            left.setEditable(False)
        right = QtGui.QStandardItem()
        right.setEditable(False)
        return left, right
