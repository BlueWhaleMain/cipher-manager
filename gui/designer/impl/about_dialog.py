import os.path
import typing

from PyQt6 import QtWidgets, QtCore, QtGui

import cm
import gui
from gui.common.env import report_with_exception, find_path
from gui.designer.about_dialog import Ui_about_dialog

try:
    with open(find_path('LICENSE', os.path.isfile), 'r') as __f:
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
        self.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.Dialog)
        self.license_group_box.setTitle(LICENSE_TITLE)
        self.license_text_edit.setMarkdown(LICENSE_TEXT)
        self.version_label.setText(gui.__version__)
        self.cm_version_label.setText(cm.__version__)

    @report_with_exception
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key.Key_F1:
            self.close()
        super().keyPressEvent(e)
