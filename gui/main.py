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
import sys

from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtWidgets import QApplication, QSplashScreen


def main():
    """应用程序主入口"""
    app = QApplication(sys.argv)
    splash = QSplashScreen()
    splash.showMessage('Loading...', Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
    splash.show()
    QApplication.processEvents()
    from gui.common import env
    sys.excepthook = env.crash
    import logging
    __logger = logging.getLogger(__name__)
    from gui.common.logger_configurer import LoggerConfigurer
    import os
    log_path = os.path.join(env.PATH, 'log')
    logger_configurer = LoggerConfigurer(
        LoggerConfigurer.Config(level='DEBUG',
                                formatter_str='[%(asctime)s] [%(threadName)s %(funcName)s/%(levelname)s]: %(message)s',
                                path_pattern=log_path + os.sep + '%Y-%m-%d-{name}.log'))
    logger_configurer.enable_console_handler(color=True)
    logger_configurer.enable_file_handler('app')
    __logger.info(f'PID: {env.PID}, currentPath: {env.PATH}, workingDir: {os.getcwd()}, arguments: {sys.argv}.')
    splash.showMessage('Loading translation...', Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
    translator = QTranslator()
    locale_loaded = False
    try:
        if translator.load(f'qt_{QLocale().system().name()}',
                           env.find_path(os.path.join('PyQt6', 'Qt6', 'translations'), os.path.isdir)):
            locale_loaded = True
    except FileNotFoundError as e:
        __logger.warning(e)
    if locale_loaded:
        app.installTranslator(translator)
        splash.showMessage(app.tr('启动中...'), Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
    from gui.designer import icon_rc
    from gui.designer.impl.main_window import MainWindow
    window = MainWindow()
    if not locale_loaded:
        # 已解决：PyInstaller打包问题，未能包含所有translations文件
        env.warning(f'Load translation failed, see log file know more details.{os.linesep}Log directory: {log_path}.')
    window.show()
    window.init(app)
    splash.finish(window)
    splash.deleteLater()
    code = 0
    try:
        code = app.exec()
    finally:
        icon_rc.qCleanupResources()
        if code:
            __logger.info(f'App exit code {code}.')
            sys.exit(code)
