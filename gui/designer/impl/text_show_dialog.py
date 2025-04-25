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
from PyQt6 import QtWidgets

from gui.common.env import report_with_exception
from cm.error import CmInterrupt
from gui.designer.text_show_dialog import Ui_text_show_dialog


class TextShowDialog(QtWidgets.QDialog, Ui_text_show_dialog):
    """文本显示对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._accepted: bool = False

    @report_with_exception
    def accept(self) -> None:
        self._accepted = True
        self.close()
        super().accept()

    def show_text(self, title: str, text: str | None, editable: bool = False) -> str | None:
        self.setWindowTitle(title)
        if text is None:
            if not editable:
                self.plain_text_edit.setPlaceholderText('<null>')
        else:
            self.plain_text_edit.setPlainText(text)
            if editable:
                self.plain_text_edit.setPlaceholderText(text)
        if editable:
            self.plain_text_edit.setReadOnly(False)
            self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Save
                                               | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.exec()
        if editable:
            if self._accepted:
                return self.plain_text_edit.toPlainText()
            raise CmInterrupt
