import datetime
import hashlib
import json
import os
import shutil
import typing

import pydantic
import pyotp
import qrcode
from PyQt5 import QtWidgets, QtCore, QtGui

from gui.common.env import report_with_exception
from gui.common.error import OperationInterruptError
from gui.designer.impl.image_show_dialog import ImageShowDialog
from gui.designer.otp_dialog import Ui_otp_dialog

_OTP_QRCODE_TMP_FILENAME = 'otp_qrcode.tmp'
_first_algo = 'SHA1'
_algo = []
for x in hashlib.algorithms_available:
    if x.upper() == _first_algo:
        continue
    try:
        getattr(hashlib, x.lower())
        _algo.append(x)
    except AttributeError:
        pass

_algo.sort()
_algo.insert(0, _first_algo)


class OtpFile(pydantic.BaseModel):
    """ OTP文件 """
    s: str = pydantic.Field(title='密钥')
    digits: int = pydantic.Field(title='动态码长度')
    digest: str = pydantic.Field(title='算法')
    step: int = pydantic.Field(None, title='步数')
    time_slice: int = pydantic.Field(None, title='时间片长度')


class OtpDialog(QtWidgets.QDialog, Ui_otp_dialog):
    """ OTP动态码对话框 """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._hotp: typing.Optional[pyotp.HOTP] = None
        self._totp: typing.Optional[pyotp.TOTP] = None
        for name in _algo:
            self.hash_algorithm_combo_box.addItem(name.upper(), getattr(hashlib, name.lower()))
        self._image_show_dialog: ImageShowDialog = ImageShowDialog(self)
        self.time_remainder_progress_bar.setVisible(False)
        self._totp_timer: QtCore.QTimer = QtCore.QTimer(self)
        self.import_from_text_file_push_button.clicked.connect(self._import_from_text_file)
        self.export_push_button.clicked.connect(self._export)
        self.random_generate_push_button.clicked.connect(self._random_generate)
        self.lock_cipher_check_box.stateChanged.connect(self._lock_cipher_change)
        self.auto_grow_step_check_box.stateChanged.connect(self._auto_grow_step_change)
        self.generate_hotp_qrcode_push_button.clicked.connect(self._generate_hotp_qrcode)
        self.generate_hotp_code_push_button.clicked.connect(self._generate_hotp_code)
        self.verify_hotp_code_push_button.clicked.connect(self._verify_hotp_code)
        self._totp_timer.timeout.connect(self._totp_timer_timeout)
        self.date_time_edit_check_box.stateChanged.connect(self._date_time_edit_change)
        self.time_slice_spin_box.valueChanged.connect(self._time_slice_value_change)
        self.auto_generate_totp_code_check_box.stateChanged.connect(self._auto_generate_totp_code_change)
        self.generate_totp_qrcode_push_button.clicked.connect(self._generate_totp_qrcode)
        self.generate_totp_code_push_button.clicked.connect(self._generate_totp_code)
        self.verify_totp_code_push_button.clicked.connect(self._verify_totp_code)

    @report_with_exception
    def _import_from_text_file(self, _):
        try:
            if self.lock_cipher_check_box.isChecked():
                return
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', os.getcwd(),
                                                                '所有文件(*);;JSON文件(*.json)')
            if not filepath:
                return
            file = OtpFile.parse_file(filepath)
            self.cipher_plain_text_edit.setPlainText(file.s)
            self.otp_code_length_spin_box.setValue(file.digits)
            self.hash_algorithm_combo_box.setCurrentText(file.digest)
            if file.step:
                self.step_spin_box.blockSignals(True)
                self.step_spin_box.setValue(file.step)
                self.step_spin_box.blockSignals(False)
            if file.time_slice:
                self.time_slice_spin_box.blockSignals(True)
                self.time_slice_spin_box.setValue(file.time_slice)
                self.time_slice_spin_box.blockSignals(False)
        except Exception as e:
            raise OperationInterruptError('导入失败', e)

    @report_with_exception
    def _export(self, _):
        try:
            file = OtpFile(s=self.cipher_plain_text_edit.toPlainText(), digits=self.otp_code_length_spin_box.value(),
                           digest=self.hash_algorithm_combo_box.currentData(QtCore.Qt.UserRole),
                           step=self.step_spin_box.value(), time_slice=self.time_slice_spin_box.value())
            filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, '导出OTP文件', os.getcwd(),
                                                                'JSON文件(*.json);;所有文件(*)')
            if filepath:
                with open(filepath, 'w') as f:
                    json.dump(file.dict(), f, indent=2)
        except Exception as e:
            raise OperationInterruptError('导出失败', e)

    @report_with_exception
    def _random_generate(self, _):
        try:
            self.cipher_plain_text_edit.setPlainText(
                pyotp.random_base32(self.random_generate_bit_length_spin_box.value()))
        except Exception as e:
            raise OperationInterruptError('生成失败', e)

    @report_with_exception
    def _lock_cipher_change(self, checked: bool):
        # 基本界面
        self.cipher_plain_text_edit.setReadOnly(checked)
        self.import_from_text_file_push_button.setDisabled(checked)
        self.random_generate_push_button.setDisabled(checked)
        self.random_generate_bit_length_spin_box.setDisabled(checked)
        self.hash_algorithm_combo_box.setDisabled(checked)
        self.otp_code_length_spin_box.setDisabled(checked)
        # Tab页
        for c in self.hotp_tab.children():
            if isinstance(c, QtWidgets.QWidget):
                c.setEnabled(checked)
        for c in self.totp_tab.children():
            if isinstance(c, QtWidgets.QWidget):
                c.setEnabled(checked)
        # 实现
        if checked:
            s = self.cipher_plain_text_edit.toPlainText()
            digits = self.otp_code_length_spin_box.value()
            digest = self.hash_algorithm_combo_box.currentData(QtCore.Qt.UserRole)
            self._hotp = pyotp.HOTP(s, digits, digest)
            self.hotp_code_line_edit.setInputMask('9' * digits)
            self._totp = pyotp.TOTP(s, digits, digest)
            self.time_slice_spin_box.blockSignals(True)
            self.time_slice_spin_box.setValue(self._totp.interval)
            self.time_slice_spin_box.blockSignals(False)
            self.time_remainder_progress_bar.setMaximum(self._totp.interval)
            self.totp_code_line_edit.setInputMask('9' * digits)
            self._totp_timer.start(1000)
        else:
            self._totp_timer.stop()
            self._totp = None

    @report_with_exception
    def _auto_grow_step_change(self, checked: bool):
        self.step_spin_box.setReadOnly(checked)

    @report_with_exception
    def _generate_hotp_qrcode(self, _):
        if not isinstance(self._hotp, pyotp.HOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        self._generate_otp_qrcode(self._hotp.provisioning_uri(), 'HOTP')

    @report_with_exception
    def _generate_hotp_code(self, _):
        if not isinstance(self._hotp, pyotp.HOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        try:
            if self.auto_grow_step_check_box.isChecked():
                self.step_spin_box.setValue(self.step_spin_box.value() + 1)
            self.hotp_code_line_edit.setText(self._hotp.at(self.step_spin_box.value()))
        except Exception as e:
            self.lock_cipher_check_box.setChecked(False)
            raise OperationInterruptError('生成失败', e)

    @report_with_exception
    def _verify_hotp_code(self, _):
        if not isinstance(self._hotp, pyotp.HOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        try:
            if self._hotp.verify(self.hotp_code_line_edit.text(), self.step_spin_box.value()):
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, '成功', '校验通过', parent=self).exec_()
            else:
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '失败', '动态码错误', parent=self).exec_()
        except Exception as e:
            self.lock_cipher_check_box.setChecked(False)
            raise OperationInterruptError('校验失败', e)

    @report_with_exception
    def _totp_timer_timeout(self):
        if self.date_time_edit_check_box.isChecked():
            return
        self.date_time_edit.setDateTime(datetime.datetime.now())
        if self.auto_generate_totp_code_check_box.isChecked():
            timestamp = self.date_time_edit.dateTime().toTime_t()
            try:
                # 生成
                self.totp_code_line_edit.setText(self._totp.at(timestamp))
            except Exception as e:
                self.lock_cipher_check_box.setChecked(False)
                raise OperationInterruptError('生成失败', e)
            value = self._totp.interval - timestamp % self._totp.interval
            self.time_remainder_progress_bar.setValue(value)
            self.time_remainder_progress_bar.setStyleSheet(
                f"QProgressBar::chunk{{background:hsl({100 * value / self._totp.interval}, 100%, 40%)}}")

    @report_with_exception
    def _date_time_edit_change(self, checked: bool):
        self.date_time_edit.setReadOnly(not checked)

    @report_with_exception
    def _time_slice_value_change(self, value: int):
        if not isinstance(self._totp, pyotp.TOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        self._totp.interval = value
        self.time_remainder_progress_bar.setMaximum(value)

    @report_with_exception
    def _auto_generate_totp_code_change(self, checked: bool):
        self.totp_code_line_edit.setReadOnly(checked)
        self.time_remainder_progress_bar.setVisible(checked)

    @report_with_exception
    def _generate_totp_qrcode(self, _):
        if not isinstance(self._totp, pyotp.TOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        self._generate_otp_qrcode(self._totp.provisioning_uri(), 'TOTP')

    @report_with_exception
    def _generate_totp_code(self, _):
        if not isinstance(self._totp, pyotp.TOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        try:
            self.totp_code_line_edit.setText(self._totp.at(self.date_time_edit.dateTime().toTime_t()))
        except Exception as e:
            self.lock_cipher_check_box.setChecked(False)
            raise OperationInterruptError('生成失败', e)

    @report_with_exception
    def _verify_totp_code(self, _):
        if not isinstance(self._totp, pyotp.TOTP):
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '警告', '必须锁定密钥才能操作',
                                  parent=self).exec_()
            return
        try:
            if self._totp.verify(self.totp_code_line_edit.text()):
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, '成功', '校验通过', parent=self).exec_()
            else:
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, '失败', '动态码错误', parent=self).exec_()
        except Exception as e:
            self.lock_cipher_check_box.setChecked(False)
            raise OperationInterruptError('校验失败', e)

    def _generate_otp_qrcode(self, url: str, title: str):
        with open(_OTP_QRCODE_TMP_FILENAME, 'wb') as f:
            qrcode.make(url).save(f)

        @report_with_exception
        def _save(_):
            filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, '保存二维码', os.getcwd(),
                                                                'PNG文件(*.png);;所有文件(*)')
            if not filepath:
                return
            try:
                shutil.copy(_OTP_QRCODE_TMP_FILENAME, filepath)
            except Exception as e:
                raise OperationInterruptError('保存失败', e)

        self._image_show_dialog.init().with_save_button(_save).show_image(
            title, QtGui.QPixmap(_OTP_QRCODE_TMP_FILENAME))
        os.remove(_OTP_QRCODE_TMP_FILENAME)
