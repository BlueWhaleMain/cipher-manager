from PyQt5 import QtWidgets, QtCore, QtGui

from gui.common.env import report_with_exception
from gui.designer.about_form import Ui_about_form


class AboutForm(QtWidgets.QDialog, Ui_about_form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.Dialog)
        try:
            with open('LICENSE', 'r') as f:
                self.license_group_box.setTitle(f.readline())
                self.license_plain_text_edit.setPlainText(f.read())
        except FileNotFoundError:
            raise SystemExit('No License')
        except Exception as e:
            raise SystemExit('No License', e)

    @report_with_exception
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key_F1:
            self.close()
        super().keyPressEvent(e)
