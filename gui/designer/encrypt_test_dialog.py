# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'encrypt_test_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EncryptTestDialog(object):
    def setupUi(self, EncryptTestDialog):
        EncryptTestDialog.setObjectName("EncryptTestDialog")
        EncryptTestDialog.resize(620, 436)
        self.gridLayout = QtWidgets.QGridLayout(EncryptTestDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.mapping_table_view = QtWidgets.QTableView(EncryptTestDialog)
        self.mapping_table_view.setObjectName("mapping_table_view")
        self.gridLayout.addWidget(self.mapping_table_view, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(EncryptTestDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(EncryptTestDialog)
        self.buttonBox.accepted.connect(EncryptTestDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(EncryptTestDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(EncryptTestDialog)

    def retranslateUi(self, EncryptTestDialog):
        _translate = QtCore.QCoreApplication.translate
        EncryptTestDialog.setWindowTitle(_translate("EncryptTestDialog", "PEM加密算法测试"))
