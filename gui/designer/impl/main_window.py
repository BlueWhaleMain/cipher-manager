from PyQt5 import QtWidgets

from gui.common import env
from gui.designer.main_window import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        if env.window is None:
            env.window = self
        else:
            raise RuntimeError
        super().__init__()
        self.setupUi(self)
