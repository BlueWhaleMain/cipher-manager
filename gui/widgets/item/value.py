from typing import TypeVar, Generic

from PyQt6 import QtGui

_T = TypeVar('_T')


class ValueItem(QtGui.QStandardItem, Generic[_T]):
    def __init__(self, real: _T, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._real = real

    @property
    def real(self) -> _T:
        return self._real
