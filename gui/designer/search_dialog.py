# Form implementation generated from reading ui file 'search_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_search_dialog(object):
    def setupUi(self, search_dialog):
        search_dialog.setObjectName("search_dialog")
        search_dialog.resize(693, 42)
        self.grid_layout = QtWidgets.QGridLayout(search_dialog)
        self.grid_layout.setContentsMargins(-1, 2, -1, 8)
        self.grid_layout.setObjectName("grid_layout")
        self.next_push_button = QtWidgets.QPushButton(parent=search_dialog)
        self.next_push_button.setAutoFillBackground(False)
        self.next_push_button.setStyleSheet("QPushButton { background-color: transparent; }")
        icon = QtGui.QIcon.fromTheme("go-down")
        self.next_push_button.setIcon(icon)
        self.next_push_button.setDefault(True)
        self.next_push_button.setFlat(True)
        self.next_push_button.setObjectName("next_push_button")
        self.grid_layout.addWidget(self.next_push_button, 0, 1, 1, 1)
        self.exit_push_button = QtWidgets.QPushButton(parent=search_dialog)
        self.exit_push_button.setAutoFillBackground(False)
        self.exit_push_button.setStyleSheet("QPushButton { background-color: transparent; }")
        icon = QtGui.QIcon.fromTheme("application-exit")
        self.exit_push_button.setIcon(icon)
        self.exit_push_button.setFlat(True)
        self.exit_push_button.setObjectName("exit_push_button")
        self.grid_layout.addWidget(self.exit_push_button, 0, 4, 1, 1)
        self.line_edit = QtWidgets.QLineEdit(parent=search_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_edit.sizePolicy().hasHeightForWidth())
        self.line_edit.setSizePolicy(sizePolicy)
        self.line_edit.setMinimumSize(QtCore.QSize(0, 32))
        self.line_edit.setFrame(True)
        self.line_edit.setObjectName("line_edit")
        self.grid_layout.addWidget(self.line_edit, 0, 0, 1, 1)
        self.previous_push_button = QtWidgets.QPushButton(parent=search_dialog)
        self.previous_push_button.setAutoFillBackground(False)
        self.previous_push_button.setStyleSheet("QPushButton { background-color: transparent; }")
        icon = QtGui.QIcon.fromTheme("go-up")
        self.previous_push_button.setIcon(icon)
        self.previous_push_button.setFlat(True)
        self.previous_push_button.setObjectName("previous_push_button")
        self.grid_layout.addWidget(self.previous_push_button, 0, 2, 1, 1)

        self.retranslateUi(search_dialog)
        QtCore.QMetaObject.connectSlotsByName(search_dialog)

    def retranslateUi(self, search_dialog):
        _translate = QtCore.QCoreApplication.translate
        search_dialog.setWindowTitle(_translate("search_dialog", "查找"))
