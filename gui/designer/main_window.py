# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 600)
        MainWindow.setAcceptDrops(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 23))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setFocusPolicy(QtCore.Qt.NoFocus)
        self.menu_file.setToolTip("")
        self.menu_file.setStatusTip("")
        self.menu_file.setObjectName("menu_file")
        self.menu_edit = QtWidgets.QMenu(self.menubar)
        self.menu_edit.setObjectName("menu_edit")
        self.menu = QtWidgets.QMenu(self.menu_edit)
        self.menu.setObjectName("menu")
        self.menu_search = QtWidgets.QMenu(self.menubar)
        self.menu_search.setObjectName("menu_search")
        self.menu_tools = QtWidgets.QMenu(self.menubar)
        self.menu_tools.setObjectName("menu_tools")
        self.menu_view = QtWidgets.QMenu(self.menubar)
        self.menu_view.setObjectName("menu_view")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_new = QtWidgets.QAction(MainWindow)
        self.action_new.setObjectName("action_new")
        self.action_open = QtWidgets.QAction(MainWindow)
        self.action_open.setObjectName("action_open")
        self.action_attribute = QtWidgets.QAction(MainWindow)
        self.action_attribute.setObjectName("action_attribute")
        self.action_exit = QtWidgets.QAction(MainWindow)
        self.action_exit.setObjectName("action_exit")
        self.action_export = QtWidgets.QAction(MainWindow)
        self.action_export.setObjectName("action_export")
        self.action_save = QtWidgets.QAction(MainWindow)
        self.action_save.setObjectName("action_save")
        self.action_sort_asc = QtWidgets.QAction(MainWindow)
        self.action_sort_asc.setObjectName("action_sort_asc")
        self.action_sort_desc = QtWidgets.QAction(MainWindow)
        self.action_sort_desc.setObjectName("action_sort_desc")
        self.action_search = QtWidgets.QAction(MainWindow)
        self.action_search.setObjectName("action_search")
        self.action_hash_tools = QtWidgets.QAction(MainWindow)
        self.action_hash_tools.setObjectName("action_hash_tools")
        self.action_encrypt_test = QtWidgets.QAction(MainWindow)
        self.action_encrypt_test.setObjectName("action_encrypt_test")
        self.action_import = QtWidgets.QAction(MainWindow)
        self.action_import.setObjectName("action_import")
        self.action_random_password = QtWidgets.QAction(MainWindow)
        self.action_random_password.setObjectName("action_random_password")
        self.action_stay_on_top = QtWidgets.QAction(MainWindow)
        self.action_stay_on_top.setCheckable(True)
        self.action_stay_on_top.setObjectName("action_stay_on_top")
        self.action_notes_mode = QtWidgets.QAction(MainWindow)
        self.action_notes_mode.setCheckable(True)
        self.action_notes_mode.setObjectName("action_notes_mode")
        self.action_auto_lock = QtWidgets.QAction(MainWindow)
        self.action_auto_lock.setCheckable(True)
        self.action_auto_lock.setChecked(True)
        self.action_auto_lock.setObjectName("action_auto_lock")
        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_import)
        self.menu_file.addAction(self.action_export)
        self.menu_file.addAction(self.action_attribute)
        self.menu_file.addAction(self.action_exit)
        self.menu.addAction(self.action_sort_asc)
        self.menu.addAction(self.action_sort_desc)
        self.menu_edit.addAction(self.menu.menuAction())
        self.menu_search.addAction(self.action_search)
        self.menu_tools.addAction(self.action_hash_tools)
        self.menu_tools.addAction(self.action_encrypt_test)
        self.menu_tools.addAction(self.action_random_password)
        self.menu_view.addAction(self.action_stay_on_top)
        self.menu_view.addAction(self.action_notes_mode)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_auto_lock)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_edit.menuAction())
        self.menubar.addAction(self.menu_search.menuAction())
        self.menubar.addAction(self.menu_view.menuAction())
        self.menubar.addAction(self.menu_tools.menuAction())

        self.retranslateUi(MainWindow)
        self.action_exit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CipherManagerGUI"))
        self.menu_file.setTitle(_translate("MainWindow", "文件"))
        self.menu_edit.setTitle(_translate("MainWindow", "编辑"))
        self.menu.setTitle(_translate("MainWindow", "行操作"))
        self.menu_search.setTitle(_translate("MainWindow", "搜索"))
        self.menu_tools.setTitle(_translate("MainWindow", "工具"))
        self.menu_view.setTitle(_translate("MainWindow", "视图"))
        self.action_new.setText(_translate("MainWindow", "新建"))
        self.action_new.setStatusTip(_translate("MainWindow", "新建（N）"))
        self.action_new.setShortcut(_translate("MainWindow", "N"))
        self.action_open.setText(_translate("MainWindow", "打开"))
        self.action_open.setStatusTip(_translate("MainWindow", "打开（O）"))
        self.action_open.setShortcut(_translate("MainWindow", "O"))
        self.action_attribute.setText(_translate("MainWindow", "属性"))
        self.action_attribute.setStatusTip(_translate("MainWindow", "属性（A）"))
        self.action_attribute.setShortcut(_translate("MainWindow", "A"))
        self.action_exit.setText(_translate("MainWindow", "退出"))
        self.action_exit.setStatusTip(_translate("MainWindow", "退出（X）"))
        self.action_exit.setShortcut(_translate("MainWindow", "X"))
        self.action_export.setText(_translate("MainWindow", "导出"))
        self.action_export.setStatusTip(_translate("MainWindow", "导出（E）"))
        self.action_export.setShortcut(_translate("MainWindow", "E"))
        self.action_save.setText(_translate("MainWindow", "保存"))
        self.action_save.setStatusTip(_translate("MainWindow", "保存（Ctrl+S）"))
        self.action_save.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.action_sort_asc.setText(_translate("MainWindow", "升序排序"))
        self.action_sort_asc.setStatusTip(_translate("MainWindow", "升序排序"))
        self.action_sort_desc.setText(_translate("MainWindow", "降序排序"))
        self.action_sort_desc.setStatusTip(_translate("MainWindow", "降序排序"))
        self.action_search.setText(_translate("MainWindow", "查找"))
        self.action_search.setStatusTip(_translate("MainWindow", "查找（Ctrl+F）"))
        self.action_search.setShortcut(_translate("MainWindow", "Ctrl+F"))
        self.action_hash_tools.setText(_translate("MainWindow", "哈希工具"))
        self.action_hash_tools.setStatusTip(_translate("MainWindow", "哈希工具"))
        self.action_encrypt_test.setText(_translate("MainWindow", "PEM加密算法测试"))
        self.action_encrypt_test.setStatusTip(_translate("MainWindow", "加密算法测试"))
        self.action_import.setText(_translate("MainWindow", "导入"))
        self.action_import.setShortcut(_translate("MainWindow", "I"))
        self.action_random_password.setText(_translate("MainWindow", "随机密码生成"))
        self.action_random_password.setStatusTip(_translate("MainWindow", "随机密码生成"))
        self.action_stay_on_top.setText(_translate("MainWindow", "总在最前"))
        self.action_stay_on_top.setStatusTip(_translate("MainWindow", "总在最前"))
        self.action_notes_mode.setText(_translate("MainWindow", "便签模式"))
        self.action_notes_mode.setStatusTip(_translate("MainWindow", "总在最前，无边框"))
        self.action_notes_mode.setShortcut(_translate("MainWindow", "F12"))
        self.action_auto_lock.setText(_translate("MainWindow", "自动锁定"))
        self.action_auto_lock.setStatusTip(_translate("MainWindow", "自动锁定"))
