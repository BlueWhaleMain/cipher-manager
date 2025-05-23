# Form implementation generated from reading ui file 'check_for_updates_form.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_check_for_updates_form(object):
    def setupUi(self, check_for_updates_form):
        check_for_updates_form.setObjectName("check_for_updates_form")
        check_for_updates_form.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/window_icon/cm-gui.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        check_for_updates_form.setWindowIcon(icon)
        self.grid_layout = QtWidgets.QGridLayout(check_for_updates_form)
        self.grid_layout.setObjectName("grid_layout")
        self.pre_release_check_box = QtWidgets.QCheckBox(parent=check_for_updates_form)
        self.pre_release_check_box.setObjectName("pre_release_check_box")
        self.grid_layout.addWidget(self.pre_release_check_box, 2, 0, 1, 1)
        self.update_details_text_browser = QtWidgets.QTextBrowser(parent=check_for_updates_form)
        self.update_details_text_browser.setObjectName("update_details_text_browser")
        self.grid_layout.addWidget(self.update_details_text_browser, 0, 0, 1, 4)
        self.check_for_update_push_button = QtWidgets.QPushButton(parent=check_for_updates_form)
        self.check_for_update_push_button.setObjectName("check_for_update_push_button")
        self.grid_layout.addWidget(self.check_for_update_push_button, 2, 1, 1, 1)
        self.browser_download_push_button = QtWidgets.QPushButton(parent=check_for_updates_form)
        self.browser_download_push_button.setEnabled(False)
        self.browser_download_push_button.setObjectName("browser_download_push_button")
        self.grid_layout.addWidget(self.browser_download_push_button, 2, 3, 1, 1)
        self.open_url_push_button = QtWidgets.QPushButton(parent=check_for_updates_form)
        self.open_url_push_button.setObjectName("open_url_push_button")
        self.grid_layout.addWidget(self.open_url_push_button, 2, 2, 1, 1)

        self.retranslateUi(check_for_updates_form)
        QtCore.QMetaObject.connectSlotsByName(check_for_updates_form)

    def retranslateUi(self, check_for_updates_form):
        _translate = QtCore.QCoreApplication.translate
        check_for_updates_form.setWindowTitle(_translate("check_for_updates_form", "检查新版本"))
        self.pre_release_check_box.setText(_translate("check_for_updates_form", "检查预览版"))
        self.check_for_update_push_button.setText(_translate("check_for_updates_form", "检查更新"))
        self.browser_download_push_button.setText(_translate("check_for_updates_form", "在浏览器下载"))
        self.open_url_push_button.setText(_translate("check_for_updates_form", "前往更新页"))
