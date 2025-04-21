import logging

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from cm.error import CmNotImplementedError
from gui.common.env import report_with_exception
from gui.designer.impl.about_dialog import AboutDialog
from gui.designer.impl.basic_type_conversion_dialog import BasicTypeConversionDialog
from gui.designer.impl.otp_dialog import OtpDialog
from gui.designer.impl.random_password_dialog import RandomPasswordDialog
from gui.designer.main_window import Ui_MainWindow
from gui.widgets.table_view.cipher_file import CipherFileTableView


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    __logger = logging.getLogger(__name__)

    @report_with_exception
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._name = self.windowTitle()
        self._table_view = CipherFileTableView(self.central_widget)
        self.grid_layout.addWidget(self._table_view, 0, 0, 1, 1)
        self.model = QtGui.QStandardItemModel(self._table_view)
        self._table_view.setModel(self.model)
        self._about_dialog: AboutDialog = AboutDialog(self)
        self._random_password_dialog: RandomPasswordDialog = RandomPasswordDialog(self)
        self._basic_type_conversion_dialog: BasicTypeConversionDialog = BasicTypeConversionDialog(self)
        self._otp_dialog: OtpDialog = OtpDialog(self)

        self.action_new.triggered.connect(self._new_file)
        self.action_open.triggered.connect(self._open_file)
        self.action_save.triggered.connect(self._save_file)
        self.action_save_new.triggered.connect(self._save_new)
        self.action_ren.triggered.connect(self._ren)
        self.action_close.triggered.connect(self._close_file)

        self.action_import.triggered.connect(self._import_file)
        self.action_export.triggered.connect(self._export_file)
        self.action_attribute.triggered.connect(self._file_attribute)

        self.action_encrypt_file.triggered.connect(self._encrypt_file)
        self.action_decrypt_file.triggered.connect(self._decrypt_file)

        self.action_decrypt_all.triggered.connect(self._decrypt_all)
        self.action_reload.triggered.connect(self._reload)
        self.action_sort_asc.triggered.connect(self._sort_asc)
        self.action_sort_desc.triggered.connect(self._sort_desc)

        self.action_search.triggered.connect(self._search)

        self.action_stay_on_top.triggered.connect(self._stay_on_top)
        self.action_notes_mode.triggered.connect(self._notes_mode)
        self.action_resize_column.triggered.connect(self._resize_column)
        self.action_auto_lock.triggered.connect(self._refresh)

        self.action_otp.triggered.connect(self._otp)
        self.action_hash_tools.triggered.connect(self._hash_tools)
        self.action_random_password.triggered.connect(self._random_password)
        self.action_basic_type_conversion.triggered.connect(self._basic_type_conversion)

        self.action_about.triggered.connect(self._about)
        self.action_github.triggered.connect(self._open_github)

        self._table_view.refreshed.connect(self._refresh)
        self.setStatusTip(self.tr('就绪'))

    @report_with_exception
    def init(self, app: QtWidgets.QApplication):
        arguments = app.arguments()
        if len(arguments) > 1:
            self._open_file_(arguments[1])
        else:
            self._refresh_()

    @report_with_exception
    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        urls = e.mimeData().urls()
        if urls:
            self._table_view.open_file(urls[0].toLocalFile())
        super().dropEvent(e)

    @report_with_exception
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().urls():
            e.accept()
        else:
            e.ignore()
        super().dragEnterEvent(e)

    @report_with_exception
    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        if self._table_view.edited:
            result = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Information, '退出', '有操作未保存。',
                QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard
                | QtWidgets.QMessageBox.StandardButton.Cancel).exec()
            if result == QtWidgets.QMessageBox.StandardButton.Save:
                self._table_view.save_file()
            elif result == QtWidgets.QMessageBox.StandardButton.Cancel:
                e.ignore()
                return
        super().closeEvent(e)

    @report_with_exception
    def changeEvent(self, e: QtCore.QEvent) -> None:
        if e.type() in (QtCore.QEvent.Type.ActivationChange, QtCore.QEvent.Type.WindowStateChange):
            if not self.isActiveWindow() or self.isMinimized():
                if self.action_auto_lock.isChecked():
                    self._table_view.lock()
        super().changeEvent(e)

    @report_with_exception
    def hideEvent(self, e: QtGui.QHideEvent) -> None:
        if self.action_auto_lock.isChecked():
            self._table_view.lock()
        super().hideEvent(e)

    @report_with_exception
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key.Key_F12:
            self.action_notes_mode.setChecked(False)
            self._notes_mode_(False)
        super().keyPressEvent(e)

    @report_with_exception
    def _new_file(self, _):
        self._table_view.new_file()

    @report_with_exception
    def _open_file(self, _):
        self._open_file_()

    @report_with_exception
    def _save_file(self, _):
        self._table_view.save_file()

    @report_with_exception
    def _save_new(self, _):
        self._table_view.save_new_file()

    @report_with_exception
    def _ren(self, _):
        self._table_view.move_file()

    @report_with_exception
    def _close_file(self, _):
        self._table_view.close_file()

    @report_with_exception
    def _import_file(self, _):
        self._table_view.import_file()

    @report_with_exception
    def _export_file(self, _):
        self._table_view.export_file()

    @report_with_exception
    def _file_attribute(self, _):
        self._table_view.open_attribute_dialog()

    @report_with_exception
    def _encrypt_file(self, _):
        self._table_view.encrypt_file()

    @report_with_exception
    def _decrypt_file(self, _):
        self._table_view.decrypt_file()

    @report_with_exception
    def _decrypt_all(self, _):
        self._table_view.decrypt_all()

    @report_with_exception
    def _reload(self, _):
        self._table_view.reload()

    @report_with_exception
    def _sort_asc(self, _):
        raise CmNotImplementedError

    @report_with_exception
    def _sort_desc(self, _):
        raise CmNotImplementedError

    @report_with_exception
    def _search(self, _):
        raise CmNotImplementedError

    @report_with_exception
    def _stay_on_top(self, selected):
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, selected)
        self.show()

    @report_with_exception
    def _notes_mode(self, selected):
        self._notes_mode_(selected)

    @report_with_exception
    def _resize_column(self, _):
        self._table_view.resizeColumnsToContents()

    @report_with_exception
    def _otp(self, _):
        self._otp_dialog.show()
        self._otp_dialog.activateWindow()

    @report_with_exception
    def _hash_tools(self, _):
        raise CmNotImplementedError

    @report_with_exception
    def _random_password(self, _):
        self._random_password_dialog.show()
        self._random_password_dialog.activateWindow()

    @report_with_exception
    def _basic_type_conversion(self, _):
        self._basic_type_conversion_dialog.show()
        self._basic_type_conversion_dialog.activateWindow()

    @report_with_exception
    def _about(self, _):
        self._about_dialog.show()
        self._about_dialog.activateWindow()

    @report_with_exception
    def _open_github(self, _):
        QDesktopServices.openUrl(QUrl("https://github.com/BlueWhaleMain/cipher-manager"))

    @report_with_exception
    def _refresh(self, _):
        self._refresh_()

    def _open_file_(self, filepath: str = None):
        self._table_view.open_file(filepath)

    def _notes_mode_(self, selected):
        self.action_auto_lock.setChecked(not selected)
        if not self.action_stay_on_top.isChecked():
            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, selected)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, selected)
        self.menubar.setVisible(not selected)
        self.show()

    @property
    def _lock_title(self) -> str:
        if not self._table_view.has_file:
            return ''
        if self._table_view.locked is True:
            return self.tr("已锁定")
        if self.action_auto_lock.isChecked():
            return self.tr("自动锁定已开启")
        return ''

    def _refresh_(self):
        self.setWindowTitle(f'{"*" if self._table_view.edited else ""}'
                            f'{f"{self._table_view.filepath} - " if self._table_view.filepath else ""}'
                            f'{self._name}'
                            f'{self._lock_title}')
        self.action_save.setEnabled(self._table_view.edited)
        has_file = self._table_view.has_file
        self.action_save_new.setEnabled(has_file)
        self.action_ren.setEnabled(has_file)
        self.action_close.setEnabled(has_file)

        self.action_export.setEnabled(has_file)
        self.action_attribute.setEnabled(has_file)

        self.action_encrypt_file.setEnabled(has_file)

        self.action_decrypt_all.setEnabled(has_file)
        self.action_reload.setEnabled(has_file)
        self.action_sort_asc.setEnabled(has_file)
        self.action_sort_desc.setEnabled(has_file)

        self.action_search.setEnabled(has_file)

        self.action_resize_column.setEnabled(has_file)
