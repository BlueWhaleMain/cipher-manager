import functools
import logging
import os
import signal
import subprocess
import sys
from typing import Any, Callable

import psutil
from PyQt6 import QtWidgets

import cm.base
from cm.error import CmBaseException

__LOG: logging.Logger = logging.getLogger(__name__)

PID = os.getpid()
CMDLINE = psutil.Process(os.getpid()).cmdline()
SELF_CMD = sys.argv[0]
PATH = os.path.dirname(SELF_CMD)
_raw_cmds = []
for arg in CMDLINE:
    _raw_cmds.append(arg)
    if arg == SELF_CMD:
        break

# 禁用内存擦除，在Qt中极其不稳定
cm.base.erase_disabled = True


def find_path(path: str, validator=os.path.exists, external=tuple()) -> str:
    paths = [*sys.path, *external]
    for sys_path in paths:
        if validator(os.path.join(sys_path, path)):
            return os.path.join(sys_path, path)
    raise FileNotFoundError(path, paths)


def new_instance(filepath: str) -> None:
    subprocess.Popen([*_raw_cmds, filepath])


app: QtWidgets.QApplication | None = None
window: QtWidgets.QMainWindow | None = None
# 避免一个异常记录两次
shown_exception: BaseException | None = None


def message(icon: QtWidgets.QMessageBox.Icon, title: str = None, text: str = None,
            buttons: QtWidgets.QMessageBox.StandardButton = QtWidgets.QMessageBox.StandardButton.NoButton,
            parent=window, *args, max_len: int = 255, **kwargs):
    if parent is None:
        parent = window
    return QtWidgets.QMessageBox(icon, title, text if len(text) < max_len else text[:max_len] + '...', buttons, parent,
                                 *args, **kwargs).exec()


def info(msg: str, title: str = '提示', *args, **kwargs):
    return message(QtWidgets.QMessageBox.Icon.Information, title, msg, *args, **kwargs)


def warning(msg: str, title: str = '警告', *args, **kwargs):
    return message(QtWidgets.QMessageBox.Icon.Warning, title, msg, *args, **kwargs)


def error(msg: str, title: str = '错误', *args, **kwargs):
    return message(QtWidgets.QMessageBox.Icon.Critical, title, msg, *args, **kwargs)


def critical(msg: str, title: str = '致命异常',
             buttons: QtWidgets.QMessageBox.StandardButton = QtWidgets.QMessageBox.StandardButton.Abort, *args,
             **kwargs):
    return message(QtWidgets.QMessageBox.Icon.Critical, title, msg, buttons, *args, **kwargs)


_raw_crash = sys.excepthook


def crash(e_t: type[BaseException], e: BaseException, *_, **__) -> Any:
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
        __LOG.info(e, exc_info=True)
        _raw_crash(e_t, e, *_, **__)
        return
    # 一切未处理的异常均需要导致应用退出，正常退出之前可以执行保存数据等操作，原始崩溃是不友好的
    if not e is shown_exception:
        __LOG.critical(e, exc_info=True)
        t_e_name = type(e).__name__
        es = str(e)
        critical(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
    try:
        if window:
            window.close()
        if app:
            app.exit(1)
    finally:
        # 防止致命情况不产生任何记录，尽管Python解释器可能会处理该情况
        _raw_crash(e_t, e, *_, **__)


def report_with_exception(func: Callable[..., Any | None]) -> Callable[..., None]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        global shown_exception
        while True:
            try:
                func(*args, **kwargs)
                break
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
                            warning(f'{es}：{os.linesep}{cs}。')
                        else:
                            # 由异常引发的流程打断，按错误处理
                            error(f'{cs}。')
                    elif es:
                        __LOG.info(f'{es}。')
                        # 单纯打断流程，提示用户
                        info(f'{es}。')
                    else:
                        # 建议用return替代无需提示用户的中断
                        __LOG.debug(e, exc_info=True)
                elif isinstance(e, NotImplementedError):
                    es = str(e)
                    if es:
                        # 这里可能是不支持的操作，需要警告用户
                        warning(f'{es}：{os.linesep}{cs}。')
                    else:
                        # 功能没有实现时提供友好反馈，不应在稳定版中存在
                        __LOG.debug(e, exc_info=True)
                        info(f'功能尚未实现。')
                else:
                    __LOG.error(e, exc_info=True)
                    # 已知的异常
                    if cs:
                        error(f'{t_c_name}：{os.linesep}{cs if cs else e}。')
                    # 检查并主动抛出的异常
                    elif es:
                        warning(f'{es}。')
                    # 无名异常，应尽量避免
                    else:
                        error(f'{t_e_name}：{os.linesep}{t_c_name if t_c_name else e}。')
                shown_exception = e
                break
            except Exception as e:
                __LOG.error(e, exc_info=True)
                es = str(e)
                t_e_name = type(e).__name__
                # 可能可以重试本次操作来解决，也可能需要紧急崩溃
                # 对非专业用户不友好，应尽量避免
                result = critical(f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。',
                                  '未知异常', QtWidgets.QMessageBox.StandardButton.Retry
                                  | QtWidgets.QMessageBox.StandardButton.Abort
                                  | QtWidgets.QMessageBox.StandardButton.Ignore)
                shown_exception = e
                if result == QtWidgets.QMessageBox.StandardButton.Retry:
                    continue
                if result == QtWidgets.QMessageBox.StandardButton.Abort:
                    raise
                if result == QtWidgets.QMessageBox.StandardButton.Ignore:
                    break

    return wrapper
