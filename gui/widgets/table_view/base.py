from PyQt5 import QtWidgets, QtGui, QtCore

from gui.common.env import report_with_exception


class BaseTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.context_menu = QtWidgets.QMenu(self)
        self.action_remove = QtWidgets.QAction('删除')
        self.context_menu.addAction(self.action_remove)
        self.customContextMenuRequested.connect(self.create_context_menu)

    @report_with_exception
    def create_context_menu(self, _):
        self.context_menu.popup(QtGui.QCursor.pos())
