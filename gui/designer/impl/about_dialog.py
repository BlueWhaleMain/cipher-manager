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
    """关于对话框"""

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
