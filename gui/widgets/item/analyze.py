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
from PyQt6 import QtGui, QtCore

_translate = QtCore.QCoreApplication.translate


class AnalyzeItem(QtGui.QStandardItem):
    """值分析单元"""

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
