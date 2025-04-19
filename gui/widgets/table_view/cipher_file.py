import csv
import functools
import logging
import os
import pickle
import shutil

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMessageBox, QProgressDialog

from cm import file_load, CmValueError
from cm.error import CmInterrupt
from cm.file.base import CipherFile
from cm.file.protect import ProtectCipherFile
from cm.file.table_record import TableRecordCipherFile
from cm.progress import CmProgress
from gui.common.env import report_with_exception, new_instance
from gui.common.progress import execute_in_progress, each_in_steps
from gui.designer.impl.attribute_dialog import AttributeDialog
from gui.designer.impl.input_password_dialog import InputPasswordDialog
from gui.designer.impl.new_cipher_file_dialog import NewCipherFileDialog
from gui.designer.impl.random_password_dialog import RandomPasswordDialog
from gui.designer.impl.text_show_dialog import TextShowDialog

_LOG = logging.getLogger(__name__)


class CipherFileTableView(QtWidgets.QTableView):
    refreshed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.__cipher_file: TableRecordCipherFile | None = None
        self._cipher_file_protocol: int = pickle.DEFAULT_PROTOCOL
        self._filepath: str | None = None
        self._edit_lock: bool = False
        self._edited: bool = False
        self._ignore_auto_lock: bool = False
        self._new_cipher_file_dialog: NewCipherFileDialog = NewCipherFileDialog(self)
        self._attribute_dialog: AttributeDialog = AttributeDialog(self)
        self._text_show_dialog: TextShowDialog = TextShowDialog(self)
        self._random_password_dialog: RandomPasswordDialog = RandomPasswordDialog(self)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.context_menu = QtWidgets.QMenu(self)

        self.action_view = QtGui.QAction(self)
        self.action_view.setText(self.tr('查看'))
        self.context_menu.addAction(self.action_view)

        self.action_edit = QtGui.QAction(self)
        self.action_edit.setText(self.tr('修改'))
        self.context_menu.addAction(self.action_edit)

        self.action_generate = QtGui.QAction(self)
        self.action_generate.setText(self.tr('生成'))
        self.context_menu.addAction(self.action_generate)

        self.context_menu.addSeparator()

        self.action_decrypt_row = QtGui.QAction(self)
        self.action_decrypt_row.setText(self.tr('解密整行'))
        self.context_menu.addAction(self.action_decrypt_row)

        self.action_decrypt_col = QtGui.QAction(self)
        self.action_decrypt_col.setText(self.tr('解密整列'))
        self.context_menu.addAction(self.action_decrypt_col)

        self.context_menu.addSeparator()

        self.action_remove_line = QtGui.QAction(self)
        self.action_remove_line.setText(self.tr('删除整行'))
        self.context_menu.addAction(self.action_remove_line)

        self.action_remove_colum = QtGui.QAction(self)
        self.action_remove_colum.setText(self.tr('删除整列'))
        self.context_menu.addAction(self.action_remove_colum)

        self.customContextMenuRequested.connect(self.create_context_menu)
        self.doubleClicked.connect(self._double_click)

        self.action_view.triggered.connect(self._view_item)
        self.action_edit.triggered.connect(self._edit_item)
        self.action_decrypt_row.triggered.connect(self._decrypt_row)
        self.action_decrypt_col.triggered.connect(self._decrypt_col)
        self.action_generate.triggered.connect(self._generate_item)
        self.action_remove_line.triggered.connect(self._remove_row)
        self.action_remove_colum.triggered.connect(self._remove_col)

        self.setAcceptDrops(True)

    @report_with_exception
    def setModel(self, model: QtCore.QAbstractItemModel | None) -> None:
        super().setModel(model)
        # noinspection PyUnresolvedReferences
        model.dataChanged.connect(self._data_changed)
        self._refresh(reload=True)

    def model(self) -> QtGui.QStandardItemModel | None:
        # 解决IDE类型索引不正确的问题
        return super().model()

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
        return self.__cipher_file is not None

    def new_file(self) -> None:
        if self.has_file and self._edited:
            raise CmInterrupt(self.tr('有操作未保存'))
        self._cipher_file = self._new_cipher_file_dialog.create_file()
        self.save_file()

    def open_file(self, filepath: str = None) -> None:
        if not filepath:
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('选择密钥文件'), self.current_dir,
                                                                self.tr('Pickle文件(*.pkl);;所有文件(*)'))
            if not filepath:
                return
        if self.has_file or self._edited:
            result = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, self.tr('打开'),
                                           self.tr('在新窗口中打开？'), QtWidgets.QMessageBox.StandardButton.Yes
                                           | QtWidgets.QMessageBox.StandardButton.No
                                           | QtWidgets.QMessageBox.StandardButton.Cancel, parent=self).exec()
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                new_instance(filepath)
                return
            elif result == QtWidgets.QMessageBox.StandardButton.Cancel:
                return
        if self.edited:
            result = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, self.tr('警告'),
                                           self.tr('有修改未保存，是否丢弃？'), QtWidgets.QMessageBox.StandardButton.Yes
                                           | QtWidgets.QMessageBox.StandardButton.No, parent=self).exec()
            if result == QtWidgets.QMessageBox.StandardButton.No:
                return
        with open(filepath, 'rb') as f:
            try:
                data = pickle.load(f)
            except Exception as e:
                raise CmValueError(self.tr('文件格式异常')) from e
            self._cipher_file = file_load(data)
            self._filepath = filepath
        self._refresh()

    def import_file(self) -> None:
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('导入记录'), self.current_dir,
                                                            self.tr('CSV文件(*.csv);;所有文件(*)'))
        if not filepath:
            return
        if not self._suggest_unlock():
            return
        with open(filepath, 'r') as f:
            for row in csv.reader(f):
                self._cipher_file.append_row(row)
            self._edited = True
            self._refresh(reload=True)

    def save_file(self, filepath: str = None) -> None:
        cipher_file = self._cipher_file
        if not self.has_file:
            return
        if not filepath:
            if not self._filepath:
                # 没有保存的路径属于新文件
                self._ui_edit_happened()
                self._filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr('保存密钥文件'),
                                                                          self.current_dir,
                                                                          self.tr('Pickle文件(*.pkl);;所有文件(*)'))
            filepath = self._filepath
        if not filepath:
            return
        with open(filepath, 'wb') as f:
            # noinspection PyTypeChecker
            pickle.dump(cipher_file.model_dump(), f, self._cipher_file_protocol)
            self._edited = False
        self._refresh()

    def move_file(self) -> None:
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr('重命名/移动密钥文件'), self.current_dir,
                                                            self.tr('Pickle文件(*.pkl);;所有文件(*)'))
        if not filepath:
            return
        shutil.move(self._filepath, filepath)
        self._filepath = filepath
        self._refresh()

    def save_new_file(self) -> None:
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr('另存密钥文件'), self.current_dir,
                                                            self.tr('Pickle文件(*.pkl);;所有文件(*)'))
        if not filepath:
            return
        with open(filepath, 'wb') as f:
            # noinspection PyTypeChecker
            pickle.dump(self._cipher_file, f, self._cipher_file_protocol)
            self._edited = False
        self._filepath = filepath
        self._refresh()

    def export_file(self) -> None:
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr('导出记录'),
                                                            os.path.join(self.current_dir,
                                                                         os.path.splitext(self._filepath)[0] + '.csv'),
                                                            self.tr('CSV文件(*.csv);;所有文件(*)'))
        if not filepath:
            return
        if not self._suggest_unlock():
            return
        with open(filepath, 'w') as f:
            csv.writer(f).writerows(self._cipher_file.reader())

    def encrypt_file(self) -> None:
        if not self._suggest_unlock():
            return
        self._ignore_auto_lock = True
        try:
            protect_file = ProtectCipherFile.from_cipher_file(self._cipher_file)
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('选择要加密的文件'), self.current_dir,
                                                                self.tr('所有文件(*)'))
            if not filepath:
                return
            dist_filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr('选择保存位置'),
                                                                     os.path.join(self.current_dir,
                                                                                  os.path.basename(filepath)
                                                                                  + ".cm-protect"),
                                                                     self.tr('管理器保护文件(*.cm-protect)'
                                                                             ';;所有文件(*)'))
            if not dist_filepath:
                return
            cm_progress = CmProgress(title=self.tr('加密文件中'))
            execute_in_progress(self, protect_file.pack_to, filepath, dist_filepath, 2048, cm_progress,
                                cm_progress=cm_progress)
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, self.tr('提示'),
                                  f'{self.tr("文件已加密至：")}{dist_filepath}{self.tr("。")}',
                                  QtWidgets.QMessageBox.StandardButton.Ok, self).exec()
        finally:
            self._ignore_auto_lock = False

    def decrypt_file(self) -> None:
        self_decrypt = self._suggest_unlock()
        self._ignore_auto_lock = True
        try:
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('选择要解密的文件'), self.current_dir,
                                                                self.tr('管理器保护文件(*.cm-protect);;所有文件(*)'))
            if not filepath:
                return
        finally:
            self._ignore_auto_lock = False
        protect_file = ProtectCipherFile.from_protect_file(filepath)
        if self_decrypt:
            if not protect_file.try_unlock_from_cipher_file(self._cipher_file):
                if not self._unlock_cipher_file(protect_file):
                    return
        else:
            if not self._unlock_cipher_file(protect_file):
                return
        dist_filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr('选择保存位置'),
                                                                 os.path.join(self.current_dir,
                                                                              protect_file.decrypt_filename()),
                                                                 self.tr('所有文件(*)'))
        if not dist_filepath:
            return
        cm_progress = CmProgress(title=self.tr('解密文件中'))
        execute_in_progress(self, protect_file.unpack_to, dist_filepath, 2048, cm_progress,
                            cm_progress=cm_progress)
        QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, self.tr('提示'),
                              f'{self.tr("文件已解密至：")}{dist_filepath}{self.tr("。")}',
                              QtWidgets.QMessageBox.StandardButton.Ok, self).exec()

    def open_attribute_dialog(self) -> None:
        self._attribute_dialog.load_file(self._cipher_file)

    def lock(self):
        if self._ignore_auto_lock:
            return
        if self.has_file:
            cipher_file = self._cipher_file
            if not cipher_file.locked:
                cipher_file.lock()
                self._refresh(reload=True)

    @property
    def _cipher_file(self) -> TableRecordCipherFile:
        if not self.has_file:
            result = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, self.tr('提示'),
                                           self.tr('当前没有任何加密方式，创建一个？'),
                                           QtWidgets.QMessageBox.StandardButton.Yes
                                           | QtWidgets.QMessageBox.StandardButton.Open
                                           | QtWidgets.QMessageBox.StandardButton.Cancel).exec()
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                self.new_file()
            elif result == QtWidgets.QMessageBox.StandardButton.Open:
                self.open_file()
            else:
                raise CmInterrupt
        return self.__cipher_file

    @_cipher_file.setter
    def _cipher_file(self, val: TableRecordCipherFile) -> None:
        self.__cipher_file = val
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
    def _edit_item(self, _):
        index = self.currentIndex()
        self._try_edit(index.column(), index.row())
        self._set(index, self._text_show_dialog.show_text(self.action_edit.text(),
                                                          self._get(self.currentIndex()),
                                                          True))

    @report_with_exception
    def _decrypt_row(self, _):
        cols = self.model().columnCount()
        row = self.currentIndex().row()
        progress = QProgressDialog(self)
        progress.setWindowTitle(self.tr('解密第{}行...').format(row + 1))
        try:
            self._ignore_auto_lock = True
            for col in each_in_steps(progress, range(cols), cols):
                if not self._try_edit(col, row):
                    progress.cancel()
        finally:
            self._ignore_auto_lock = False

    @report_with_exception
    def _decrypt_col(self, _):
        rows = self.model().rowCount()
        col = self.currentIndex().column()
        progress = QProgressDialog(self)
        progress.setWindowTitle(self.tr('解密第{}列...').format(col + 1))
        try:
            self._ignore_auto_lock = True
            for row in each_in_steps(progress, range(rows), rows):
                if not self._try_edit(col, row):
                    progress.cancel()
        finally:
            self._ignore_auto_lock = False
        if not progress.wasCanceled():
            self.resizeColumnToContents(col)

    @report_with_exception
    def _generate_item(self, _):
        index = self.currentIndex()
        text = self._random_password_dialog.manual_spawn()
        if text:
            self._set(index, text)

    @report_with_exception
    def _remove_row(self, _):
        row = self.currentIndex().row()
        if row >= self.model().rowCount() - 1:
            return
        button = QMessageBox.warning(self, self.tr('你确定吗？'), self.tr('将删除整行。'),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if button == QMessageBox.StandardButton.No:
            return
        self._cipher_file.records.pop(row)
        self.model().removeRow(row)
        self._ui_edit_happened()

    @report_with_exception
    def _remove_col(self, _):
        col = self.currentIndex().column()
        if col >= self.model().columnCount() - 1:
            return
        button = QMessageBox.warning(self, self.tr('你确定吗？'), self.tr('将删除整列。'),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if button == QMessageBox.StandardButton.No:
            return
        for record in self._cipher_file.records:
            if len(record) > col:
                record.pop(col)
        self.model().removeColumn(col)
        self._ui_edit_happened()

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
        finally:
            self._ui_edit_happened()

    def _ui_edit_happened(self):
        self._edited = True
        self._refresh()

    def _get(self, index: QtCore.QModelIndex) -> str | None:
        item = self.model().item(index.row(), index.column())
        return item.text() if item else None

    def _set(self, index: QtCore.QModelIndex, val: str) -> None:
        self._try_edit(index.column(), index.row())
        self.model().item(index.row(), index.column()).setText(val)

    def _set_(self, col: int, row: int, val: str) -> None:
        self._try_edit(col, row)
        self.model().item(col, row).setText(val)

    def _try_edit(self, col: int, row: int) -> bool:
        item = self._get_cell(row, col)
        if item.isEditable():
            return True
        if not self._suggest_unlock():
            return False
        self._edit_lock = True
        result = False
        try:
            # 重新获得QStandardItem对象，规避C对象被回收的异常
            # 若问题已解决，请移除此行代码
            item = self._get_cell(row, col)
            value = self._cipher_file.get_cell(row, col)
            if value:
                # 在未提供解密方式的情况下尝试编辑密码框
                # RuntimeError: wrapped C/C++ object of type QStandardItem has been deleted
                # 可能是弹出对话框处理其他逻辑时，QStandardItem对象被回收
                # 有概率造成闪退，无法捕获异常
                item.setText(value)
            item.setEditable(True)
            result = True
        finally:
            self._edit_lock = False
            return result

    def _suggest_unlock(self) -> bool:
        try:
            if self._cipher_file is None:
                return False
            if self._cipher_file.locked and not self._unlock():
                return False
            return True
        except CmInterrupt:
            return False

    def _unlock(self) -> bool:
        cipher_file = self._cipher_file
        if self._unlock_cipher_file(cipher_file):
            self._refresh()
            return True
        return False

    def _unlock_cipher_file(self, cipher_file: CipherFile) -> bool:
        if cipher_file.key_type.is_file:
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('选择包含密钥的文件'), self.current_dir,
                                                                self.tr('所有文件(*)'
                                                                        ';;二进制密钥文件(*.der *.cer *.cert)'
                                                                        ';;文本密钥文件(*.pem *.asc)'
                                                                        ';;私钥文件(*.key)'
                                                                        ';;包含公钥的证书(*.crt *.p7c)'))
            if not filepath:
                return False
            with open(filepath, 'rb') as f:
                key = f.read()
        else:
            key = InputPasswordDialog(self).getpass(self.tr('输入密码'), verify=cipher_file.key_hash is None,
                                                    validator=cipher_file.validate_key)
            if key is None:
                return False
        if cipher_file.set_key(key):
            self._ui_edit_happened()
        if cipher_file.key_type.is_file:
            if not cipher_file.validate_key(key):
                result = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, self.tr('密钥文件可能不正确'),
                                               self.tr('忽略并继续？'), QtWidgets.QMessageBox.StandardButton.Ignore
                                               | QtWidgets.QMessageBox.StandardButton.Cancel).exec()
                if result == QtWidgets.QMessageBox.StandardButton.Cancel:
                    return False
            passphrase = InputPasswordDialog(self).getpass(self.tr('输入证书密码（没有点击取消）'),
                                                           validator=self._key_passphrase_validator(key, cipher_file))
            if passphrase is None:
                return False
            execute_in_progress(self, cipher_file.unlock, key, passphrase)
        else:
            cipher_file.unlock(key)
        return True

    @classmethod
    def _key_passphrase_validator(cls, key: bytes, cipher_file: CipherFile):
        @functools.wraps(cipher_file.unlock)
        def wrapper(passphrase: str) -> bool:
            try:
                cipher_file.unlock(key, passphrase)
                return True
            except ValueError as e:
                _LOG.warning(e)
                return False

        return wrapper

    def _edit_data(self, col: int, row: int) -> None:
        if not self._suggest_unlock():
            return
        model = self.model()
        self._cipher_file.set_cell(row, col, model.item(row, col).text())
        column_count = model.columnCount()
        row_count = model.rowCount()
        if col + 1 >= column_count:
            model.appendColumn([self._make_cell() for _ in range(row_count)])
        if row + 1 >= row_count:
            model.appendRow([self._make_cell() for _ in range(column_count)])

    def _refresh(self, reload: bool = False):
        model = self.model()
        if reload is True:
            model.removeRows(0, model.rowCount())
            model.setRowCount(0)
            model.setColumnCount(0)
            if self.has_file:
                cipher_file = self._cipher_file
                for row in range(len(cipher_file.records)):
                    for col in range(len(cipher_file.records[row])):
                        model.setItem(row, col, self._make_cell(cipher_file.records[row][col].hex()))
            model.setColumnCount(model.columnCount() + 1)
            model.setRowCount(model.rowCount() + 1)
            self._get_cell(0, 0).setEditable(False)
            self.resizeColumnsToContents()
            for col in range(model.columnCount()):
                self.setColumnWidth(col, min(self.columnWidth(col), 255))
        self.action_decrypt_row.setEnabled(model.rowCount() > 1)
        self.action_decrypt_col.setEnabled(model.columnCount() > 1)
        self.action_remove_line.setEnabled(model.rowCount() > 1)
        self.action_remove_colum.setEnabled(model.columnCount() > 1)
        self.refreshed.emit()

    def _get_cell(self, row: int, col: int) -> QtGui.QStandardItem:
        model = self.model()
        item = model.item(row, col)
        if item is None:
            item = self._make_cell()
            model.setItem(row, col, item)
        return item

    @classmethod
    def _make_cell(cls, text: str = None) -> QtGui.QStandardItem:
        cell = QtGui.QStandardItem()
        if text:
            cell.setText(text)
        cell.setEditable(False)
        return cell
