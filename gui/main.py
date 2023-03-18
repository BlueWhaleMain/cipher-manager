import logging
import os
import sys

from PyQt5 import QtWidgets

from gui.common import env
from gui.common.logger_configurer import LoggerConfigurer
from gui.designer.impl.main_window import MainWindow

__logger = logging.getLogger(__name__)


def main():
    # path_pattern='./log/{name}-%Y-%m-%d{sequence}'
    logger_configurer = LoggerConfigurer(
        LoggerConfigurer.Config(level='DEBUG',
                                formatter_str='[%(asctime)s] [%(threadName)s %(funcName)s/%(levelname)s]: %(message)s'))
    logger_configurer.enable_console_handler(color=True)
    __logger.debug(f'PID:{os.getpid()}')
    code = 0
    app = None
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow(app)
        env.window = window
        window.show()
        code = app.exec_()
    except (SystemExit, KeyboardInterrupt) as e:
        # 静默处理
        if e is env.main_ignore_exception:
            raise
        t_e_name = type(e).__name__
        es = str(e)
        __logger.info(f'{t_e_name}：{es}。' if es else f'{t_e_name}。')
        raise
    except BaseException as e:
        # 不记录已被记录过的异常
        if e is env.main_ignore_exception:
            raise
        elif app:
            t_e_name = type(e).__name__
            es = str(e)
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, '应用已崩溃',
                                  f'{t_e_name}：{os.linesep}{es}。' if es else f'{t_e_name}。').exec_()
        # 仅能记录app.exec_()执行之前的异常
        __logger.error(e, exc_info=True)
        raise
    finally:
        if code:
            __logger.info(f'App exit code {code}.')
            sys.exit(code)
