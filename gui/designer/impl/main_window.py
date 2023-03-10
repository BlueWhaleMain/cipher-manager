import logging
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from gui.common import env
from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.designer.impl.about_form import AboutForm
from gui.designer.impl.encrypt_test_dialog import EncryptTestDialog
from gui.designer.impl.random_password_dialog import RandomPasswordDialog
from gui.designer.impl.text_show_dialog import TextShowDialog
from gui.designer.main_window import Ui_MainWindow
from gui.widgets.item_model.cipher_file.base import CipherFileItemModel
from gui.widgets.table_view.base import BaseTableView


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    __logger = logging.getLogger(__name__)

    def __init__(self, app: QtWidgets.QApplication, *args, **kwargs):
        if env.window is None:
            env.window = self
        else:
            raise RuntimeError
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._name = self.windowTitle()
        self.table_view = BaseTableView(self.centralwidget)
        self.gridLayout.addWidget(self.table_view, 0, 0, 1, 1)
        self.model = CipherFileItemModel(self.table_view)
        self.table_view.setModel(self.model)
        self._about_form: AboutForm = AboutForm()
        self.action_new.triggered.connect(self.new_file)
        self.action_open.triggered.connect(self.open_file)
        self.action_save.triggered.connect(self.save_file)
        self.action_export.triggered.connect(self.export_file)
        self.action_attribute.triggered.connect(self.file_attribute)
        self.action_encrypt_test.triggered.connect(self.encrypt_test)
        self.action_import.triggered.connect(self.import_file)
        self.action_random_password.triggered.connect(self.random_password)
        self.action_stay_on_top.triggered.connect(self.stay_on_top)
        self.action_notes_mode.triggered.connect(self.notes_mode)
        self.action_about.triggered.connect(self.about)
        self.model.refreshed.connect(self.refresh)
        self.table_view.doubleClicked.connect(self.table_view_double_click)
        self.table_view.action_view.triggered.connect(self.view_item)
        self.table_view.action_generate.triggered.connect(self.generate_item)
        self.table_view.action_remove.triggered.connect(self.remove_item)
        arguments = app.arguments()
        if len(arguments) > 1:
            self.load_file(arguments[1])
        else:
            self.refresh()
        self.setStatusTip('就绪')

    @report_with_exception
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().urls():
            e.accept()
        else:
            e.ignore()

    @report_with_exception
    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        urls = e.mimeData().urls()
        if urls:
            self._load_file(urls[0].toLocalFile())

    @report_with_exception
    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        if self.model.edited:
            result = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Information, '退出', '有操作未保存。',
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel).exec_()
            if result == QtWidgets.QMessageBox.Save:
                try:
                    self.model.save_file()
                    return
                except OperationInterruptError:
                    pass
            elif result == QtWidgets.QMessageBox.Close:
                return
            e.ignore()

    @report_with_exception
    def changeEvent(self, e: QtCore.QEvent) -> None:
        if e.type() in (QtCore.QEvent.ActivationChange, QtCore.QEvent.WindowStateChange):
            if not self.isActiveWindow() or self.isMinimized():
                if self.action_auto_lock.isChecked():
                    self.model.lock()

    @report_with_exception
    def hideEvent(self, e: QtGui.QHideEvent) -> None:
        if self.action_auto_lock.isChecked():
            self.model.lock()

    @report_with_exception
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key_F12:
            self.action_notes_mode.setChecked(False)
            self._notes_mode(False)

    @report_with_exception
    def new_file(self, _):
        self.model.make_cipher_file()

    @report_with_exception
    def import_file(self, _):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', self.model.current_dir,
                                                            '所有文件(*);;JSON文件(*.json)')
        if filepath:
            self.model.import_file(os.path.abspath(filepath))

    @report_with_exception
    def open_file(self, _):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择密钥文件', self.model.current_dir,
                                                            '所有文件(*);;Pickle文件(*.pkl)')
        if filepath:
            self.load_file(filepath)

    @report_with_exception
    def save_file(self, _):
        self.model.save_file()

    @report_with_exception
    def export_file(self, _):
        self.model.dump_file()

    @report_with_exception
    def load_file(self, filepath: str):
        self._load_file(filepath)

    def _load_file(self, filepath: str):
        self.model.load_file(os.path.abspath(filepath))

    @report_with_exception
    def refresh(self):
        self._refresh()

    def _refresh(self):
        self.setWindowTitle(f'{"*" if self.model.edited else ""}'
                            f'{f"{self.model.filepath} - " if self.model.filepath else ""}'
                            f'{self._name}')
        if self.model.has_file:
            self.action_attribute.setEnabled(True)
            self.action_save.setEnabled(self.model.edited)
            self.action_export.setEnabled(True)
        else:
            self.action_attribute.setEnabled(False)
            self.action_save.setEnabled(False)
            self.action_export.setEnabled(False)
        self.table_view.action_remove.setEnabled(self.model.rowCount() > 1)

    @report_with_exception
    def table_view_double_click(self, index: QtCore.QModelIndex):
        self.model.try_edit(index.column(), index.row())

    @report_with_exception
    def view_item(self, _):
        d = TextShowDialog()
        d.setWindowTitle(self.table_view.action_view.text())
        d.plain_text_edit.setPlainText(self.model.get(self.table_view.currentIndex()))
        d.exec_()

    @report_with_exception
    def generate_item(self, _):
        index = self.table_view.currentIndex()
        d = RandomPasswordDialog()
        d.exec_()
        self.model.set(index, d.result_plain_text_edit.toPlainText())

    @report_with_exception
    def remove_item(self, _):
        self.model.remove(self.table_view.currentIndex().row())

    @report_with_exception
    def file_attribute(self, _):
        self.model.open_attribute_dialog()

    @report_with_exception
    def encrypt_test(self, _):
        EncryptTestDialog().run()

    @report_with_exception
    def random_password(self, _):
        RandomPasswordDialog().exec_()

    @report_with_exception
    def stay_on_top(self, selected):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, selected)
        self.show()

    @report_with_exception
    def notes_mode(self, selected):
        self._notes_mode(selected)

    def _notes_mode(self, selected):
        self.action_auto_lock.setChecked(not selected)
        if not self.action_stay_on_top.isChecked():
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, selected)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, selected)
        self.menubar.setVisible(not selected)
        self.show()

    @report_with_exception
    def about(self, _):
        self._about_form = AboutForm()
        self._about_form.show()
