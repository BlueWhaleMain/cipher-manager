from PyQt5 import QtWidgets


class BaseTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
