import typing

from PyQt5 import QtWidgets, QtCore

from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.designer.input_password_dialog import Ui_InputPasswordDialog


class InputPasswordDialog(QtWidgets.QDialog, Ui_InputPasswordDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._result: typing.Optional[str] = None

    @report_with_exception
    def accept(self) -> None:
        self._result = self.lineEdit.text()
        self.close()

    def getpass(self, text: str = '输入密码', title: str = None, verify: bool = False) -> str:
        if title:
            self.setWindowTitle(title)
        self.lineEdit.setPlaceholderText(text)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.exec_()
        if self._result is None:
            raise OperationInterruptError
        while verify:
            self.setWindowTitle('再次输入确认')
            result = self._result
            self._result = None
            self.lineEdit.clear()
            self.exec_()
            if self._result is None:
                raise OperationInterruptError
            elif self._result == result:
                return result
            else:
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, '请再输一遍', '两次输入不一致',
                                      QtWidgets.QMessageBox.Ok).exec_()
                self._result = result
        return self._result
