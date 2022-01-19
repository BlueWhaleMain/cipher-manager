import logging
import os
import sys

from PyQt5 import QtWidgets

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
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())
