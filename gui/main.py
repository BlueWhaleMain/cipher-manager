import sys

from PyQt6 import QtWidgets, QtCore


def main():
    app = QtWidgets.QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen()
    splash.showMessage('Loading...', QtCore.Qt.AlignmentFlag.AlignCenter, QtCore.Qt.GlobalColor.white)
    splash.show()
    from gui.common import env
    env.app = app
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
    translator = QtCore.QTranslator()
    locale_loaded = False
    try:
        if translator.load(f'qt_{QtCore.QLocale().system().name()}',
                           env.find_path(os.path.join('PyQt6', 'Qt6', 'translations'), os.path.isdir)):
            locale_loaded = True
    except FileNotFoundError as e:
        __logger.warning(e)
    if locale_loaded:
        app.installTranslator(translator)
    from gui.designer.impl.main_window import MainWindow
    window = MainWindow()
    env.window = window
    if not locale_loaded:
        # 已解决：PyInstaller打包问题，未能包含所有translations文件
        env.warning(f'本地化文件未能成功加载，详见日志。{os.linesep}日志目录：{log_path}。')
    window.show()
    window.init(app)
    splash.finish(window)
    splash.deleteLater()
    code = 0
    try:
        code = app.exec()
    finally:
        if code:
            __logger.info(f'App exit code {code}.')
            sys.exit(code)
