import csv
import functools
import logging
import os
import pickle
import shutil

from PyQt6.QtCore import pyqtSignal, Qt, QAbstractItemModel, QModelIndex, pyqtBoundSignal
from PyQt6.QtGui import QAction, QIcon, QCursor, QStandardItem
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QInputDialog, QStyledItemDelegate, QTableView, QWidget, \
    QHeaderView, QMenu, QFileDialog
from PyQt6.sip import isdeleted

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


class CipherFileTableView(QTableView):
    refreshed: pyqtBoundSignal = pyqtSignal(bool)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.__cipher_file: TableRecordCipherFile | None = None
        self._cipher_file_protocol: int = pickle.DEFAULT_PROTOCOL
        self._filepath: str | None = None
        self._edited: bool = False
        self._new_cipher_file_dialog: NewCipherFileDialog = NewCipherFileDialog(self)
        self._attribute_dialog: AttributeDialog = AttributeDialog(self)
        self._text_show_dialog: TextShowDialog = TextShowDialog(self)
        self._random_password_dialog: RandomPasswordDialog = RandomPasswordDialog(self)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.context_menu = QMenu(self)

        self.action_view = QAction(self)
        self.action_view.setText(self.tr('查看'))
        self.context_menu.addAction(self.action_view)

        self.action_edit = QAction(self)
        self.action_edit.setText(self.tr('修改'))
        self.context_menu.addAction(self.action_edit)

        self.action_generate = QAction(self)
        self.action_generate.setText(self.tr('生成'))
        self.context_menu.addAction(self.action_generate)

        self.context_menu.addSeparator()

        self.action_decrypt_row = QAction(self)
        self.action_decrypt_row.setText(self.tr('解密整行'))
        self.context_menu.addAction(self.action_decrypt_row)

        self.action_decrypt_col = QAction(self)
        self.action_decrypt_col.setText(self.tr('解密整列'))
        self.context_menu.addAction(self.action_decrypt_col)

        self.context_menu.addSeparator()

        icon = QIcon.fromTheme("edit-delete")
        self.action_remove_line = QAction(self)
        self.action_remove_line.setIcon(icon)
        self.action_remove_line.setText(self.tr('删除整行'))
        self.context_menu.addAction(self.action_remove_line)

        self.action_remove_colum = QAction(self)
        self.action_remove_colum.setIcon(icon)
        self.action_remove_colum.setText(self.tr('删除整列'))
        self.context_menu.addAction(self.action_remove_colum)

        self.context_menu.addSeparator()

        self.action_resize_colum = QAction(self)
        self.action_resize_colum.setText(self.tr('调整列宽'))
        self.context_menu.addAction(self.action_resize_colum)

        self.customContextMenuRequested.connect(self.create_context_menu)
        self.doubleClicked.connect(self._double_click)

        # noinspection PyUnresolvedReferences
        self.action_view.triggered.connect(self._view_item)
        # noinspection PyUnresolvedReferences
        self.action_edit.triggered.connect(self._edit_item)
        # noinspection PyUnresolvedReferences
        self.action_decrypt_row.triggered.connect(self._decrypt_row)
        # noinspection PyUnresolvedReferences
        self.action_decrypt_col.triggered.connect(self._decrypt_col)
        # noinspection PyUnresolvedReferences
        self.action_generate.triggered.connect(self._generate_item)
        # noinspection PyUnresolvedReferences
        self.action_remove_line.triggered.connect(self._remove_row)
        # noinspection PyUnresolvedReferences
        self.action_remove_colum.triggered.connect(self._remove_col)
        # noinspection PyUnresolvedReferences
        self.action_resize_colum.triggered.connect(self._resize_col)

        self.setAcceptDrops(True)

    @report_with_exception
    def setModel(self, model: QAbstractItemModel | None) -> None:
        super().setModel(model)
        # noinspection PyUnresolvedReferences
        model.dataChanged.connect(self._data_changed)
        self._refresh(reload=True)

    @report_with_exception
    def create_context_menu(self, _):
        self.context_menu.popup(QCursor.pos())

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

    @property
    def locked(self) -> bool | None:
        return None if self.__cipher_file is None else self.__cipher_file.locked

    def new_file(self) -> None:
        if self.has_file and self._edited:
            raise CmInterrupt(self.tr('有操作未保存'))
        self._cipher_file = self._new_cipher_file_dialog.create_file()
        self.save_file()

    def open_file(self, filepath: str = None) -> None:
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(self, self.tr('选择加密定义文件'), self.current_dir,
                                                      self.tr('Pickle文件(*.pkl);;所有文件(*)'))
            if not filepath:
                return
        if self.has_file or self._edited:
            result = QMessageBox.information(self, self.tr('打开'), self.tr('在新窗口中打开？'),
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                             | QMessageBox.StandardButton.Cancel)
            if result == QMessageBox.StandardButton.Yes:
                new_instance(filepath)
                return
            elif result == QMessageBox.StandardButton.Cancel:
                return
        if self.edited:
            result = QMessageBox.warning(self, self.tr('警告'), self.tr('有修改未保存，是否丢弃？'),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if result == QMessageBox.StandardButton.No:
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
        filepath, _ = QFileDialog.getOpenFileName(self, self.tr('导入记录'), self.current_dir,
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
                self._file_edited()
                self._filepath, _ = QFileDialog.getSaveFileName(self, self.tr('保存加密定义文件'), self.current_dir,
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
        filepath, _ = QFileDialog.getSaveFileName(self, self.tr('重命名/移动加密定义文件'), self.current_dir,
                                                  self.tr('Pickle文件(*.pkl);;所有文件(*)'))
        if not filepath:
            return
        shutil.move(self._filepath, filepath)
        self._filepath = filepath
        self._refresh()

    def save_new_file(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(self, self.tr('另存加密定义文件'), self.current_dir,
                                                  self.tr('Pickle文件(*.pkl);;所有文件(*)'))
        if not filepath:
            return
        with open(filepath, 'wb') as f:
            # noinspection PyTypeChecker
            pickle.dump(self._cipher_file, f, self._cipher_file_protocol)
        self._filepath = filepath
        self._edited = False
        self._refresh()

    def export_file(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(self, self.tr('导出记录'),
                                                  os.path.join(self.current_dir,
                                                               os.path.splitext(self._filepath)[0] + '.csv'),
                                                  self.tr('CSV文件(*.csv);;所有文件(*)'))
        if not filepath:
            return
        if not self._suggest_unlock():
            return
        with open(filepath, 'w') as f:
            csv.writer(f).writerows(self._cipher_file.reader())

    def close_file(self) -> None:
        if self.has_file and self._edited:
            raise CmInterrupt(self.tr('有操作未保存'))
        self._cipher_file = None

    def encrypt_file(self) -> None:
        if not self._suggest_unlock():
            return
        protect_file = ProtectCipherFile.from_cipher_file(self._cipher_file)
        filepath, _ = QFileDialog.getOpenFileName(self, self.tr('选择要加密的文件'), self.current_dir,
                                                  self.tr('所有文件(*)'))
        if not filepath:
            return
        if protect_file.iter_count > 1:
            filesize = os.path.getsize(filepath)
            # 假设对称加密1024个字节1000次为流畅
            simple_encrypt_len = 1024
            suggest_iter_count = 1 if (protect_file.cipher_name == protect_file.cipher_name.PKCS1_OAEP
                                       or protect_file.cipher_name == protect_file.cipher_name.PKCS1_V1_5) else 1000
            # 此处暂时简单评估加密复杂度，以不大于表格流畅迭代次数的复杂度积为准
            crypt_score = simple_encrypt_len * suggest_iter_count
            if filesize * protect_file.iter_count > crypt_score:
                button = QMessageBox.question(self, self.tr('加密迭代次数过大'), self.tr('降低迭代次数？'),
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                                              QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)
                if button == QMessageBox.StandardButton.Cancel:
                    return
                if button == QMessageBox.StandardButton.Yes:
                    # 大文件的迭代次数曲线应随着体积增长而急剧下降，最终为1
                    iter_count = max(protect_file.iter_count * crypt_score // filesize, 1)
                    protect_file.iter_count, ok = QInputDialog.getInt(self, self.tr('输入合适的值'),
                                                                      self.tr('加密迭代次数'), iter_count)
                    if not ok:
                        return
        dist_filepath, _ = QFileDialog.getSaveFileName(self, self.tr('选择保存位置'),
                                                       os.path.join(self.current_dir, os.path.basename(filepath)
                                                                    + ".cm-protect"),
                                                       self.tr('管理器保护文件(*.cm-protect)'
                                                               ';;所有文件(*)'))
        if not dist_filepath:
            return
        cm_progress = CmProgress(title=self.tr('加密文件中'))
        execute_in_progress(self, protect_file.pack_to, filepath, dist_filepath, cm_progress, 2048,
                            cm_progress=cm_progress)
        QMessageBox.information(self, self.tr('提示'), f'{self.tr("文件已加密至：")}{dist_filepath}{self.tr("。")}',
                                QMessageBox.StandardButton.Ok)

    def decrypt_file(self) -> None:
        self_decrypt = self._suggest_unlock()
        filepath, _ = QFileDialog.getOpenFileName(self, self.tr('选择要解密的文件'), self.current_dir,
                                                  self.tr('管理器保护文件(*.cm-protect);;所有文件(*)'))
        if not filepath:
            return
        protect_file = ProtectCipherFile.from_protect_file(filepath)
        if self_decrypt:
            if not protect_file.try_unlock_from_cipher_file(self._cipher_file):
                if not self._unlock_cipher_file(protect_file):
                    return
        else:
            if not self._unlock_cipher_file(protect_file):
                return
        dist_filepath, _ = QFileDialog.getSaveFileName(self, self.tr('选择保存位置'),
                                                       os.path.join(self.current_dir,
                                                                    protect_file.decrypt_filename()),
                                                       self.tr('所有文件(*)'))
        if not dist_filepath:
            return
        cm_progress = CmProgress(title=self.tr('解密文件中'))
        execute_in_progress(self, protect_file.unpack_to, dist_filepath, cm_progress, 2048,
                            cm_progress=cm_progress)
        QMessageBox.information(self, self.tr('提示'), f'{self.tr("文件已解密至：")}{dist_filepath}{self.tr("。")}',
                                QMessageBox.StandardButton.Ok)

    def decrypt_all(self):
        cols = self.model().columnCount()
        rows = self.model().rowCount()
        progress = QProgressDialog(self)
        progress.setWindowTitle(self.tr('解密中...'))
        for row in each_in_steps(progress, range(rows), rows):
            sub_progress = QProgressDialog(progress)
            sub_progress.setWindowTitle(self.tr('解密第{}行...').format(row + 1))
            for col in each_in_steps(sub_progress, range(cols), cols):
                if not self._try_edit(row, col):
                    sub_progress.cancel()
            if sub_progress.wasCanceled():
                progress.cancel()
        self.resizeColumnsToContents()

    def reload(self):
        self._refresh(True)

    def open_attribute_dialog(self) -> None:
        self._attribute_dialog.load_file(self._cipher_file)

    def lock(self):
        if self.has_file:
            cipher_file = self._cipher_file
            if not cipher_file.locked:
                cipher_file.lock()
                self._refresh(reload=True)

    @property
    def _cipher_file(self) -> TableRecordCipherFile:
        if not self.has_file:
            result = QMessageBox.question(self, self.tr('提示'), self.tr('当前没有任何加密方式，创建一个？'),
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Open
                                          | QMessageBox.StandardButton.Cancel)
            if result == QMessageBox.StandardButton.Yes:
                self.new_file()
            elif result == QMessageBox.StandardButton.Open:
                self.open_file()
            else:
                raise CmInterrupt
        return self.__cipher_file

    @_cipher_file.setter
    def _cipher_file(self, val: TableRecordCipherFile | None) -> None:
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
        self._set(self.currentIndex(), self._text_show_dialog.show_text(self.action_edit.text(),
                                                                        self._get(self.currentIndex()), True))

    @report_with_exception
    def _decrypt_row(self, _):
        cols = self.model().columnCount()
        row = self.currentIndex().row()
        progress = QProgressDialog(self)
        progress.setWindowTitle(self.tr('解密第{}行...').format(row + 1))
        for col in each_in_steps(progress, range(cols), cols):
            if not self._try_edit(row, col):
                progress.cancel()

    @report_with_exception
    def _decrypt_col(self, _):
        rows = self.model().rowCount()
        col = self.currentIndex().column()
        progress = QProgressDialog(self)
        progress.setWindowTitle(self.tr('解密第{}列...').format(col + 1))
        for row in each_in_steps(progress, range(rows), rows):
            if not self._try_edit(row, col):
                progress.cancel()
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
        self._file_edited()
        self.model().removeRow(row)

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
        self._file_edited()
        self.model().removeColumn(col)

    @report_with_exception
    def _resize_col(self, _):
        col = self.currentIndex().column()
        if col >= self.model().columnCount() - 1:
            return
        self.resizeColumnToContents(col)

    @report_with_exception
    def _double_click(self, index: QModelIndex):
        self._try_edit(index.row(), index.column())

    @report_with_exception
    def _data_changed(self, index: QModelIndex, index2: QModelIndex, raw_index: list[int]):
        sender = self.sender()
        # 以下代码只能被用户修改触发
        if not isinstance(sender, QStyledItemDelegate):
            return
        print('单元格被修改', sender, (index.row(), index.column()), (index2.row(), index2.column()), raw_index)
        self._edit_data(index.row(), index.column())

    def _file_edited(self):
        self._edited = True
        self._refresh()

    def _get(self, index: QModelIndex) -> str | None:
        # noinspection PyUnresolvedReferences
        item = self.model().item(index.row(), index.column())
        return item.text() if item else None

    def _set(self, index: QModelIndex, val: str) -> None:
        if self._try_edit(index.row(), index.column()):
            # noinspection PyUnresolvedReferences
            self.model().item(index.row(), index.column()).setText(val)
            self._edit_data(index.row(), index.column())

    def _try_edit(self, row: int, col: int) -> bool:
        item = self._get_cell(row, col)
        if item.isEditable():
            return True
        if not self._suggest_unlock():
            return False
        if isdeleted(item):
            item = self._get_cell(row, col)
        value = self._cipher_file.get_cell(row, col)
        if value:
            item.setText(value)
        item.setEditable(True)
        return True

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
        while cipher_file.key_type.is_file:
            filepath, _ = QFileDialog.getOpenFileName(self, self.tr('选择包含密钥的文件'), self.current_dir,
                                                      self.tr('所有文件(*)'
                                                              ';;DER证书(*.der *.cer *.cert)'
                                                              ';;ASCII PEM证书(*.pem *.asc)'
                                                              ';;未加密的私钥文件(*.key)'
                                                              ';;PKCS证书(*.crt *.p7c)'))
            if not filepath:
                return False
            with open(filepath, 'rb') as f:
                key = f.read()
            if cipher_file.set_key(key):
                self._file_edited()
            if not cipher_file.validate_key(key):
                result = QMessageBox.question(self, self.tr('密钥文件可能不正确'), self.tr('忽略并继续？'),
                                              QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Ignore
                                              | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Retry)
                if result == QMessageBox.StandardButton.Retry:
                    continue
                if result == QMessageBox.StandardButton.Cancel:
                    return False
            passphrase = InputPasswordDialog(self).getpass(self.tr('输入文件密码（没有点击取消）'),
                                                           validator=self._key_passphrase_validator(key, cipher_file))
            if passphrase is None:
                return False
            return True
        key = InputPasswordDialog(self).getpass(self.tr('输入密码'), verify=cipher_file.key_hash is None,
                                                validator=cipher_file.validate_key)
        if key is None:
            return False
        if cipher_file.set_key(key):
            self._file_edited()
        cipher_file.unlock(key)
        return True

    def _key_passphrase_validator(self, key: bytes, cipher_file: CipherFile):
        @functools.wraps(cipher_file.unlock)
        def wrapper(passphrase: str) -> bool:
            execute_in_progress(self, cipher_file.unlock, key, passphrase)
            return True

        return wrapper

    def _edit_data(self, row: int, col: int) -> None:
        if not self._suggest_unlock():
            return
        model = self.model()
        try:
            # noinspection PyUnresolvedReferences
            self._cipher_file.set_cell(row, col, model.item(row, col).text())
        except:
            # 阻止反复响应事件导致状态不正确
            model.blockSignals(True)
            try:
                # noinspection PyUnresolvedReferences
                self._get_cell(row, col).setText(self._cipher_file.get_cell(row, col))
            finally:
                model.blockSignals(False)
            raise
        self._file_edited()
        column_count = model.columnCount()
        row_count = model.rowCount()
        if col + 1 >= column_count:
            # noinspection PyUnresolvedReferences
            model.appendColumn([self._make_cell() for _ in range(row_count)])
        if row + 1 >= row_count:
            # noinspection PyUnresolvedReferences
            model.appendRow([self._make_cell() for _ in range(column_count)])

    def _refresh(self, reload: bool = False):
        model = self.model()
        if reload is True:
            model.removeRows(0, model.rowCount())
            # noinspection PyUnresolvedReferences
            model.setRowCount(0)
            # noinspection PyUnresolvedReferences
            model.setColumnCount(0)
            if self.has_file:
                cipher_file = self._cipher_file
                for row in range(len(cipher_file.records)):
                    for col in range(len(cipher_file.records[row])):
                        # noinspection PyUnresolvedReferences
                        model.setItem(row, col, self._make_cell(cipher_file.records[row][col].hex()))
            # noinspection PyUnresolvedReferences
            model.setColumnCount(model.columnCount() + 1)
            # noinspection PyUnresolvedReferences
            model.setRowCount(model.rowCount() + 1)
            self._get_cell(0, 0).setEditable(False)
            self.resizeColumnsToContents()
            for col in range(model.columnCount()):
                self.setColumnWidth(col, min(self.columnWidth(col), 255))
        self.action_decrypt_row.setEnabled(model.rowCount() > 1)
        self.action_decrypt_col.setEnabled(model.columnCount() > 1)
        self.action_remove_line.setEnabled(model.rowCount() > 1)
        self.action_remove_colum.setEnabled(model.columnCount() > 1)
        self.refreshed.emit(reload)

    def _get_cell(self, row: int, col: int) -> QStandardItem:
        model = self.model()
        # noinspection PyUnresolvedReferences
        item = model.item(row, col)
        if item is None:
            item = self._make_cell()
            # noinspection PyUnresolvedReferences
            model.setItem(row, col, item)
        return item

    @classmethod
    def _make_cell(cls, text: str = None) -> QStandardItem:
        cell = QStandardItem()
        if text:
            cell.setText(text)
        cell.setEditable(False)
        return cell
