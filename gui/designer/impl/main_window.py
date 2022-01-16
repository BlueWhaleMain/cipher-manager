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

    def __init__(self, *args, **kwargs):
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
        self.action_open.triggered.connect(self.open_file)
        self.model.refreshed.connect(self.refresh)
        self.table_view.doubleClicked.connect(self.table_view_double_click)

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
    def open_file(self, _):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选取文件', os.getcwd(), '所有文件(*);;Pickle文件(*.pkl)')
        self.load_file(filepath)

    def load_file(self, filepath: str):
        try:
            self.model.load_file(os.path.abspath(filepath))
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '文件读取失败', str(e)).exec_()

    @report_with_exception
    def refresh(self):
        self.setWindowTitle(f'{"*" if self.model.edited else ""}'
                            f'{f"{self.model.filepath} - " if self.model.filepath else ""}'
                            f'{self._name}')

    @report_with_exception
    def table_view_double_click(self, index: QtCore.QModelIndex):
        pass
