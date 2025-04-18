import typing

from PyQt6 import QtWidgets, QtGui

from gui.designer.image_show_dialog import Ui_image_show_dialog


class ImageShowDialog(QtWidgets.QDialog, Ui_image_show_dialog):
    """ 图像显示对话框 """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

    def init(self) -> 'ImageShowDialog':
        """ 初始化 """
        self.button_box.clear()
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        return self

    def with_save_button(self, save_cb: typing.Callable[[bool], typing.Any]) -> 'ImageShowDialog':
        """
        添加保存按钮
        :param save_cb: 保存回调
        """
        self.button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(save_cb)
        return self

    def show_image(self, title: str, pixmap: QtGui.QPixmap) -> int:
        """
        显示图像
        :param title: 标题
        :param pixmap: 图像
        """
        self.setWindowTitle(title)
        self.image_label.setPixmap(pixmap)
        return self.exec()
