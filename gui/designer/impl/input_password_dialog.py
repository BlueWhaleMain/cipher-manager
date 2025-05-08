#  MIT License
#
#  Copyright (c) 2022-2025 BlueWhaleMain
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
import base64
import functools
import typing
from typing import Callable, AnyStr

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QWidget, QMessageBox, QDialog

from cm import CmValueError
from cm.error import CmRuntimeError, CmInterrupt
from gui.common import ENCODINGS
from gui.common.env import report_with_exception
from gui.designer.input_password_dialog import Ui_InputPasswordDialog


class InputPasswordDialog(QDialog, Ui_InputPasswordDialog):
    """输入密码对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._result: typing.Optional[AnyStr] = None
        self.error_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.plain_text_edit.hide()
        self.error_label.hide()
        self.show_password_check_box.checkStateChanged.connect(self._show_password_change)
        self.multi_line_check_box.checkStateChanged.connect(self._multiline_change)
        head = ('str', 'HEX', 'BASE64')
        body = set(ENCODINGS)
        for h in head:
            if h in ENCODINGS:
                body.remove(h)
        self.password_encoding_combo_box.addItems(head + tuple(body))
        self.password_encoding_combo_box.setCurrentIndex(0)
        self.line_edit.setFocus()

    @report_with_exception
    def showEvent(self, _) -> None:
        self.resize(int(self.minimumHeight() * 2 / 0.618), self.minimumHeight())

    @report_with_exception
    def accept(self) -> None:
        text = self.line_edit.text() if self.line_edit.isVisible() else self.plain_text_edit.toPlainText()
        try:
            _encoding = self.password_encoding_combo_box.currentData(0)
            if _encoding == 'str':
                self._result = text
            elif _encoding == 'HEX':
                self._result = bytes.fromhex(text)
            elif _encoding == 'BASE64':
                self._result = base64.standard_b64decode(text)
            elif _encoding in ENCODINGS:
                self._result = text.encode(_encoding)
            else:
                raise CmValueError(_encoding)
        except Exception as e:
            raise CmRuntimeError(str(e)) from e
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
            self.plain_text_edit.setFocus()
        else:
            self.plain_text_edit.hide()
            self.line_edit.show()
            self.line_edit.setFocus()
            self.show_password_check_box.show()
        self.resize(int(self.minimumHeight() * 2 / 0.618), self.minimumHeight())

    def _clear(self):
        self._result = None
        self.line_edit.clear()
        self.plain_text_edit.clear()

    def _try_execute_validator(self, validator: Callable[[str], bool]) -> Callable[[str], bool]:
        # 此处异常无法正常被外部捕获
        @report_with_exception
        @functools.wraps(validator)
        def wrapper(*args, **kwargs) -> bool:
            try:
                self.error_label.clear()
                result = validator(*args, **kwargs)
                self.error_label.hide()
                return result
            except CmValueError as e:
                self.error_label.setText(str(e))
                self.error_label.show()
                return False
            except CmInterrupt as e:
                self.error_label.setText(self.tr('已取消 ') + str(e))
                self.error_label.show()
                return False
            except BaseException:
                self.error_label.setText(self.tr('未知异常'))
                self.error_label.show()
                raise

        return wrapper

    @classmethod
    def getpass(cls, parent: QWidget, title: str = 'Enter password', placeholder: str = 'password',
                verify: bool = False, validator: Callable[[AnyStr], bool] = None) -> AnyStr | None:
        """弹出对话框输入密码，支持二次确认与验证内容"""
        self = cls(parent)
        if title:
            self.setWindowTitle(title)
        self.line_edit.setPlaceholderText(placeholder)
        self.plain_text_edit.setPlaceholderText(placeholder)
        self.exec()
        if self._result is None:
            return None
        if verify:
            self.setWindowTitle(self.tr('输入两次以确认'))
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
                self.setWindowTitle(self.tr('验证失败，请再试一次'))
                self._clear()
                self.exec()
            while not validator(self._result):
                if self._result is None:
                    return None
                if self._result == result:
                    button = QMessageBox.question(self, self.tr('密码可能不正确'), self.tr('忽略并继续？'),
                                                  QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Retry,
                                                  QMessageBox.StandardButton.Retry)
                    if button == QMessageBox.StandardButton.Ignore:
                        return self._result
                result = self._result
                self._clear()
                self.exec()

        return self._result
