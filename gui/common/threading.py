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
import abc
import logging
from typing import TypeVar, Generic, ParamSpec, Callable

from PyQt6 import QtCore

_LOG = logging.getLogger(__name__)
_T = TypeVar('_T')


class CallableThread(QtCore.QThread, Generic[_T]):
    """
    可调用的QT线程

    Attributes:
        returned: 任务已返回
        excepted: 任务抛出异常
        done: 任务已结束
    """
    # pyqtSignal不支持泛型标志
    returned: QtCore.pyqtSignal = None
    excepted: QtCore.pyqtSignal = QtCore.pyqtSignal(BaseException)
    done = QtCore.pyqtSignal(object)

    @abc.abstractmethod
    def _run(self) -> _T:
        """执行内部逻辑"""

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
        """默认异常处理函数"""
        _LOG.error(e, exc_info=True)

    def enable_default_except(self) -> None:
        """启用默认异常处理器"""
        self.excepted.connect(self._inner_excepted)


_P = ParamSpec("_P")


class DefaultCallableThread(CallableThread[_T]):
    """默认可调用的Qt线程，执行指定的函数"""
    returned = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtCore.QObject, func: Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        super().__init__(parent)
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _run(self) -> _T:
        return self._func(*self._args, **self._kwargs)
