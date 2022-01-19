import logging
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from gui.common import env
from gui.common.env import report_with_exception
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
        self.action_new.triggered.connect(self.new_file)
        self.action_open.triggered.connect(self.open_file)
        self.action_save.triggered.connect(self.save_file)
        self.action_export.triggered.connect(self.export_file)
        self.action_attribute.triggered.connect(self.file_attribute)
        self.model.refreshed.connect(self.refresh)
        self.table_view.doubleClicked.connect(self.table_view_double_click)
        self.table_view.action_remove.triggered.connect(self.remove_item)
        arguments = app.arguments()
        if len(arguments) > 1:
            self.load_file(arguments[1])

    @report_with_exception
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    @report_with_exception
    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        filepath = e.mimeData().text().split('\n')[0].lstrip('file:///')
        self.load_file(filepath)

    @report_with_exception
    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        if self.model.edited:
            result = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Information, '退出', '有操作未保存',
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel).exec_()
            if result == QtWidgets.QMessageBox.Save:
                self.model.save_file()
                return
            elif result == QtWidgets.QMessageBox.Close:
                return
            e.ignore()

    @report_with_exception
    def new_file(self, _):
        self.model.make_cipher_file()

    @report_with_exception
    def open_file(self, _):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择密钥文件', os.getcwd(), '所有文件(*);;Pickle文件(*.pkl)')
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
        self.model.load_file(os.path.abspath(filepath))

    @report_with_exception
    def refresh(self):
        self.setWindowTitle(f'{"*" if self.model.edited else ""}'
                            f'{f"{self.model.filepath} - " if self.model.filepath else ""}'
                            f'{self._name}')

    @report_with_exception
    def table_view_double_click(self, index: QtCore.QModelIndex):
        self.model.try_edit(index.column(), index.row())

    @report_with_exception
    def remove_item(self, _):
        self.model.remove(self.table_view.currentIndex().row())

    @report_with_exception
    def file_attribute(self, _):
        self.model.open_attribute_dialog()
