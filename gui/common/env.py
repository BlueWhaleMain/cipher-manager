import functools
import logging
import os
import typing

from PyQt5 import QtWidgets

from gui.common.error import OperationInterruptError

window: typing.Optional[QtWidgets.QMainWindow] = None
# 避免一个异常记录两次
main_ignore_exception: typing.Optional[BaseException] = None
__logger: logging.Logger = logging.getLogger(__name__)


def _message(icon: QtWidgets.QMessageBox.Icon, title: str, message: str, *args):
    return QtWidgets.QMessageBox(icon, title, message if len(message) < 100 else message[:100] + '...', *args,
                                 parent=window).exec_()


def report_with_exception(func: typing.Callable[..., typing.Optional[typing.Any]]) -> typing.Callable[..., None]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        global main_ignore_exception
        while True:
            try:
                func(*args, **kwargs)
                break
            except OperationInterruptError as e:
                if e.msg and e.exc:
                    _message(QtWidgets.QMessageBox.Icon.Warning, '警告', f'{e.msg}：{os.linesep}{e.exc}。')
                elif e.exc:
                    t_e_name = type(e.exc).__name__
                    es = str(e.exc)
                    _message(QtWidgets.QMessageBox.Icon.Critical, '错误',
                             f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。')
                elif e.msg:
                    _message(QtWidgets.QMessageBox.Icon.Information, '提示', e.msg + '。')
                # 没有信息的异常仅用于打断执行流程
                break
            except (SystemExit, KeyboardInterrupt) as e:
                t_e_name = type(e).__name__
                es = str(e)
                __logger.info(f'{t_e_name}：{es}。' if es else f'{t_e_name}。')
                main_ignore_exception = e
                # 静默处理
                raise
            except BaseException as e:
                __logger.error(e, exc_info=True)
                main_ignore_exception = e
                t_e_name = type(e).__name__
                es = str(e)
                result = _message(
                    QtWidgets.QMessageBox.Icon.Critical, '致命异常',
                    f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。',
                    QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Abort | QtWidgets.QMessageBox.Ignore)
                if result == QtWidgets.QMessageBox.Retry:
                    continue
                if result == QtWidgets.QMessageBox.Abort:
                    raise
                if result == QtWidgets.QMessageBox.Ignore:
                    break

    return wrapper
