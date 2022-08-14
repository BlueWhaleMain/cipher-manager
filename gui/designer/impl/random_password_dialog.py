import os
import random
import re
import typing

import pydantic
from PyQt5 import QtWidgets, QtGui, QtCore

from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.common.threading import CallableThread
from gui.designer.random_password_dialog import Ui_RandomPasswordDialog


def verify(s, pts):
    for p in pts:
        if not re.fullmatch(p, s):
            return False
    return True


class SpawnConfigure(pydantic.BaseModel):
    """ 生成配置 """
    pwd_mini_len: int = pydantic.Field(title='最短密码长度')
    dictionary: dict[str, str] = pydantic.Field(title='字典')
    conditions: dict[str, str] = pydantic.Field(title='正则条件')


class SpawnThread(CallableThread):
    """ 生成密码线程 """
    returned = QtCore.pyqtSignal(str)

    def __init__(self, character_set: typing.Sequence[str], pwd_len: int, conditions: typing.Sequence[str] = None):
        super().__init__()
        self._character_set = character_set
        self._pwd_len = pwd_len
        if conditions:
            self._conditions = conditions
        else:
            self._conditions = []
        self._retry_max = 64

    def __del__(self):
        self.wait()

    def general(self) -> str:
        pwd = ''
        for i in range(self._pwd_len):
            pwd += random.choice(self._character_set)
        return pwd

    def _run(self) -> str:
        retry = 0
        result = self.general()
        while not verify(result, self._conditions):
            if retry < self._retry_max:
                result = self.general()
            else:
                return '生成失败，请检查是否存在不可能满足的条件'
            retry += 1
        return result


class RandomPasswordDialog(QtWidgets.QDialog, Ui_RandomPasswordDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._configure = SpawnConfigure(pwd_mini_len=self.length_spin_box.minimum(), dictionary={
            '默认': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+',
            '易于键盘输入': '23456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ~!@#$%^&*()+',
            '易于手写': '2349aderAEFGHJLNRT@#$%&*'
        }, conditions={'包含数字': r".*[0-9]+.*", '包含小写字母': r".*[a-z]+.*", '包含大写字母': r".*[A-Z]+.*",
                       '包含符号': r".*[~!@#$%^&*()_+]+.*"})
        self.apply_configure()
        self.import_condition_push_button.clicked.connect(self.import_file)
        self.spawn_push_button.clicked.connect(self.pbs_clicked)
        self._spawn_thread = None

    @report_with_exception
    def import_file(self, _):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', os.getcwd(), '所有文件(*);;JSON文件(*.json)')
        if filepath:
            try:
                self._configure = SpawnConfigure.parse_file(os.path.abspath(filepath))
            except ValueError as e:
                raise OperationInterruptError('文件格式异常', e)
            self.apply_configure()

    @report_with_exception
    def apply_configure(self):
        self.length_spin_box.setMinimum(self._configure.pwd_mini_len)
        self.length_spin_box.setValue(self._configure.pwd_mini_len)
        for name, value in self._configure.dictionary.items():
            self.character_set_combo_box.addItem(name, value)
        self.character_set_combo_box.setCurrentIndex(0)
        self.condition_list_widget.clear()
        for k, v in self._configure.conditions.items():
            checkbox = QtWidgets.QCheckBox(k)
            checkbox.setChecked(True)
            item = QtWidgets.QListWidgetItem()
            self.condition_list_widget.addItem(item)
            self.condition_list_widget.setItemWidget(item, checkbox)

    def get_conditions(self) -> list[str]:
        result = []
        for i in range(self.condition_list_widget.count()):
            item = self.condition_list_widget.item(i)
            checkbox = self.condition_list_widget.itemWidget(item)
            if isinstance(checkbox, QtWidgets.QCheckBox):
                if checkbox.isChecked():
                    result.append(self._configure.conditions[checkbox.text()])
        return result

    @report_with_exception
    def pbs_clicked(self, _):
        self.spawn()

    def show_spawn(self, result: str):
        self.result_plain_text_edit.setPlainText(result)
        self.condition_list_widget.setEnabled(True)

    def spawn(self):
        length = self.length_spin_box.value()
        if length > 0 and (self._spawn_thread is None or isinstance(self._spawn_thread,
                                                                    SpawnThread) and self._spawn_thread.isFinished()):
            self.condition_list_widget.setDisabled(True)
            self._spawn_thread = SpawnThread(self.character_set_combo_box.currentData(QtCore.Qt.ItemDataRole.UserRole),
                                             self.length_spin_box.value(), self.get_conditions())
            self._spawn_thread.excepted_enable()
            self._spawn_thread.start()
            self._spawn_thread.returned.connect(self.show_spawn)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if isinstance(self._spawn_thread, SpawnThread):
            self._spawn_thread.quit()
