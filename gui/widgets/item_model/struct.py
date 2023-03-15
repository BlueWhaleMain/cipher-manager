import struct

from PyQt5 import QtGui

from common.enum import DescriptionStrEnum
from gui.widgets.item.enum import EnumItem


class Endianness(DescriptionStrEnum):
    """ 字节序 """
    NATIVE_ORDER4 = '@', '本机,凑够4字节'
    NATIVE_ORDER = '=', '本机'
    LITTLE = '<', '小端'
    BIG = '>', '大端'
    NETWORK = '!', '网络字节序'


class BasicTypes(DescriptionStrEnum):
    """ 基本类型 """
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._endian = Endianness.NATIVE_ORDER4

    @property
    def endian(self) -> Endianness:
        return self._endian

    @endian.setter
    def endian(self, val: Endianness):
        self._endian = val

    @property
    def struct(self) -> struct.Struct:
        s = self._endian.value
        for i in range(self.rowCount()):
            r = self.item(i, 0)
            if isinstance(r, EnumItem):
                s += r.real
        return struct.Struct(s)

    def append(self, t: BasicTypes):
        self.appendRow(EnumItem(t))
