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
import struct

from PyQt6 import QtGui

from common.enum import DescriptionStrEnum
from gui.widgets.item.value import ValueItem


class Endianness(DescriptionStrEnum):
    """字节序枚举"""
    NATIVE_ORDER4 = '@', '本机,凑够4字节'
    NATIVE_ORDER = '=', '本机'
    LITTLE = '<', '小端'
    BIG = '>', '大端'
    NETWORK = '!', '网络字节序'


class BasicTypes(DescriptionStrEnum):
    """基本类型枚举"""
    PAD_BYTE = 'x', 'pad byte'
    CHAR = 'c', 'char'
    SIGNED_CHAR = 'b', 'signed char'
    UNSIGNED_CHAR = 'B', 'unsigned char'
    BOOL = '?', 'bool'
    SHORT = 'h', 'short'
    UNSIGNEDSHORT = 'H', 'unsigned short'
    INT = 'i', 'int'
    UNSIGNEDINT = 'I', 'unsigned int'
    LONG = 'l', 'long'
    UNSIGNEDLONG = 'L', 'unsigned long'
    LONGLONG = 'q', 'long long'
    UNSIGNED_LONGLONG = 'Q', 'unsigned long long'
    FLOAT = 'f', 'float'
    DOUBLE = 'd', 'double'
    CHARARRAY = 's', 'char[]'
    CHAR_PTR = 'p', 'char[] ptr'
    VOID_PTR = 'P', 'void *'


class StructItemModel(QtGui.QStandardItemModel):
    """结构体单元模型"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._endian = Endianness.NATIVE_ORDER4

    @property
    def endian(self) -> Endianness:
        """字节序"""
        return self._endian

    @endian.setter
    def endian(self, val: Endianness):
        """设置字节序"""
        self._endian = val

    @property
    def struct(self) -> struct.Struct:
        """构建结构体"""
        # extended enum
        s = self._endian.value
        for i in range(self.rowCount()):
            r = self.item(i, 0)
            if isinstance(r, ValueItem):
                s += r.real
        # ignore
        # is str not tuple
        return struct.Struct(s)

    def append(self, t: BasicTypes):
        """追加结构体定义"""
        self.appendRow(ValueItem(t, t.description))
