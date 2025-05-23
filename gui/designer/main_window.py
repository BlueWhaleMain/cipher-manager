# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 600)
        MainWindow.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/window_icon/cm-gui.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.central_widget = QtWidgets.QWidget(parent=MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.setObjectName("grid_layout")
        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 21))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(parent=self.menubar)
        self.menu_file.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.menu_file.setToolTip("")
        self.menu_file.setStatusTip("")
        self.menu_file.setObjectName("menu_file")
        self.menu_edit = QtWidgets.QMenu(parent=self.menubar)
        self.menu_edit.setObjectName("menu_edit")
        self.menu_search = QtWidgets.QMenu(parent=self.menubar)
        self.menu_search.setObjectName("menu_search")
        self.menu_tools = QtWidgets.QMenu(parent=self.menubar)
        self.menu_tools.setObjectName("menu_tools")
        self.menu_view = QtWidgets.QMenu(parent=self.menubar)
        self.menu_view.setObjectName("menu_view")
        self.menu_help = QtWidgets.QMenu(parent=self.menubar)
        self.menu_help.setObjectName("menu_help")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_new = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("document-new")
        self.action_new.setIcon(icon)
        self.action_new.setObjectName("action_new")
        self.action_open = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.action_open.setIcon(icon)
        self.action_open.setObjectName("action_open")
        self.action_attribute = QtGui.QAction(parent=MainWindow)
        self.action_attribute.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("document-properties")
        self.action_attribute.setIcon(icon)
        self.action_attribute.setObjectName("action_attribute")
        self.action_exit = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("application-exit")
        self.action_exit.setIcon(icon)
        self.action_exit.setObjectName("action_exit")
        self.action_export = QtGui.QAction(parent=MainWindow)
        self.action_export.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("x-office-spreadsheet")
        self.action_export.setIcon(icon)
        self.action_export.setObjectName("action_export")
        self.action_save = QtGui.QAction(parent=MainWindow)
        self.action_save.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("document-save")
        self.action_save.setIcon(icon)
        self.action_save.setObjectName("action_save")
        self.action_search = QtGui.QAction(parent=MainWindow)
        self.action_search.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("edit-find")
        self.action_search.setIcon(icon)
        self.action_search.setObjectName("action_search")
        self.action_hash_tools = QtGui.QAction(parent=MainWindow)
        self.action_hash_tools.setEnabled(False)
        self.action_hash_tools.setObjectName("action_hash_tools")
        self.action_import = QtGui.QAction(parent=MainWindow)
        self.action_import.setObjectName("action_import")
        self.action_random_password = QtGui.QAction(parent=MainWindow)
        self.action_random_password.setObjectName("action_random_password")
        self.action_stay_on_top = QtGui.QAction(parent=MainWindow)
        self.action_stay_on_top.setCheckable(True)
        self.action_stay_on_top.setObjectName("action_stay_on_top")
        self.action_notes_mode = QtGui.QAction(parent=MainWindow)
        self.action_notes_mode.setCheckable(True)
        self.action_notes_mode.setObjectName("action_notes_mode")
        self.action_auto_lock = QtGui.QAction(parent=MainWindow)
        self.action_auto_lock.setCheckable(True)
        self.action_auto_lock.setChecked(True)
        self.action_auto_lock.setObjectName("action_auto_lock")
        self.action_about = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("help-about")
        self.action_about.setIcon(icon)
        self.action_about.setObjectName("action_about")
        self.action_basic_type_conversion = QtGui.QAction(parent=MainWindow)
        self.action_basic_type_conversion.setObjectName("action_basic_type_conversion")
        self.action_ren = QtGui.QAction(parent=MainWindow)
        self.action_ren.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("folder-drag-accept")
        self.action_ren.setIcon(icon)
        self.action_ren.setObjectName("action_ren")
        self.action_save_new = QtGui.QAction(parent=MainWindow)
        self.action_save_new.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("document-save-as")
        self.action_save_new.setIcon(icon)
        self.action_save_new.setObjectName("action_save_new")
        self.action_otp = QtGui.QAction(parent=MainWindow)
        self.action_otp.setObjectName("action_otp")
        self.action_encrypt_file = QtGui.QAction(parent=MainWindow)
        self.action_encrypt_file.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("security-high")
        self.action_encrypt_file.setIcon(icon)
        self.action_encrypt_file.setObjectName("action_encrypt_file")
        self.action_decrypt_file = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("security-low")
        self.action_decrypt_file.setIcon(icon)
        self.action_decrypt_file.setObjectName("action_decrypt_file")
        self.action_reload = QtGui.QAction(parent=MainWindow)
        self.action_reload.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.action_reload.setIcon(icon)
        self.action_reload.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.action_reload.setObjectName("action_reload")
        self.action_decrypt_all = QtGui.QAction(parent=MainWindow)
        self.action_decrypt_all.setEnabled(False)
        self.action_decrypt_all.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.action_decrypt_all.setObjectName("action_decrypt_all")
        self.action_github = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("network-server")
        self.action_github.setIcon(icon)
        self.action_github.setObjectName("action_github")
        self.action_resize_column = QtGui.QAction(parent=MainWindow)
        self.action_resize_column.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.action_resize_column.setObjectName("action_resize_column")
        self.action_check_for_updates = QtGui.QAction(parent=MainWindow)
        self.action_check_for_updates.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.action_check_for_updates.setObjectName("action_check_for_updates")
        self.action_close = QtGui.QAction(parent=MainWindow)
        self.action_close.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.action_close.setObjectName("action_close")
        self.action_generate_rsa_keystore = QtGui.QAction(parent=MainWindow)
        self.action_generate_rsa_keystore.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.action_generate_rsa_keystore.setObjectName("action_generate_rsa_keystore")
        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_new)
        self.menu_file.addAction(self.action_ren)
        self.menu_file.addAction(self.action_close)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_import)
        self.menu_file.addAction(self.action_export)
        self.menu_file.addAction(self.action_attribute)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_encrypt_file)
        self.menu_file.addAction(self.action_decrypt_file)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.menu_edit.addAction(self.action_decrypt_all)
        self.menu_edit.addAction(self.action_reload)
        self.menu_search.addAction(self.action_search)
        self.menu_tools.addAction(self.action_otp)
        self.menu_tools.addAction(self.action_random_password)
        self.menu_tools.addAction(self.action_generate_rsa_keystore)
        self.menu_tools.addAction(self.action_basic_type_conversion)
        self.menu_view.addAction(self.action_stay_on_top)
        self.menu_view.addAction(self.action_notes_mode)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_resize_column)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_auto_lock)
        self.menu_help.addAction(self.action_about)
        self.menu_help.addAction(self.action_github)
        self.menu_help.addAction(self.action_check_for_updates)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_edit.menuAction())
        self.menubar.addAction(self.menu_search.menuAction())
        self.menubar.addAction(self.menu_view.menuAction())
        self.menubar.addAction(self.menu_tools.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.retranslateUi(MainWindow)
        self.action_exit.triggered.connect(MainWindow.close) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CipherManagerGUI"))
        self.menu_file.setTitle(_translate("MainWindow", "文件(&F)"))
        self.menu_edit.setTitle(_translate("MainWindow", "编辑(&E)"))
        self.menu_search.setTitle(_translate("MainWindow", "搜索(&S)"))
        self.menu_tools.setTitle(_translate("MainWindow", "工具(&O)"))
        self.menu_view.setTitle(_translate("MainWindow", "视图(&V)"))
        self.menu_help.setTitle(_translate("MainWindow", "?"))
        self.action_new.setText(_translate("MainWindow", "新建(&N)"))
        self.action_new.setStatusTip(_translate("MainWindow", "新建加密方式"))
        self.action_new.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.action_open.setText(_translate("MainWindow", "打开(&O)"))
        self.action_open.setStatusTip(_translate("MainWindow", "打开加密方式"))
        self.action_open.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.action_attribute.setText(_translate("MainWindow", "属性(&A)"))
        self.action_attribute.setStatusTip(_translate("MainWindow", "查看加密方式的属性"))
        self.action_exit.setText(_translate("MainWindow", "退出(&X)"))
        self.action_exit.setStatusTip(_translate("MainWindow", "退出应用"))
        self.action_export.setText(_translate("MainWindow", "导出(&E)"))
        self.action_export.setStatusTip(_translate("MainWindow", "导出加密方式中存储的记录"))
        self.action_save.setText(_translate("MainWindow", "保存(&S)"))
        self.action_save.setStatusTip(_translate("MainWindow", "保存加密方式"))
        self.action_save.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.action_search.setText(_translate("MainWindow", "查找(&F)"))
        self.action_search.setStatusTip(_translate("MainWindow", "解密并查找字符串"))
        self.action_search.setShortcut(_translate("MainWindow", "Ctrl+F"))
        self.action_hash_tools.setText(_translate("MainWindow", "哈希工具"))
        self.action_hash_tools.setStatusTip(_translate("MainWindow", "打开哈希工具"))
        self.action_import.setText(_translate("MainWindow", "导入(&I)"))
        self.action_import.setStatusTip(_translate("MainWindow", "从表格中导入记录"))
        self.action_random_password.setText(_translate("MainWindow", "随机密码生成"))
        self.action_random_password.setStatusTip(_translate("MainWindow", "打开随机密码生成器"))
        self.action_stay_on_top.setText(_translate("MainWindow", "总在最前"))
        self.action_stay_on_top.setStatusTip(_translate("MainWindow", "窗口总在最前"))
        self.action_notes_mode.setText(_translate("MainWindow", "便签模式"))
        self.action_notes_mode.setStatusTip(_translate("MainWindow", "窗口固定在最前，无边框"))
        self.action_notes_mode.setShortcut(_translate("MainWindow", "F12"))
        self.action_auto_lock.setText(_translate("MainWindow", "自动锁定"))
        self.action_auto_lock.setStatusTip(_translate("MainWindow", "失去焦点时自动锁定工作区"))
        self.action_about.setText(_translate("MainWindow", "关于 CipherMangerGUI"))
        self.action_about.setStatusTip(_translate("MainWindow", "关于 CipherMangerGUI"))
        self.action_about.setShortcut(_translate("MainWindow", "F1"))
        self.action_basic_type_conversion.setText(_translate("MainWindow", "基本类型转换"))
        self.action_basic_type_conversion.setStatusTip(_translate("MainWindow", "打开基本类型转换工具"))
        self.action_ren.setText(_translate("MainWindow", "重命名/移动"))
        self.action_ren.setStatusTip(_translate("MainWindow", "重命名/移动加密定义文件"))
        self.action_save_new.setText(_translate("MainWindow", "另存为"))
        self.action_save_new.setStatusTip(_translate("MainWindow", "加密定义文件另存为"))
        self.action_otp.setText(_translate("MainWindow", "OTP"))
        self.action_otp.setStatusTip(_translate("MainWindow", "打开OTP工具"))
        self.action_encrypt_file.setText(_translate("MainWindow", "加密文件"))
        self.action_encrypt_file.setStatusTip(_translate("MainWindow", "使用当前加密方式加密文件"))
        self.action_decrypt_file.setText(_translate("MainWindow", "解密文件"))
        self.action_decrypt_file.setStatusTip(_translate("MainWindow", "读取加密方式并解密文件"))
        self.action_reload.setText(_translate("MainWindow", "重新加载"))
        self.action_reload.setStatusTip(_translate("MainWindow", "重新加载文件中的内容"))
        self.action_reload.setShortcut(_translate("MainWindow", "Ctrl+Shift+H"))
        self.action_decrypt_all.setText(_translate("MainWindow", "解密全部"))
        self.action_decrypt_all.setStatusTip(_translate("MainWindow", "解密所有单元格"))
        self.action_decrypt_all.setShortcut(_translate("MainWindow", "Ctrl+Shift+V"))
        self.action_github.setText(_translate("MainWindow", "GitHub"))
        self.action_github.setStatusTip(_translate("MainWindow", "前往GitHub仓库首页"))
        self.action_resize_column.setText(_translate("MainWindow", "一键调整列宽"))
        self.action_resize_column.setStatusTip(_translate("MainWindow", "一键调整列宽至合适大小"))
        self.action_resize_column.setShortcut(_translate("MainWindow", "Ctrl+Shift+\\"))
        self.action_check_for_updates.setText(_translate("MainWindow", "检查新版本"))
        self.action_check_for_updates.setToolTip(_translate("MainWindow", "检查新版本"))
        self.action_check_for_updates.setStatusTip(_translate("MainWindow", "打开版本检查窗口"))
        self.action_close.setText(_translate("MainWindow", "关闭(&C)"))
        self.action_close.setToolTip(_translate("MainWindow", "关闭(C)"))
        self.action_close.setStatusTip(_translate("MainWindow", "关闭当前加密方式"))
        self.action_close.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.action_generate_rsa_keystore.setText(_translate("MainWindow", "生成RSA私钥"))
        self.action_generate_rsa_keystore.setToolTip(_translate("MainWindow", "生成RSA私钥"))
        self.action_generate_rsa_keystore.setStatusTip(_translate("MainWindow", "简单生成RSA私钥并导出"))
