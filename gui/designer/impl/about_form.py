from PyQt5 import QtWidgets, QtCore

from gui.designer.about_form import Ui_about_form


class AboutForm(QtWidgets.QWidget, Ui_about_form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        try:
            with open('LICENSE', 'r') as f:
                self.license_group_box.setTitle(f.readline())
                self.license_plain_text_edit.setPlainText(f.read())
        except FileNotFoundError:
            raise SystemExit('No License')
        except Exception as e:
            raise SystemExit('No License', e)
