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
import os
from datetime import timedelta
from typing import TypeVar, Callable, ParamSpec, Generic, Iterable

from PyQt6 import QtWidgets, QtCore, sip
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QProgressDialog, QApplication, QMessageBox

from cm.error import CmInterrupt
from cm.progress import CmProgress
from gui.common.threading import DefaultCallableThread

_P = ParamSpec("_P")
_T = TypeVar('_T')


def _tr(text: str) -> str:
    return QCoreApplication.translate('progress', text)


class _Future(Generic[_T]):
    """不包含Python挂起的协程对象"""
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

# 进度条刷新率
_INTERVAL = 100

def execute_in_progress(self: QtWidgets.QWidget, fn: Callable[_P, _T], /, *args: _P.args,
                        cm_progress: CmProgress = None, **kwargs: _P.kwargs) -> _T:
    """创建线程执行耗时过程，阻塞，弹出进度对话框，支持进度管理器"""
    future = _Future()
    thread = DefaultCallableThread(self, fn, *args, **kwargs)
    thread.returned.connect(future.set_result)
    thread.excepted.connect(future.set_exception)
    progress = QtWidgets.QProgressDialog(self)
    if cm_progress is None:
        # 无限等待
        progress.canceled.connect(thread.quit)
        progress.setWindowTitle(_tr('请等待'))
        progress.setRange(0, 0)
    else:
        # 可跟踪进度
        progress.canceled.connect(cm_progress.cancel)
        progress.setWindowTitle(_tr('请稍等') if cm_progress.title is None else cm_progress.title)
        progress.setRange(0, 100)
        progress.setToolTip('0')
    t = QtCore.QTimer(self)
    t.setInterval(_INTERVAL)

    def progress_update():
        if future.done():
            t.stop()
            if sip.isdeleted(progress):
                return
            progress.accept()
        elif thread.isFinished():
            t.stop()
            if sip.isdeleted(progress):
                return
            progress.close()
        if not cm_progress:
            # 无进度更新
            return
        progress.setWindowTitle(_tr('请稍等') if cm_progress.title is None else cm_progress.title)
        skip = int(progress.toolTip())
        current = cm_progress.current
        total = cm_progress.total
        if current > skip and 0 < current < total:
            eta = str(timedelta(seconds=(total - current) / (current - skip) // 10))
        else:
            eta = '**:**:**'
        progress.setToolTip(str(current))
        progress.setValue(int(min(current / max(1, total) * 100, 99)) if total > 0 else 0)
        progress.setLabelText(f"({cm_progress.current_str} / {cm_progress.total_str}) {cm_progress.unit}"
                              f" - ETA: {eta}{os.linesep}{cm_progress.last_msg}")

    t.timeout.connect(progress_update)
    t.start()
    thread.start()
    progress.exec()
    if not thread.isFinished():
        while True:
            wait_progress = QProgressDialog(self)
            wait_progress.setWindowTitle(_tr('等待任务结束...'))
            wait_progress.setRange(0, 0)
            wait_progress.show()
            while not thread.isFinished():
                QApplication.processEvents()
                # 确保线程退出，否则可能导致应用无法正常结束
                thread.wait(_INTERVAL)
                if wait_progress.wasCanceled():
                    button = QMessageBox.warning(self, _tr('是否强制停止任务？'), _tr('该操作可能导致丢失正在处理的数据。'),
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                 QMessageBox.StandardButton.No)
                    if button == QMessageBox.StandardButton.Yes:
                        thread.terminate()
                    break
            else:
                break
        wait_progress.accept()
    if progress.wasCanceled():
        raise CmInterrupt
    return future.result()


def each_in_steps(progress: QProgressDialog, steps: Iterable[_T], total: int = 0) -> Iterable[_T]:
    """执行多个步骤并弹出进度条对话框，非阻塞，仅在遍历时执行"""
    progress.setRange(0, total)
    progress.setValue(0)
    progress.show()
    try:
        for step in steps:
            yield step
            value = progress.value()
            progress.setValue(value + 1)
            progress.setLabelText(f'{value} / {total}')
            QApplication.processEvents()
            if progress.wasCanceled():
                break
    except:
        progress.close()
        raise
    progress.accept()
