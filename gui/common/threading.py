import abc
import logging
from typing import TypeVar, Generic, ParamSpec, Callable

from PyQt6 import QtCore

_LOG = logging.getLogger(__name__)
_T = TypeVar('_T')


class CallableThread(QtCore.QThread, Generic[_T]):
    """ 可调用的QT线程 """
    # pyqtSignal不支持泛型标志
    returned: QtCore.pyqtSignal = None
    excepted: QtCore.pyqtSignal = QtCore.pyqtSignal(BaseException)
    done = QtCore.pyqtSignal(object)

    @abc.abstractmethod
    def _run(self) -> _T:
        pass

    def run(self) -> None:
        try:
            if self.returned:
                self.returned.emit(self._run())
            else:
                self._run()
        except BaseException as e:
            self.excepted.emit(e)
        finally:
            self.done.emit(None)

    @classmethod
    def _inner_excepted(cls, e: BaseException) -> None:
        _LOG.error(e, exc_info=True)

    def enable_default_except(self) -> None:
        self.excepted.connect(self._inner_excepted)


_P = ParamSpec("_P")


class DefaultCallableThread(CallableThread[_T]):
    returned = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtCore.QObject, func: Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        super().__init__(parent)
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _run(self) -> _T:
        return self._func(*self._args, **self._kwargs)
