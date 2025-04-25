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
import functools
import logging
import os
import signal
import subprocess
import sys
from types import TracebackType
from typing import Any, Callable

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication, QMessageBox
from psutil import Process

import cm.base
from cm.error import CmBaseException

__LOG: logging.Logger = logging.getLogger(__name__)

# 应用程序当前PID
PID = os.getpid()
# 应用程序当前完整命令行
CMDLINE = Process(os.getpid()).cmdline()
# 当前应用程序启动命令（不包含参数与上下文）
SELF_CMD = sys.argv[0]
# 当前可执行文件路径
PATH = os.path.dirname(SELF_CMD)
# 当前应用程序启动命令（可被用于启动同一个实例）
_raw_cmds = []
for arg in CMDLINE:
    _raw_cmds.append(arg)
    if arg == SELF_CMD:
        break

# 禁用内存擦除，在Qt中极其不稳定
cm.base.erase_disabled = True


def find_path(path: str, validator=os.path.exists, external=tuple()) -> str:
    """寻找路径"""
    paths = [*sys.path, *external]
    for sys_path in paths:
        if validator(os.path.join(sys_path, path)):
            return os.path.join(sys_path, path)
    raise FileNotFoundError(path, paths)


def new_instance(filepath: str) -> None:
    """新建应用程序实例"""
    subprocess.Popen([*_raw_cmds, filepath])


# 避免一个异常记录两次
shown_exception: BaseException | None = None


def message(icon: QMessageBox.Icon, title: str = None, text: str = None,
            buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
            parent=None, *args, max_len: int = 255, **kwargs) -> int:
    """弹出消息框（消息长度未知）"""
    if parent is None:
        parent = QApplication.activeWindow()
    if QThread.currentThread() == QApplication.instance().thread():
        return QMessageBox(icon, title, text if len(text) < max_len else text[:max_len] + '...', buttons, parent, *args,
                           **kwargs).exec()
    # 此情况无法获取用户输入
    buttons = QMessageBox.StandardButton.NoButton
    QMessageBox(icon, title, text if len(text) < max_len else text[:max_len] + '...', buttons, parent, *args,
                **kwargs).show()
    return buttons


def info(msg: str, title: str = '提示', *args, **kwargs) -> int:
    return message(QMessageBox.Icon.Information, title, msg, *args, **kwargs)


def warning(msg: str, title: str = '警告', *args, **kwargs) -> int:
    return message(QMessageBox.Icon.Warning, title, msg, *args, **kwargs)


def error(msg: str, title: str = '错误', *args, **kwargs) -> int:
    return message(QMessageBox.Icon.Critical, title, msg, *args, **kwargs)


def critical(msg: str, title: str = '致命异常', buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Abort,
             *args, **kwargs) -> int:
    return message(QMessageBox.Icon.Critical, title, msg, buttons, *args, **kwargs)


def crash(e_t: type[BaseException], e: BaseException, traceback: TracebackType | None) -> Any:
    """崩溃应用"""
    global shown_exception
    if issubclass(e_t, CmBaseException):
        if e is shown_exception:
            return
        # 若应用内定义的异常未经处理被抛出到别的地方，需要引发崩溃
    elif e_t == KeyboardInterrupt:
        # 静默处理控制台退出异常
        es = str(e)
        if es:
            __LOG.info(f'{es}。')
        if sys.platform == "win32":
            sys.exit(0xC000013A)
        else:
            sys.exit(signal.SIGINT)
    elif e_t == SystemExit:
        # 应尽量避免非正常退出等致命退出情况
        __LOG.info(e, exc_info=traceback)
        return
    if not e is shown_exception:
        __LOG.critical(e, exc_info=traceback)
        t_e_name = type(e).__name__
        es = str(e)
        button = critical(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。',
                          buttons=QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Abort)
        if button == QMessageBox.StandardButton.Ignore:
            # 选择忽略仍可能闪退，这是无法避免的
            return
    # 一切未处理的异常均需要导致应用退出，正常退出之前可以执行保存数据等操作，原始崩溃是不友好的
    QApplication.closeAllWindows()
    QApplication.exit(1)


def report_with_exception(func: Callable[..., Any | None]) -> Callable[..., Any | None]:
    """包装函数使其向用户报告异常，避免信号槽函数崩溃，用法类似于@qt_safe"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        global shown_exception
        while True:
            try:
                return func(*args, **kwargs)
            except CmBaseException as e:
                es = str(e)
                t_e_name = type(e).__name__
                cs = str(e.__cause__) if e.__cause__ else None
                t_c_name = type(e.__cause__).__name__ if e.__cause__ else None
                # 此类异常用于打断执行流程，除非有信息否则不需要显示
                if isinstance(e, KeyboardInterrupt):
                    if cs:
                        __LOG.debug(f'{es}：{cs}。')
                        if es:
                            # 包含异常描述的一般为主动打断流程，警告用户
                            warning(f'{es}：{os.linesep}{cs}。', parent=args[0])
                        else:
                            # 由异常引发的流程打断，按错误处理
                            error(f'{cs}。', parent=args[0])
                    elif es:
                        __LOG.info(f'{es}。')
                        # 单纯打断流程，提示用户
                        info(f'{es}。', parent=args[0])
                    else:
                        # 建议用return替代无需提示用户的中断
                        __LOG.debug(e, exc_info=True)
                elif isinstance(e, NotImplementedError):
                    es = str(e)
                    if es:
                        # 这里可能是不支持的操作，需要警告用户
                        warning(f'{es}：{os.linesep}{cs}。', parent=args[0])
                    else:
                        # 功能没有实现时提供友好反馈，不应在稳定版中存在
                        __LOG.debug(e, exc_info=True)
                        info(f'功能尚未实现。', parent=args[0])
                else:
                    __LOG.error(e, exc_info=True)
                    # 已知的异常
                    if cs:
                        error(f'{t_c_name}：{os.linesep}{cs if cs else e}。', parent=args[0])
                    # 检查并主动抛出的异常
                    elif es:
                        warning(f'{es}。', parent=args[0])
                    # 无名异常，应尽量避免
                    else:
                        error(f'{t_e_name}：{os.linesep}{t_c_name if t_c_name else e}。', parent=args[0])
                shown_exception = e
                break
            except Exception as e:
                __LOG.error(e, exc_info=True)
                es = str(e)
                t_e_name = type(e).__name__
                # 可能可以重试本次操作来解决，也可能需要紧急崩溃
                # 对非专业用户不友好，应尽量避免
                result = critical(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。',
                                  '未知异常', QMessageBox.StandardButton.Retry
                                  | QMessageBox.StandardButton.Abort
                                  | QMessageBox.StandardButton.Ignore, parent=args[0])
                shown_exception = e
                if result == QMessageBox.StandardButton.Retry:
                    continue
                if result == QMessageBox.StandardButton.Abort:
                    raise
                if result == QMessageBox.StandardButton.Ignore:
                    break
                raise

    return wrapper
