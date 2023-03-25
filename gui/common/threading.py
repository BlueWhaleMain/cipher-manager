import abc
import os
import typing

from PyQt5 import QtCore, QtWidgets

_RT = typing.TypeVar('_RT')


class CallableThread(QtCore.QThread, typing.Generic[_RT]):
    """ 可调用的QT线程 """
    # pyqtSignal不支持泛型标志
    returned: QtCore.pyqtSignal = None
    excepted: QtCore.pyqtSignal = QtCore.pyqtSignal(BaseException)

    @abc.abstractmethod
    def _run(self) -> _RT:
        pass

    def run(self) -> None:
        try:
            if self.returned:
                self.returned.emit(self._run())
            else:
                self._run()
        except BaseException as e:
            self.excepted.emit(e)

    def _inner_excepted(self, e: BaseException) -> None:
        t_e_name = type(e).__name__
        es = str(e)
        QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, f'[{self.__class__.__name__}]未知异常',
                              f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。').exec_()

    def excepted_enable(self) -> None:
        self.excepted.connect(self._inner_excepted)
