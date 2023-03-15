from PyQt5 import QtGui

from common.enum import DescriptionStrEnum


class EnumItem(QtGui.QStandardItem):
    def __init__(self, real: DescriptionStrEnum, *args, **kwargs):
        super().__init__(real.description, *args, **kwargs)
        self._real = real

    @property
    def real(self) -> DescriptionStrEnum:
        return self._real
