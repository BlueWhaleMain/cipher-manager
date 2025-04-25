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
import typing

from PyQt6 import QtWidgets, QtGui

from gui.designer.image_show_dialog import Ui_image_show_dialog


class ImageShowDialog(QtWidgets.QDialog, Ui_image_show_dialog):
    """图像显示对话框"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

    def init(self) -> 'ImageShowDialog':
        """初始化"""
        self.button_box.clear()
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        return self

    def with_save_button(self, save_cb: typing.Callable[[bool], typing.Any]) -> 'ImageShowDialog':
        """
        添加保存按钮

        Args:
            save_cb: 保存回调

        Returns:
            自身
        """
        self.button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(save_cb)
        return self

    def show_image(self, title: str, pixmap: QtGui.QPixmap) -> int:
        """
        显示图像

        Args:
            title: 标题
            pixmap: 图像

        Returns:
            是否确认
        """
        self.setWindowTitle(title)
        self.image_label.setPixmap(pixmap)
        return self.exec()
