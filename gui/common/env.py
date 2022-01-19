import functools
import logging
import typing

from PyQt5 import QtWidgets

from gui.common.error import InterruptError

window: typing.Optional[QtWidgets.QMainWindow] = None
__logger = logging.getLogger(__name__)


def report_with_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
                break
            except InterruptError as e:
                if e.msg and e.exc:
                    QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, e.msg, str(e.exc)).exec_()
                elif e.exc:
                    QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, type(e.exc).__name__, str(e.exc))
                break
            except BaseException as e:
                __logger.error(e, exc_info=True)
                result = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Critical, '致命异常', f'{type(e).__name__}\r\n{e}',
                    QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Abort | QtWidgets.QMessageBox.Ignore,
                    window).exec_()
                if result == QtWidgets.QMessageBox.Retry:
                    continue
                if result == QtWidgets.QMessageBox.Abort:
                    raise
                if result == QtWidgets.QMessageBox.Ignore:
                    break

    return wrapper
