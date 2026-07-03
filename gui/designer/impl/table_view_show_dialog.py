#  MIT License
#
#  Copyright (c) 2026 BlueWhaleMain
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
from PyQt6.QtGui import QStandardItemModel

from cm.error import CmInterrupt
from gui.common.env import report_with_exception, GLOBAL_SIGNAL
from gui.designer.table_view_show_dialog import Ui_table_view_show_dialog


class TableViewShowDialog(QtWidgets.QDialog, Ui_table_view_show_dialog):
    """表格显示对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._accepted: bool = False

    @report_with_exception
    def accept(self) -> None:
        self._accepted = True
        self.close()
        super().accept()

    def show_item_model(self, title: str, item_model: QStandardItemModel | None,
                        editable: bool = False, protect_content: bool = True) -> QStandardItemModel | None:
        self.setWindowTitle(title)
        if item_model is None:
            if editable:
                self.table_view.setModel(QStandardItemModel())
        else:
            self.table_view.setModel(item_model)
        if editable:
            # noinspection PyTypeChecker
            self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Save
                                               | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.table_view.resizeColumnsToContents()

        if protect_content:
            GLOBAL_SIGNAL.app_try_lock.connect(self.reject)
        try:
            self.exec()
            if editable:
                if self._accepted:
                    return self.table_view.model()
                raise CmInterrupt
            return None
        finally:
            if protect_content:
                # 断开自动锁定信号，避免连接累积与对象被删后 emit 崩溃
                try:
                    GLOBAL_SIGNAL.app_try_lock.disconnect(self.reject)
                except (TypeError, RuntimeError):
                    pass
