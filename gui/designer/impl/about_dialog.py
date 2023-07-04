import typing

from PyQt5 import QtWidgets, QtCore, QtGui

from gui.common.env import report_with_exception
from gui.designer.about_dialog import Ui_about_dialog

try:
    with open('LICENSE', 'r') as __f:
        LICENSE_TITLE: typing.Final[str] = __f.readline()
        LICENSE_TEXT: typing.Final[str] = __f.read()
except FileNotFoundError:
    raise SystemExit('No License')
except Exception as __e:
    raise SystemExit('No License', __e)


class AboutDialog(QtWidgets.QDialog, Ui_about_dialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.Dialog)
        self.license_group_box.setTitle(LICENSE_TITLE)
        self.license_text_edit.setMarkdown(LICENSE_TEXT)

    @report_with_exception
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key_F1:
            self.close()
        super().keyPressEvent(e)
