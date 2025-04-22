import functools
import typing
from typing import Callable

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit

from cm import CmValueError
from gui.common.env import report_with_exception
from gui.designer.input_password_dialog import Ui_InputPasswordDialog


class InputPasswordDialog(QtWidgets.QDialog, Ui_InputPasswordDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._result: typing.Optional[str] = None
        self.error_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.plain_text_edit.hide()
        self.error_label.hide()
        self.show_password_check_box.checkStateChanged.connect(self._show_password_change)
        self.multi_line_check_box.checkStateChanged.connect(self._multiline_change)

    @report_with_exception
    def showEvent(self, _) -> None:
        self.resize(int(self.minimumHeight() * 2 / 0.618), self.minimumHeight())

    @report_with_exception
    def accept(self) -> None:
        self._result = self.line_edit.text() if self.line_edit.isVisible() else self.plain_text_edit.toPlainText()
        # self.close()
        super().accept()

    @report_with_exception
    def _show_password_change(self, checked: Qt.CheckState):
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal
                                   if checked == Qt.CheckState.Checked else QLineEdit.EchoMode.Password)

    @report_with_exception
    def _multiline_change(self, checked: Qt.CheckState):
        if checked == Qt.CheckState.Checked:
            self.show_password_check_box.hide()
            self.line_edit.hide()
            self.plain_text_edit.show()
        else:
            self.plain_text_edit.hide()
            self.line_edit.show()
            self.show_password_check_box.show()
        self.resize(int(self.minimumHeight() * 2 / 0.618), self.minimumHeight())

    def _clear(self):
        self._result = None
        self.line_edit.clear()
        self.plain_text_edit.clear()

    def _try_execute_validator(self, validator: Callable[[str], bool]) -> Callable[[str], bool]:
        @functools.wraps(validator)
        def wrapper(*args, **kwargs) -> bool:
            result = False
            try:
                result = validator(*args, **kwargs)
                self.error_label.hide()
            except CmValueError as e:
                self.error_label.setText(str(e))
                self.error_label.show()
            finally:
                return result

        return wrapper

    def getpass(self, text: str = '输入密码', title: str = None, verify: bool = False,
                validator: Callable[[str], bool] = None) -> str | None:
        if title:
            self.setWindowTitle(title)
        self.line_edit.setPlaceholderText(text)
        self.plain_text_edit.setPlaceholderText(text)
        self.exec()
        if self._result is None:
            return None
        if verify:
            self.setWindowTitle('输入两次以确认')
        result = self._result
        while verify:
            self._clear()
            self.exec()
            if self._result is None:
                return None
            elif self._result == result:
                break
            else:
                result = self._result
        if validator:
            validator = self._try_execute_validator(validator)
            result = self._result
            if validator(result):
                return result
            else:
                self.setWindowTitle('验证失败，请再试一次')
                self._clear()
                self.exec()
            while not validator(self._result):
                if self._result is None:
                    return None
                if self._result == result:
                    button = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, '密码可能不正确', '忽略并继续？',
                                                   QtWidgets.QMessageBox.StandardButton.Ignore
                                                   | QtWidgets.QMessageBox.StandardButton.Retry).exec()
                    if button == QtWidgets.QMessageBox.StandardButton.Ignore:
                        return self._result
                result = self._result
                self._clear()
                self.exec()

        return self._result
