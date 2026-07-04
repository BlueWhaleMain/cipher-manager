#  MIT License
#
#  Copyright (c) 2022-2026 BlueWhaleMain
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import time

import keyboard
from Crypto.PublicKey import RSA
from PyQt6.QtCore import QUrl, Qt, QEvent, QTimer, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QDesktopServices, QStandardItemModel, QDropEvent, QDragEnterEvent, QCloseEvent, QHideEvent, \
    QKeyEvent, QCursor, QMouseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog, QFileDialog, QSystemTrayIcon

import cm.base
from cm.error import CmNotImplementedError
from gui.common import env
from gui.common.env import report_with_exception, GLOBAL_SIGNAL, new_instance, quit_now
from gui.common.progress import execute_in_progress
from gui.designer.impl.about_dialog import AboutDialog
from gui.designer.impl.basic_type_conversion_dialog import BasicTypeConversionDialog
from gui.designer.impl.check_for_updates_form import CheckForUpdatesForm
from gui.designer.impl.delayed_operation_confirm_dialog import DelayedOperationDialog
from gui.designer.impl.input_password_dialog import InputPasswordDialog
from gui.designer.impl.otp_dialog import OtpDialog
from gui.designer.impl.random_password_dialog import RandomPasswordDialog
from gui.designer.impl.search_dialog import SearchDialog
from gui.designer.main_window import Ui_MainWindow
from gui.widgets.table_view.cipher_file import CipherFileTableView


class MainWindow(QMainWindow, Ui_MainWindow):
    """应用程序主窗口"""
    insert_selection_triggered = pyqtSignal()
    toggle_flow_mode_triggered = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._name = self.windowTitle()
        self._system_tray_icon = QSystemTrayIcon(self)
        self._system_tray_icon.setIcon(self.windowIcon())
        self._system_tray_icon.show()
        self._table_view = CipherFileTableView(self.central_widget)
        self.grid_layout.addWidget(self._table_view, 0, 0, 1, 1)
        self._table_view.setModel(QStandardItemModel(self._table_view))
        self._idle_waiting = False
        self._idle_max = 30 * 1000
        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._idle_timeout)
        self._idle_timer.start(self._idle_max)
        self._search_dialog = SearchDialog(self._table_view, self)
        self._about_dialog: AboutDialog = AboutDialog(self)
        self._random_password_dialog: RandomPasswordDialog = RandomPasswordDialog(self)
        self._basic_type_conversion_dialog: BasicTypeConversionDialog = BasicTypeConversionDialog(self)
        self._otp_dialog: OtpDialog = OtpDialog(self)
        self._check_for_updates_form: CheckForUpdatesForm = CheckForUpdatesForm()

        self.action_new.triggered.connect(self._new_file)
        self.action_open.triggered.connect(self._open_file)
        self.action_save.triggered.connect(self._save_file)
        self.action_save_new.triggered.connect(self._save_new)
        self.action_ren.triggered.connect(self._ren)
        self.action_close.triggered.connect(self._close_file)

        self.action_merge.triggered.connect(self._merge_from_file)
        self.action_import.triggered.connect(self._import_file)
        self.action_export.triggered.connect(self._export_file)
        self.action_attribute.triggered.connect(self._file_attribute)

        self.action_encrypt_file.triggered.connect(self._encrypt_file)
        self.action_decrypt_file.triggered.connect(self._decrypt_file)

        self.action_decrypt_all.triggered.connect(self._decrypt_all)
        self.action_reload.triggered.connect(self._reload)

        self.action_search.triggered.connect(self._search)

        self.action_stay_on_top.triggered.connect(self._stay_on_top)
        self.action_notes_mode.triggered.connect(self._notes_mode)
        self.action_flow_mode.triggered.connect(self._flow_mode)
        self.action_resize_column.triggered.connect(self._resize_column)
        self.action_auto_lock.triggered.connect(self._refresh)

        self.action_otp.triggered.connect(self._otp)
        self.action_hash_tools.triggered.connect(self._hash_tools)
        self.action_random_password.triggered.connect(self._random_password)
        self.action_generate_rsa_keystore.triggered.connect(self._generate_rsa_keystore)
        self.action_basic_type_conversion.triggered.connect(self._basic_type_conversion)

        self.action_about.triggered.connect(self._about)
        self.action_github.triggered.connect(self._open_github)
        self.action_check_for_updates.triggered.connect(self._check_for_updates)

        self.insert_selection_triggered.connect(self._insert_selection)
        keyboard.add_hotkey('Ctrl+Alt+Space', self.insert_selection_triggered.emit, suppress=True)
        self.toggle_flow_mode_triggered.connect(self._toggle_flow_mode)
        keyboard.add_hotkey('Ctrl+Alt+V', self.toggle_flow_mode_triggered.emit, suppress=True)

        self._table_view.refreshed.connect(self._refresh)
        self.setStatusTip(self.tr('就绪'))
        self._started = True

    @report_with_exception
    def init(self, app: QApplication):
        """初始化操作"""
        app.applicationStateChanged.connect(self._application_state_changed)
        app.installEventFilter(self)

        arguments = app.arguments()
        if len(arguments) > 1:
            self._open_file_(arguments[1])
        else:
            self._refresh_()

    @report_with_exception
    def eventFilter(self, o, e: QEvent) -> bool:
        if isinstance(e, QMouseEvent) or isinstance(e, QKeyEvent):
            self._reset_idle()
        return super().eventFilter(o, e)

    @report_with_exception
    def dropEvent(self, e: QDropEvent) -> None:
        mime_data = e.mimeData()
        urls = mime_data.urls() if mime_data else None
        if urls:
            self._table_view.open_file(urls[0].toLocalFile())
        super().dropEvent(e)

    @report_with_exception
    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        mime_data = e.mimeData()
        if mime_data and mime_data.urls():
            e.accept()
        else:
            e.ignore()
        super().dragEnterEvent(e)

    @report_with_exception
    def closeEvent(self, e: QCloseEvent) -> None:
        if not env.restarting and self._table_view.edited:
            result = QMessageBox.information(self, '退出', '有操作未保存。', QMessageBox.StandardButton.Save
                                             | QMessageBox.StandardButton.Discard
                                             | QMessageBox.StandardButton.Cancel)
            if result == QMessageBox.StandardButton.Save:
                self._table_view.save_file()
            elif result == QMessageBox.StandardButton.Cancel:
                e.ignore()
                return
            self._table_view.discard_change()
        super().closeEvent(e)
        quit_now()

    @report_with_exception
    def hideEvent(self, e: QHideEvent) -> None:
        self._auto_save_()
        if self.action_auto_lock.isChecked():
            self._try_lock_()
        super().hideEvent(e)

    @report_with_exception
    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key.Key_F12:
            self._quit_notes_mode()
        super().keyPressEvent(e)

    def setWindowFlag(self, a0, on=...):
        super().setWindowFlag(a0, on)
        self.action_stay_on_top.setChecked(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)

    @report_with_exception
    def _application_state_changed(self, state: Qt.ApplicationState):
        if state != Qt.ApplicationState.ApplicationActive:
            self._auto_save_()
            if self.action_auto_lock.isChecked():
                self._try_lock_()

    @report_with_exception
    def _idle_timeout(self):
        if self._idle_waiting:
            return
        self._idle_waiting = True

        try:
            self._auto_save_()
            if (cm.base.erase_triggered
                and self.action_auto_lock.isChecked()
                and self._table_view.locked is not False
                and DelayedOperationDialog.auto_confirm_with_delay(self, 10 * 1000, '应用将在10秒后重启')):
                if self._table_view.filepath:
                    new_instance(self._table_view.filepath, restart=True)
                else:
                    if self._table_view.edited:
                        bak = 'backup_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.pkl'
                        self._table_view.save_file(bak)
                        new_instance(bak, restart=True)
                    else:
                        # 兜底，一般走不到这个case
                        new_instance(restart=True)
                self._system_tray_icon.showMessage(self.tr('提示'), self.tr('因长时间未活动，应用已重启'))
                return
            if self.action_notes_mode.isChecked():
                self._quit_notes_mode()
            if self.action_auto_lock.isChecked():
                self._try_lock_(True)
        finally:
            self._idle_waiting = False
            self._reset_idle()

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
    def _merge_from_file(self, _):
        self._table_view.merge_from_file()

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
    def _search(self, _):
        self._search_dialog.show()
        pos = QCursor.pos()
        if not self.geometry().contains(pos):
            return
        line_edit = self._search_dialog.line_edit
        self._search_dialog.move(pos.x() - line_edit.width() // 2, pos.y() - line_edit.height() // 2)

    @report_with_exception
    def _stay_on_top(self, selected):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, selected)
        self.show()

    @report_with_exception
    def _notes_mode(self, selected):
        self._notes_mode_(selected)

    @report_with_exception
    def _flow_mode(self, selected):
        self._flow_mode_(selected)

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
    def _generate_rsa_keystore(self, _):
        bits, ok = QInputDialog.getInt(self, self.tr('输入RSA位数，必须是2的指数倍'), self.tr('RSA位数：'), 4096, 1024)
        if not ok:
            return
        # noinspection PyTypeChecker
        key = execute_in_progress(self, RSA.generate, bits)
        passphrase = InputPasswordDialog.getpass(self, self.tr('设置密码'), self.tr('用于保护私钥的加密密钥'), True)
        filepath, _ = QFileDialog.getSaveFileName(self, '选择私钥保存位置',
                                                  filter=self.tr('DER证书(*.der);;所有文件(*)'))
        if not filepath:
            return
        with open(filepath, 'wb') as f:
            f.write(key.export_key('DER', passphrase, 8))
        QMessageBox.information(self, self.tr('提示'), self.tr('私钥已保存至：{}').format(filepath))

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
    def _check_for_updates(self, _):
        self._check_for_updates_form.show()

    @report_with_exception
    def _refresh(self, _):
        self._refresh_()

    @report_with_exception
    def _insert_selection(self):
        self._reset_idle()
        if QApplication.modalWindow() is not None:
            return
        old_window_flags = self.windowFlags()
        if self._table_view.locked:
            self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)
            try:
                self._table_view.insert_selection()
            finally:
                self.setWindowFlags(old_window_flags)
                self.showMinimized()
        elif self._table_view.locked is False:
            self._table_view.insert_selection()
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.show()
            self._table_view.open_file()
            self.setWindowFlags(old_window_flags)
            self._toggle_flow_mode()

    @report_with_exception
    def _toggle_flow_mode(self):
        self._reset_idle()
        checked = not self.action_flow_mode.isChecked() or not self.isActiveWindow()
        self.action_flow_mode.setChecked(checked)
        self.action_flow_mode.triggered.emit(checked)

    def _auto_save_(self):
        self._table_view.auto_save()

    def _try_lock_(self, idle_wait=False):
        GLOBAL_SIGNAL.app_try_lock.emit()

        # 此处仅在未锁定时提示以减少打扰
        if (idle_wait and self._table_view.locked is False
            and DelayedOperationDialog.auto_confirm_with_delay(self, 10 * 1000, '应用将在10秒后锁定') is False):
            return

        if self._table_view.lock() and QApplication.applicationState() != Qt.ApplicationState.ApplicationActive:
            self._system_tray_icon.showMessage(self.tr('提示'), self.tr('已锁定'))

        self._refresh_()

    def _open_file_(self, filepath: str | None = None):
        self._table_view.open_file(filepath)

    def _notes_mode_(self, selected):
        self.action_auto_lock.setChecked(not selected)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, selected)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, selected)
        self.menubar.setVisible(not selected)
        self.statusbar.setVisible(not selected)
        self.show()

    def _quit_notes_mode(self):
        if not self.action_notes_mode.isChecked():
            return
        if self.action_flow_mode.isChecked():
            self.action_flow_mode.setChecked(False)
            self.action_flow_mode.triggered.emit(False)
            return
        self.action_notes_mode.setChecked(False)
        self.action_notes_mode.triggered.emit(False)

    def _flow_mode_(self, selected):
        if not selected:
            if hasattr(self, '_before_flow_size'):
                self.resize(self._before_flow_size)
                delattr(self, '_before_flow_size')
            if hasattr(self, '_before_flow_pos'):
                self.move(self._before_flow_pos)
                delattr(self, '_before_flow_pos')
        self.setWindowFlag(Qt.WindowType.Tool, selected)
        self.action_notes_mode.setChecked(True)
        self.action_notes_mode.triggered.emit(True)
        if selected:
            self._before_flow_size = self.size()
            self._before_flow_pos = self.pos()
            self.resize(QSize(self.menubar.width(), 64 + 32))
            cursor_pos = QCursor().pos()
            self.move(QPoint(cursor_pos.x() - self.size().width() // 2, cursor_pos.y() + 64 + 32))
        self._table_view.scrollTo(self._table_view.currentIndex())

    @property
    def _lock_title(self) -> str:
        if not self._table_view.has_file:
            return ''
        if self._table_view.locked:
            return self.tr('已锁定')
        if self.action_auto_lock.isChecked():
            return self.tr('自动锁定已开启')
        return ''

    def _reset_idle(self):
        self._idle_timer.start()

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

        self.action_merge.setEnabled(has_file)
        self.action_export.setEnabled(has_file)
        self.action_attribute.setEnabled(has_file)

        self.action_encrypt_file.setEnabled(has_file)

        self.action_decrypt_all.setEnabled(has_file)
        self.action_reload.setEnabled(has_file)

        self.action_search.setEnabled(has_file)

        self.action_resize_column.setEnabled(has_file)
