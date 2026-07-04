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

from PyQt6.QtCore import QTimer, QPropertyAnimation, Qt
from PyQt6.QtWidgets import QDialog, QWidget, QApplication

from gui.designer.delayed_operation_confirm_dialog import Ui_delayed_operation_confirm_dialog


class DelayedOperationDialog(QDialog, Ui_delayed_operation_confirm_dialog):
    """图像显示对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._ended = False
        self._emit_timer = QTimer()
        self.finished.connect(self._emit_timer.stop)
        self._emit_timer.timeout.connect(self.accept)
        self._timeout_animation = QPropertyAnimation(self.progress_bar, b'value')
        self.finished.connect(self._timeout_animation.stop)

    @classmethod
    def auto_confirm_with_delay(cls, parent: QWidget, delay: int, detail: str | None = None) -> bool:
        self = cls(parent)
        if detail is not None:
            self.label.setText(detail)

        self._emit_timer.start(delay)

        self._timeout_animation.stop()
        self._timeout_animation.setDuration(delay)
        self._timeout_animation.setStartValue(100)
        self._timeout_animation.setEndValue(0)
        self._timeout_animation.start()

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        QApplication.alert(parent)
        return bool(self.exec())
