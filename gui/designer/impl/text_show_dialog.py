from PyQt5 import QtWidgets

from gui.designer.text_show_dialog import Ui_text_show_dialog


class TextShowDialog(QtWidgets.QDialog, Ui_text_show_dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
