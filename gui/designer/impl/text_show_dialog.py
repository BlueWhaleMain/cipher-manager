from PyQt6 import QtWidgets

from gui.common.env import report_with_exception
from cm.error import CmInterrupt
from gui.designer.text_show_dialog import Ui_text_show_dialog


class TextShowDialog(QtWidgets.QDialog, Ui_text_show_dialog):
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
