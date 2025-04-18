from PyQt6 import QtGui


class ReadOnlyItem(QtGui.QStandardItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(False)
