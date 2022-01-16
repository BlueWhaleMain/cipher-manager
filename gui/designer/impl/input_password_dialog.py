import typing

from PyQt5 import QtWidgets, QtCore

from gui.common.env import report_with_exception
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

    def getpass(self, text: str = '输入密码', title: str = None) -> str:
        if title:
            self.setWindowTitle(title)
        self.lineEdit.setPlaceholderText(text)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.exec_()
        if self._result is None:
            raise KeyboardInterrupt
        return self._result
