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
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QStandardItemModel, QKeyEvent
from PyQt6.QtWidgets import QDialog, QPushButton, QWidgetAction, QLineEdit, QTableView, QMessageBox
from typing_extensions import Literal

from gui.common.env import report_with_exception
from gui.designer.search_dialog import Ui_search_dialog


class SearchDialog(QDialog, Ui_search_dialog):
    """搜索对话框"""

    def __init__(self, view: QTableView, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = view
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        self.exit_push_button.clicked.connect(self.close)
        self.clear_push_button = QPushButton(self.line_edit)
        icon = QIcon.fromTheme("edit-clear")
        self.clear_push_button.setIcon(icon)
        self.clear_push_button.setAutoFillBackground(True)
        self.clear_push_button.setStyleSheet("QPushButton { background-color: transparent; }")
        self.clear_push_button.setFlat(True)
        self.clear_action = QWidgetAction(self.line_edit)
        self.clear_action.setDefaultWidget(self.clear_push_button)
        self.line_edit.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)
        # noinspection PyUnresolvedReferences
        self.clear_action.triggered.connect(self.line_edit.clear)
        # noinspection PyUnresolvedReferences
        self.clear_push_button.clicked.connect(self.clear_action.trigger)
        self.next_push_button.clicked.connect(self._search_next)
        self.previous_push_button.clicked.connect(self._search_previous)
        self.line_edit.setFocus()

    @report_with_exception
    def _search_next(self, _):
        self._search('next')

    @report_with_exception
    def _search_previous(self, _):
        self._search('previous')

    @report_with_exception
    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key.Key_Up:
            self._search('previous')
        elif e.key() == Qt.Key.Key_Down:
            self._search('next')
        super().keyPressEvent(e)

    def _search(self, direction: Literal['next', 'previous']):
        text = self.line_edit.text()
        if not text:
            return
        # noinspection PyTypeChecker
        model: QStandardItemModel = self.view.model()
        index = self.view.currentIndex()
        first = True
        row_end = model.rowCount() if direction == 'next' else -1
        direction_step = 1 if direction == 'next' else -1
        column_start_at = index.column()
        column_start = 0 if direction == 'next' else model.columnCount()
        column_end = model.columnCount() if direction == 'next' else -1
        for row in range(index.row(), row_end, direction_step):
            for column in range(column_start if column_start_at is None else column_start_at, column_end,
                                direction_step):
                if first is True:
                    first = False
                    continue
                item = model.item(row, column)
                if not item:
                    continue
                if text in item.text():
                    self.view.setCurrentIndex(model.createIndex(row, column))
                    return
            column_start_at = None
        QMessageBox.information(self, self.tr('提示'), self.tr('未找到：{}。').format(text))
