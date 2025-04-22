import sys

from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtWidgets import QApplication, QSplashScreen


def main():
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
