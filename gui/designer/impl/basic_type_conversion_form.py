import base64
import os

from PyQt5 import QtWidgets, QtCore, QtGui

from gui.common import ENCODINGS
from gui.common.env import report_with_exception
from gui.designer.basic_type_conversion_form import Ui_basic_type_conversion_form
from gui.widgets.item_model.struct import StructItemModel, Endianness, BasicTypes


class BasicTypeConversionForm(QtWidgets.QDialog, Ui_basic_type_conversion_form):
    """ 基本类型转换窗体 """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._e2v = {}
        for v in Endianness.__members__:
            self.endianness_combo_box.addItem(Endianness[v].description, Endianness[v])
            self._e2v[Endianness[v].description] = Endianness[v]
        self._b2v = {}
        for v in BasicTypes.__members__:
            self.type_combo_box.addItem(BasicTypes[v].description, BasicTypes[v])
            self._b2v[BasicTypes[v].description] = BasicTypes[v]
        head = ('HEX', 'BASE64', 'ASCII', 'UTF-8')
        body = set(ENCODINGS)
        for h in head:
            body.remove(h)
        _translate = QtCore.QCoreApplication.translate
        self.to_string_method_combo_box.addItems(head + tuple(body))
        self.context_menu = QtWidgets.QMenu(self)
        self.action_up = QtWidgets.QAction(self)
        self.action_up.setText(_translate('BaseTableView', '上移'))
        self.context_menu.addAction(self.action_up)
        self.action_up.triggered.connect(self._up_type)
        self.action_down = QtWidgets.QAction(self)
        self.action_down.setText(_translate('BaseTableView', '下移'))
        self.context_menu.addAction(self.action_down)
        self.action_down.triggered.connect(self._down_type)
        self.context_menu.addSeparator()
        self.action_remove = QtWidgets.QAction(self)
        self.action_remove.setText(_translate('BaseTableView', '删除'))
        self.context_menu.addAction(self.action_remove)
        self.action_remove.triggered.connect(self._remove_type)
        self.action_clear = QtWidgets.QAction(self)
        self.action_clear.setText(_translate('BaseTableView', '清空'))
        self.context_menu.addAction(self.action_clear)
        self.action_clear.triggered.connect(self._clear_type)
        self._model: StructItemModel = StructItemModel()
        self.type_list_view.setModel(self._model)
        self.type_list_view.customContextMenuRequested.connect(self.create_context_menu)
        self.add_type_push_button.clicked.connect(self._add_type)
        self._model.dataChanged.connect(self._types_changed)
        self.endianness_combo_box.currentIndexChanged.connect(self._endian_changed)
        self.to_string_method_combo_box.currentIndexChanged.connect(self._to_string_method_changed)
        self.context_plain_text_edit.textChanged.connect(self._context_changed)
        self.read_push_button.clicked.connect(self._read)
        self.write_push_button.clicked.connect(self._write)
        self.auto_read_check_box.clicked.connect(self._auto_read_mode)
        self.auto_write_check_box.clicked.connect(self._auto_write_mode)
        self._item = tuple()

    @report_with_exception
    def create_context_menu(self, _):
        c = self._model.rowCount()
        if c < 1:
            return
        if self.type_list_view.selectionModel().selectedIndexes():
            self.action_remove.setEnabled(True)
            if c > 1:
                self.action_up.setEnabled(True)
                self.action_down.setEnabled(True)
            else:
                self.action_up.setEnabled(False)
                self.action_down.setEnabled(False)
        else:
            self.action_up.setEnabled(False)
            self.action_down.setEnabled(False)
            self.action_remove.setEnabled(False)
        self.context_menu.popup(QtGui.QCursor.pos())

    @report_with_exception
    def _add_type(self, _):
        for i in range(self.count_spin_box.value()):
            self._model.append(self._b2v[self.type_combo_box.currentData(0)])
        self._types_changed_()

    @report_with_exception
    def _up_type(self, _):
        index = self.type_list_view.currentIndex()
        self._move_type_(index.row(), index.row() - 1)
        self._types_changed_()

    @report_with_exception
    def _down_type(self, _):
        index = self.type_list_view.currentIndex()
        self._move_type_(index.row(), index.row() + 1)
        self._types_changed_()

    def _move_type_(self, current_row: int, target_row: int):
        if current_row == target_row:
            return
        if current_row < 0 or target_row > self._model.rowCount() - 1:
            return
        if current_row < target_row:
            if current_row == self._model.rowCount() - 1:
                return
        else:
            if current_row == 0:
                return
        row = self._model.takeRow(current_row)
        self._model.insertRow(target_row, row)
        self.type_list_view.setCurrentIndex(self._model.index(target_row, 0))

    @report_with_exception
    def _remove_type(self, _):
        indexes = self.type_list_view.selectionModel().selectedIndexes()
        indexes.reverse()
        for i in indexes:
            self._model.removeRow(i.row())
        self.type_list_view.selectionModel().clear()
        self._types_changed_()

    @report_with_exception
    def _clear_type(self, _):
        self._model.clear()
        self._types_changed_()

    @report_with_exception
    def _types_changed(self, *_):
        self._types_changed_()

    def _types_changed_(self):
        s = self._model.struct
        self.sizeof_val_label.setText(str(s.size))
        self._auto_rw()

    @report_with_exception
    def _endian_changed(self, *_):
        self._model.endian = self._e2v[self.endianness_combo_box.currentData(0)]
        self._auto_rw()

    @report_with_exception
    def _to_string_method_changed(self, *_):
        self._auto_rw()

    @report_with_exception
    def _context_changed(self, *_):
        if self.context_plain_text_edit.isReadOnly():
            return
        self._auto_rw()

    @report_with_exception
    def _read(self, *_):
        self._read_()

    @report_with_exception
    def _write(self, *_):
        self._write_()

    @report_with_exception
    def _auto_read_mode(self, checked: bool):
        if checked:
            self.auto_write_check_box.setChecked(False)
            self.context_plain_text_edit.setReadOnly(False)

    @report_with_exception
    def _auto_write_mode(self, checked: bool):
        if checked:
            self.auto_read_check_box.setChecked(False)
            self.context_plain_text_edit.setReadOnly(True)
        else:
            self.context_plain_text_edit.setReadOnly(False)

    def _auto_rw(self):
        if self.auto_read_check_box.isChecked():
            self._read_()
        elif self.auto_write_check_box.isChecked():
            self._write_()

    def _read_(self):
        decode_type = self.to_string_method_combo_box.currentData(0)
        text = self.context_plain_text_edit.toPlainText()
        if decode_type == 'HEX':
            try:
                b = bytes.fromhex(text)
            except Exception as e:
                t_e_name = 'hex读取失败'
                es = str(e)
                self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                return
        elif decode_type == 'BASE64':
            try:
                b = base64.standard_b64decode(text)
            except Exception as e:
                t_e_name = 'base64解码失败'
                es = str(e)
                self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                return
        elif decode_type in ENCODINGS:
            try:
                b = text.encode(decode_type)
            except Exception as e:
                t_e_name = decode_type + '编码失败'
                es = str(e)
                self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                return
        else:
            self.memory_plain_text_edit.setPlainText('不支持的操作。')
            return
        self.bytes_length_val_label.setText(str(len(b)))
        try:
            self._item = self._model.struct.unpack(b)
        except Exception as e:
            t_e_name = '解码失败'
            es = str(e)
            self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
            return
        self.memory_plain_text_edit.setPlainText(str(self._item))

    def _write_(self):
        encode_type = self.to_string_method_combo_box.currentData(0)
        try:
            b = self._model.struct.pack(*self._item)
        except Exception as e:
            t_e_name = '编码失败'
            es = str(e)
            self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
            return
        if encode_type == 'HEX':
            try:
                text = b.hex()
            except Exception as e:
                t_e_name = 'hex格式化失败'
                es = str(e)
                self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                return
        elif encode_type == 'BASE64':
            try:
                text = base64.standard_b64encode(b).decode()
            except Exception as e:
                t_e_name = 'base64编码失败'
                es = str(e)
                self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                return
        elif encode_type in ENCODINGS:
            try:
                text = b.decode(encode_type)
            except Exception as e:
                t_e_name = encode_type + '解码失败'
                es = str(e)
                self.memory_plain_text_edit.setPlainText(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                return
        else:
            self.memory_plain_text_edit.setPlainText('不支持的操作。')
            return
        self.memory_plain_text_edit.setPlainText(str(self._item))
        self.context_plain_text_edit.setPlainText(text)
        self.bytes_length_val_label.setText(str(len(b)))
