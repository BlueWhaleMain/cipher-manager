from PyQt6 import QtGui, QtCore

_translate = QtCore.QCoreApplication.translate


class AnalyzeItem(QtGui.QStandardItem):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if value is None:
            self.setToolTip(_translate('AnalyzeItemTooltip', '空'))
        elif isinstance(value, str):
            self.setToolTip(f'{len(value)} {_translate('AnalyzeItemTooltip', '字符')}')
        elif isinstance(value, bytes):
            value = value.hex()
            self.setToolTip(f'{len(value)} {_translate('AnalyzeItemTooltip', '字节')}')
        else:
            value = str(value)
        self.setText(value)
        self.setEditable(False)
