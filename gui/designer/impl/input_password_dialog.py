import typing
from typing import Callable

from PyQt6 import QtWidgets

from gui.common.env import report_with_exception
from gui.designer.input_password_dialog import Ui_InputPasswordDialog


class InputPasswordDialog(QtWidgets.QDialog, Ui_InputPasswordDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._result: typing.Optional[str] = None

    @report_with_exception
    def accept(self) -> None:
        self._result = self.lineEdit.text()
        # self.close()
        super().accept()

    def getpass(self, text: str = '输入密码', title: str = None, verify: bool = False,
                validator: Callable[[str], bool] = None) -> str | None:
        if title:
            self.setWindowTitle(title)
        self.lineEdit.setPlaceholderText(text)
        self.exec()
        if self._result is None:
            return None
        if verify:
            self.setWindowTitle('输入两次以确认')
        while verify:
            result = self._result
            self._result = None
            self.lineEdit.clear()
            self.exec()
            if self._result is None:
                return None
            elif self._result == result:
                return result
            else:
                self._result = result
        if validator:
            result = self._result
            if not validator(self._result):
                self.setWindowTitle('验证失败，请再试一次')
                self._result = None
                self.lineEdit.clear()
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
                self._result = None
                self.lineEdit.clear()
                self.exec()

        return self._result
