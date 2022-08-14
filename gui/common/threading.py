import abc

from PyQt5 import QtCore, QtWidgets


class CallableThread(QtCore.QThread):
    """ 可调用的QT线程 """
    returned: QtCore.pyqtSignal = None
    excepted = QtCore.pyqtSignal(BaseException)

    @abc.abstractmethod
    def _run(self):
        pass

    def run(self) -> None:
        try:
            if self.returned:
                self.returned.emit(self._run())
            else:
                self._run()
        except BaseException as e:
            self.excepted.emit(e)

    def _inner_excepted(self, e: BaseException):
        QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, f'[{self.__class__.__name__}]未知异常',
                              f'{type(e).__name__}\r\n{e}').exec_()

    def excepted_enable(self):
        self.excepted.connect(self._inner_excepted)
