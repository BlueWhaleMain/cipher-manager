import random
import re
import threading

from PyQt5 import QtWidgets, QtGui

from gui.common.env import report_with_exception
from gui.designer.random_password_dialog import Ui_RandomPasswordDialog
from gui.widgets.item.readonly import ReadOnlyItem


def verify(s, pts):
    for p in pts:
        if not re.fullmatch(p, s):
            return False
    return True


class RandomPasswordDialog(QtWidgets.QDialog, Ui_RandomPasswordDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = QtGui.QStandardItemModel()
        self.list_view_of_condition.setModel(self.model)
        self._conditions = [r".*[0-9]+.*", r".*[a-z]+.*", r".*[A-Z]+.*", r".*[~!@#$%^&*()_+]+.*"]
        self._dictionary = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+'
        self._retry_max = 64
        for con in self._conditions:
            self.model.appendRow(ReadOnlyItem(con))
        self.push_button_of_spawn.clicked.connect(self.pbs_clicked)
        self.push_button_of_add_condition.clicked.connect(self.pba_clicked)
        self._task = None

    @report_with_exception
    def pbs_clicked(self, _):
        self.spawn()

    @report_with_exception
    def pba_clicked(self, _):
        self.add_condition()

    def do_spawn(self):
        pwd = ''
        retry = 0
        while not verify(pwd, self._conditions):
            pwd = ''
            for i in range(self.spin_box_of_length.value()):
                pwd += random.choice(self._dictionary)
            if retry < self._retry_max:
                self.plain_text_edit_of_result.setPlainText(pwd)
            else:
                self.plain_text_edit_of_result.setPlainText('生成失败')
                break
            retry += 1
        self._task = None

    def spawn(self):
        length = self.spin_box_of_length.value()
        if length > 0 and self._task is None:
            self._task = threading.Timer(0, self.do_spawn)
            self._task.start()

    def add_condition(self):
        condition = self.line_edit_of_add_condition.text()
        if condition:
            self._conditions.append(condition)
            self.model.appendRow(ReadOnlyItem(condition))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self._task:
            self._task.cancel()
