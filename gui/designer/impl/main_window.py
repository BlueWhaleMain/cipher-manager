import logging

from PyQt5 import QtWidgets, QtGui, QtCore

from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.designer.impl.about_dialog import AboutDialog
from gui.designer.impl.basic_type_conversion_dialog import BasicTypeConversionDialog
from gui.designer.impl.encrypt_test_dialog import EncryptTestDialog
from gui.designer.impl.otp_dialog import OtpDialog
from gui.designer.impl.random_password_dialog import RandomPasswordDialog
from gui.designer.main_window import Ui_MainWindow
from gui.widgets.table_view.cipher_file.base import CipherFileTableView


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    __logger = logging.getLogger(__name__)

    @report_with_exception
    def __init__(self, app: QtWidgets.QApplication, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._name = self.windowTitle()
        self.table_view = CipherFileTableView(self.central_widget)
        self.grid_layout.addWidget(self.table_view, 0, 0, 1, 1)
        self.model = QtGui.QStandardItemModel(self.table_view)
        self.model.setHorizontalHeaderLabels(['名称', '值'])
        self.table_view.setModel(self.model)
        self._about_dialog: AboutDialog = AboutDialog(self)
        self._encrypt_test_dialog: EncryptTestDialog = EncryptTestDialog(self)
        self._random_password_dialog: RandomPasswordDialog = RandomPasswordDialog(self)
        self._basic_type_conversion_dialog: BasicTypeConversionDialog = BasicTypeConversionDialog(self)
        self._otp_dialog: OtpDialog = OtpDialog(self)
        self.action_new.triggered.connect(self._new_file)
        self.action_open.triggered.connect(self._open_file)
        self.action_save.triggered.connect(self._save_file)
        self.action_export.triggered.connect(self._export_file)
        self.action_attribute.triggered.connect(self._file_attribute)
        self.action_encrypt_test.triggered.connect(self._encrypt_test)
        self.action_import.triggered.connect(self._import_file)
        self.action_random_password.triggered.connect(self._random_password)
        self.action_basic_type_conversion.triggered.connect(self._basic_type_conversion)
        self.action_otp.triggered.connect(self._otp)
        self.action_ren.triggered.connect(self._ren)
        self.action_save_new.triggered.connect(self._save_new)
        self.action_stay_on_top.triggered.connect(self._stay_on_top)
        self.action_notes_mode.triggered.connect(self._notes_mode)
        self.action_about.triggered.connect(self._about)
        self.table_view.refreshed.connect(self._refresh)
        arguments = app.arguments()
        if len(arguments) > 1:
            self._open_file_(arguments[1])
        else:
            self._refresh_()
        self.setStatusTip('就绪')

    @report_with_exception
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().urls():
            e.accept()
        else:
            e.ignore()
        super().dragEnterEvent(e)

    @report_with_exception
    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        urls = e.mimeData().urls()
        if urls:
            self.table_view.open_file(urls[0].toLocalFile())
        super().dropEvent(e)

    @report_with_exception
    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        if self.table_view.edited:
            result = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Information, '退出', '有操作未保存。',
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel).exec_()
            if result == QtWidgets.QMessageBox.Save:
                try:
                    self.table_view.save_file()
                    return
                except OperationInterruptError:
                    pass
            elif result == QtWidgets.QMessageBox.Close:
                return
            e.ignore()
        super().closeEvent(e)

    @report_with_exception
    def changeEvent(self, e: QtCore.QEvent) -> None:
        if e.type() in (QtCore.QEvent.ActivationChange, QtCore.QEvent.WindowStateChange):
            if not self.isActiveWindow() or self.isMinimized():
                if self.action_auto_lock.isChecked():
                    self.table_view.lock()
        super().changeEvent(e)

    @report_with_exception
    def hideEvent(self, e: QtGui.QHideEvent) -> None:
        if self.action_auto_lock.isChecked():
            self.table_view.lock()
        super().hideEvent(e)

    @report_with_exception
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key_F12:
            self.action_notes_mode.setChecked(False)
            self._notes_mode_(False)
        super().keyPressEvent(e)

    @report_with_exception
    def _new_file(self, _):
        self.table_view.new_file()

    @report_with_exception
    def _import_file(self, _):
        self.table_view.import_file()

    @report_with_exception
    def _open_file(self, _):
        self._open_file_()

    def _open_file_(self, filepath: str = None):
        self.table_view.open_file(filepath)

    @report_with_exception
    def _save_file(self, _):
        self.table_view.save_file()

    @report_with_exception
    def _export_file(self, _):
        self.table_view.dump_file()

    @report_with_exception
    def _refresh(self):
        self._refresh_()

    def _refresh_(self):
        self.setWindowTitle(f'{"*" if self.table_view.edited else ""}'
                            f'{f"{self.table_view.filepath} - " if self.table_view.filepath else ""}'
                            f'{self._name}')
        if self.table_view.has_file:
            self.action_attribute.setEnabled(True)
            self.action_save.setEnabled(self.table_view.edited)
            self.action_ren.setEnabled(True)
            self.action_save_new.setEnabled(True)
            self.action_export.setEnabled(True)
        else:
            self.action_attribute.setEnabled(False)
            self.action_save.setEnabled(False)
            self.action_ren.setEnabled(False)
            self.action_save_new.setEnabled(False)
            self.action_export.setEnabled(False)
        self.table_view.action_remove.setEnabled(self.model.rowCount() > 1)

    @report_with_exception
    def _file_attribute(self, _):
        self.table_view.open_attribute_dialog()

    @report_with_exception
    def _encrypt_test(self, _):
        self._encrypt_test_dialog.run()

    @report_with_exception
    def _random_password(self, _):
        self._random_password_dialog.show()
        self._random_password_dialog.activateWindow()

    @report_with_exception
    def _basic_type_conversion(self, _):
        self._basic_type_conversion_dialog.show()
        self._basic_type_conversion_dialog.activateWindow()

    @report_with_exception
    def _otp(self, _):
        self._otp_dialog.show()
        self._otp_dialog.activateWindow()

    @report_with_exception
    def _ren(self, _):
        self.table_view.move_file()

    @report_with_exception
    def _save_new(self, _):
        self.table_view.save_new_file()

    @report_with_exception
    def _stay_on_top(self, selected):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, selected)
        self.show()

    @report_with_exception
    def _notes_mode(self, selected):
        self._notes_mode_(selected)

    def _notes_mode_(self, selected):
        self.action_auto_lock.setChecked(not selected)
        if not self.action_stay_on_top.isChecked():
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, selected)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, selected)
        self.menubar.setVisible(not selected)
        self.show()

    @report_with_exception
    def _about(self, _):
        self._about_dialog.show()
        self._about_dialog.activateWindow()
