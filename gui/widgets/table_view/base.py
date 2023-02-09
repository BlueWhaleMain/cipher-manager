from PyQt5 import QtWidgets, QtGui, QtCore

from gui.common.env import report_with_exception


class BaseTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.context_menu = QtWidgets.QMenu(self)
        _translate = QtCore.QCoreApplication.translate
        self.action_view = QtWidgets.QAction(self)
        self.action_view.setText(_translate('BaseTableView', '查看'))
        self.context_menu.addAction(self.action_view)
        self.action_generate = QtWidgets.QAction(self)
        self.action_generate.setText(_translate('BaseTableView', '生成'))
        self.context_menu.addAction(self.action_generate)
        self.context_menu.addSeparator()
        self.action_remove = QtWidgets.QAction(self)
        self.action_remove.setText(_translate('BaseTableView', '删除'))
        self.context_menu.addAction(self.action_remove)
        self.customContextMenuRequested.connect(self.create_context_menu)

    @report_with_exception
    def create_context_menu(self, _):
        self.context_menu.popup(QtGui.QCursor.pos())
