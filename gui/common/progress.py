import os
from datetime import timedelta
from typing import TypeVar, Callable, ParamSpec, Generic

from PyQt6 import QtWidgets, QtCore, sip

from cm.error import CmInterrupt
from cm.progress import CmProgress
from gui.common.threading import DefaultCallableThread

_P = ParamSpec("_P")
_T = TypeVar('_T')


class _Future(Generic[_T]):
    _done: bool
    _result: _T | None
    _exception: BaseException | None

    def __init__(self, result: _T = None):
        self._done = False
        self._result = result
        self._exception = None

    def set_result(self, result: _T) -> None:
        self._done = True
        self._result = result

    def set_exception(self, exception: BaseException) -> None:
        self._done = True
        self._exception = exception

    def done(self) -> bool:
        return self._done

    def result(self) -> _T:
        if not self._done:
            raise CmInterrupt
        if self._exception:
            raise self._exception
        return self._result


def execute_in_progress(self: QtWidgets.QWidget, fn: Callable[_P, _T], /, *args: _P.args,
                        cm_progress: CmProgress = None, **kwargs: _P.kwargs) -> _T:
    future = _Future()
    thread = DefaultCallableThread(self, fn, *args, **kwargs)
    thread.returned.connect(future.set_result)
    thread.excepted.connect(future.set_exception)
    thread.start()
    progress = QtWidgets.QProgressDialog(self)
    # 无限等待
    if cm_progress is None:
        thread.done.connect(progress.accept)
        progress.setWindowTitle('请等待')
        progress.setRange(0, 0)
        progress.exec()
        if progress.wasCanceled():
            raise CmInterrupt
        return future.result()

    # 可跟踪进度
    progress.canceled.connect(cm_progress.cancel)
    progress.setWindowTitle('请稍等' if cm_progress.title is None else cm_progress.title)
    progress.setRange(0, 100)
    progress.setToolTip('0')
    t = QtCore.QTimer(self)
    t.setInterval(100)

    def progress_update():
        skip = int(progress.toolTip())
        current = cm_progress.current
        total = cm_progress.total
        if current > skip and current > 0 and total > 0:
            eta = str(timedelta(seconds=(total - current) / (current - skip) // 10))
        else:
            eta = '**:**:**'
        progress.setToolTip(str(current))
        if future.done():
            t.stop()
            if sip.isdeleted(progress):
                return
            progress.accept()
        else:
            progress.setValue(int(min(current / max(1, total) * 100, 99)) if total > 0 else 0)
            progress.setLabelText(f"({cm_progress.current_str} / {cm_progress.total_str}) {cm_progress.unit}"
                                  f" - ETA: {eta}{os.linesep}{cm_progress.last_msg}")

    t.timeout.connect(progress_update)
    t.start()
    progress.exec()
    if progress.wasCanceled():
        raise CmInterrupt
    return future.result()
